import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import speech_recognition as sr
import edge_tts
import asyncio
import threading
import time
import os
import ctypes
import uuid

class AudioManager:
    def __init__(self, on_wake_word_detected=None, on_command_received=None, get_wake_words_func=None):
        self.on_wake_word_detected = on_wake_word_detected
        self.on_command_received = on_command_received
        self.get_wake_words_func = get_wake_words_func
        
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 1.5  # Espera mais tempo antes de quebrar a frase
        self.is_listening = False
        self.is_awake = False
        self.listen_thread = None
        
        # Voz selecionada (Neural da Microsoft)
        self.voice = "pt-BR-AntonioNeural"
        self.last_interaction_time = time.time()

    def speak(self, text):
        """Fala um texto usando Edge-TTS e toca via Windows API (mciSendString)"""
        if not text.strip():
            return
            
        # Gera um nome de arquivo único para evitar conflitos de permissão
        filename = f"temp_{uuid.uuid4().hex}.mp3"
        file_path = os.path.abspath(filename)
            
        async def _save_audio():
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(file_path)
            
        try:
            # Gera o arquivo MP3 com voz neural
            asyncio.run(_save_audio())
            
            # Toca o arquivo MP3 usando a API nativa do Windows
            ctypes.windll.winmm.mciSendStringW(f'open "{file_path}" type mpegvideo alias mp3', None, 0, 0)
            ctypes.windll.winmm.mciSendStringW('play mp3 wait', None, 0, 0)
            ctypes.windll.winmm.mciSendStringW('close mp3', None, 0, 0)
            
            # Limpa o arquivo
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"[Áudio] Erro ao falar: {e}")

    def start_background_listening(self):
        if self.is_listening:
            return
        self.is_listening = True
        self.listen_thread = threading.Thread(target=self._listening_loop, daemon=True)
        self.listen_thread.start()

    def stop_background_listening(self):
        self.is_listening = False

    def _listening_loop(self):
        fs = 16000  # Sample rate otimizado para reconhecimento de voz
        threshold = 150  # Limiar de volume (energia) para considerar que há fala (Mais sensível)
        chunk_duration = 0.2  # Grava em blocos de 0.2 segundos (Evita diluir palavras curtas)
        buffer = []
        silence_count = 0

        while self.is_listening:
            try:
                # Verifica se passou do tempo de inatividade (10 segundos)
                if self.is_awake and (time.time() - self.last_interaction_time > 10):
                    self.is_awake = False
                    print("[Áudio] Voltando a dormir por inatividade.")
                
                # Grava um bloco de 1 segundo
                recording = sd.rec(int(chunk_duration * fs), samplerate=fs, channels=1, dtype='int16')
                sd.wait()
                
                # Calcula a energia (Volume)
                rms = np.sqrt(np.mean(np.square(recording.astype(np.float32))))
                
                if rms > threshold:
                    if not buffer:
                        print("[Áudio] Ouvindo...", end="", flush=True)
                    buffer.append(recording)
                    silence_count = 0
                    print(".", end="", flush=True) 
                else:
                    if buffer:
                        silence_count += 1
                        print("_", end="", flush=True) 
                        
                        # Se houver 3 segundos de silêncio (15 blocos de 0.2s) após a fala, processa
                        if silence_count >= 15:
                            print("\n[Áudio] Processando comando...")
                            full_recording = np.concatenate(buffer)
                            
                            # Salva e envia pro Google Speech
                            wav.write('temp_voice.wav', fs, full_recording)
                            with sr.AudioFile('temp_voice.wav') as source:
                                audio_data = self.recognizer.record(source)
                            
                            try:
                                text = self.recognizer.recognize_google(audio_data, language="pt-BR").lower()
                                print(f"[Áudio] Entendido: {text}")
                                self._process_text(text)
                            except sr.UnknownValueError:
                                pass # Não entendeu nada, ignora
                            except sr.RequestError:
                                print("[Áudio] Erro de conexão com o serviço de voz.")
                                
                            # Limpa buffer para a próxima fala
                            buffer = []
                            silence_count = 0
            except Exception as e:
                print(f"[Áudio] Erro no loop de escuta: {e}")
                time.sleep(1)

    def _process_text(self, text):
        wake_words = self.get_wake_words_func() if self.get_wake_words_func else ["jarvis"]
        
        # Se não está acordado, procura pela wake word
        if not self.is_awake:
            for w in wake_words:
                if w in text:
                    print(f"Wake word '{w}' detectada!")
                    
                    # Pega o que vem depois da wake word
                    idx = text.find(w) + len(w)
                    command = text[idx:].strip()
                    
                    # Se o usuário falou o comando junto (ex: "Jarvis, que horas são?")
                    if command and self.on_command_received:
                        self.last_interaction_time = time.time()
                        self.on_command_received(command)
                    else:
                        # Se ele só chamou o nome, acorda e responde "Sim, senhor?"
                        self.is_awake = True
                        self.last_interaction_time = time.time()
                        if self.on_wake_word_detected:
                            self.on_wake_word_detected()
                    return
        else:
            # Já estava acordado, então trata tudo como comando
            if len(text) > 2 and self.on_command_received:
                self.last_interaction_time = time.time()
                self.on_command_received(text)
