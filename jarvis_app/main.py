import math
import customtkinter as ctk
import tkinter as tk
from src.settings_manager import SettingsManager
from src.audio_manager import AudioManager
from src.supabase_client import JarvisSupabaseClient
from src import os_controller
from google import genai
import os
import threading
from dotenv import load_dotenv
import re

load_dotenv()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Cores Base
C_BG = "#000000"           # Fundo Absoluto
C_PANEL = "#03060A"        # Fundo Painéis
C_CYAN = "#00F0FF"         # Ciano Brilhante
C_CYAN_DARK = "#004050"    # Ciano Escuro
C_TEXT_DIM = "#1E4B5B"     # Texto secundário
C_WHITE_GLOW = "#E0FFFF"   # Branco do núcleo

def mix_color(c1, c2, ratio):
    """Mistura duas cores hex (ratio 0.0 a 1.0)"""
    c1 = c1.lstrip('#')
    c2 = c2.lstrip('#')
    rgb1 = tuple(int(c1[i:i+2], 16) for i in (0, 2, 4))
    rgb2 = tuple(int(c2[i:i+2], 16) for i in (0, 2, 4))
    res = tuple(int(rgb1[i] * (1-ratio) + rgb2[i] * ratio) for i in range(3))
    return f"#{res[0]:02x}{res[1]:02x}{res[2]:02x}"

class JarvisApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("J.A.R.V.I.S. - Core System")
        self.geometry("1024x768")
        try: self.state('zoomed')
        except: pass 
        
        self.configure(fg_color=C_BG)
        self.settings = SettingsManager()
        self.supabase_client = JarvisSupabaseClient()
        self.supabase_client.on_process_start = self.on_process_start
        self.supabase_client.on_process_end = self.on_process_end

        self.font_title = ctk.CTkFont(family="Courier New", size=26, weight="bold")
        self.font_sub = ctk.CTkFont(family="Courier New", size=10)
        self.font_text = ctk.CTkFont(family="Courier New", size=12)
        
        self.is_login_mode = True

        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if gemini_api_key:
            self.genai_client = genai.Client(api_key=gemini_api_key)
        else:
            self.genai_client = None

        self.build_auth_screen()

    # ==========================================
    # TELA DE AUTENTICAÇÃO (LOGIN / SIGN UP)
    # ==========================================
    def build_auth_screen(self):
        if hasattr(self, 'auth_container'):
            self.auth_container.place(relx=0.5, rely=0.5, anchor="center")
            return

        self.auth_container = ctk.CTkFrame(self, fg_color="transparent")
        self.auth_container.place(relx=0.5, rely=0.5, anchor="center")

        # Canvas para desenhar os cantos (Brackets) do HUD
        self.hud_canvas = tk.Canvas(self.auth_container, width=400, height=550, bg=C_BG, highlightthickness=0)
        self.hud_canvas.pack()
        self.draw_hud_brackets(self.hud_canvas, 400, 550)

        # Frame do formulário em si
        self.auth_frame = ctk.CTkFrame(self.auth_container, fg_color=C_PANEL, border_width=1, border_color="#001824", corner_radius=10, width=340, height=490)
        self.auth_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Ícone do Cadeado (Desenhado no Canvas)
        self.lock_canvas = tk.Canvas(self.auth_frame, width=80, height=80, bg=C_PANEL, highlightthickness=0)
        self.lock_canvas.pack(pady=(30, 10))
        self.draw_lock_icon(self.lock_canvas)

        self.title_label = ctk.CTkLabel(self.auth_frame, text="J. A. R. V. I. S.", font=self.font_title, text_color=C_CYAN)
        self.title_label.pack(pady=(0, 2))
        
        self.subtitle_label = ctk.CTkLabel(self.auth_frame, text="SECURE ACCESS TERMINAL", font=self.font_sub, text_color=C_TEXT_DIM)
        self.subtitle_label.pack(pady=(0, 30))

        # Container dos Inputs
        form_frame = ctk.CTkFrame(self.auth_frame, fg_color="transparent")
        form_frame.pack(fill="x", padx=30)

        lbl_id = ctk.CTkLabel(form_frame, text="IDENTITY", font=self.font_sub, text_color=C_TEXT_DIM)
        lbl_id.pack(anchor="w")
        self.email_entry = ctk.CTkEntry(form_frame, placeholder_text="USERNAME", font=self.font_text, 
                                        fg_color="#000000", border_color="#002233", text_color=C_CYAN, height=35)
        self.email_entry.pack(fill="x", pady=(0, 15))

        lbl_pass = ctk.CTkLabel(form_frame, text="PASSCODE", font=self.font_sub, text_color=C_TEXT_DIM)
        lbl_pass.pack(anchor="w")
        
        pass_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        pass_frame.pack(fill="x", pady=(0, 25))
        
        self.password_entry = ctk.CTkEntry(pass_frame, placeholder_text="********", show="*", font=self.font_text,
                                           fg_color="#000000", border_color="#002233", text_color=C_CYAN, height=35)
        self.password_entry.pack(side="left", fill="x", expand=True)
        
        self.btn_show_pass = ctk.CTkButton(pass_frame, text="👁", width=35, height=35, fg_color="transparent", 
                                           border_width=1, border_color="#002233", text_color=C_CYAN, hover_color="#002233",
                                           command=self.toggle_password_visibility)
        self.btn_show_pass.pack(side="right", padx=(5, 0))

        self.action_button = ctk.CTkButton(form_frame, text="INITIATE SEQUENCE >", font=ctk.CTkFont(family="Courier New", weight="bold", size=12),
                                           fg_color="transparent", border_width=1, border_color=C_CYAN, text_color=C_CYAN, hover_color="#002233", height=40,
                                           command=self.process_auth)
        self.action_button.pack(fill="x")
        
        self.toggle_mode_btn = ctk.CTkButton(form_frame, text="CREATE NEW IDENTITY", font=self.font_sub,
                                             fg_color="transparent", text_color=C_TEXT_DIM, hover_color=C_PANEL,
                                             command=self.toggle_auth_mode)
        self.toggle_mode_btn.pack(pady=15)
        
        self.status_label = ctk.CTkLabel(self.auth_frame, text="", font=self.font_sub)
        self.status_label.pack(pady=0)
        
        # Auto-login check
        creds = self.settings.get_credentials()
        if creds and creds.get("email") and creds.get("password"):
            self.email_entry.insert(0, creds["email"])
            self.password_entry.insert(0, creds["password"])
            self.status_label.configure(text="AUTO LOGIN INIT...", text_color=C_CYAN)
            self.after(500, self.process_auth)

    def draw_hud_brackets(self, canvas, w, h):
        l = 20 # tamanho da linha
        c = C_CYAN
        canvas.create_line(0, 0, l, 0, fill=c, width=2)
        canvas.create_line(0, 0, 0, l, fill=c, width=2)
        
        canvas.create_line(w, 0, w-l, 0, fill=c, width=2)
        canvas.create_line(w, 0, w, l, fill=c, width=2)
        
        canvas.create_line(0, h, l, h, fill=c, width=2)
        canvas.create_line(0, h, 0, h-l, fill=c, width=2)
        
        canvas.create_line(w, h, w-l, h, fill=c, width=2)
        canvas.create_line(w, h, w, h-l, fill=c, width=2)

    def draw_lock_icon(self, canvas):
        cx, cy = 40, 40
        canvas.create_oval(cx-30, cy-30, cx+30, cy+30, outline=C_CYAN, width=2)
        # Cadeado
        canvas.create_rectangle(cx-10, cy-2, cx+10, cy+12, outline=C_CYAN, width=1.5)
        canvas.create_arc(cx-6, cy-15, cx+6, cy+5, start=0, extent=180, outline=C_CYAN, width=1.5, style=tk.ARC)
        canvas.create_line(cx, cy+4, cx, cy+8, fill=C_CYAN, width=1.5)

    def toggle_auth_mode(self):
        self.is_login_mode = not self.is_login_mode
        self.status_label.configure(text="")
        if self.is_login_mode:
            self.subtitle_label.configure(text="SECURE ACCESS TERMINAL")
            self.action_button.configure(text="INITIATE SEQUENCE >")
            self.toggle_mode_btn.configure(text="CREATE NEW IDENTITY")
        else:
            self.subtitle_label.configure(text="REGISTRATION PROTOCOL")
            self.action_button.configure(text="REGISTER SEQUENCE >")
            self.toggle_mode_btn.configure(text="BACK TO TERMINAL")

    def process_auth(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        
        if not email or not password:
            self.status_label.configure(text="DATA REQUIRED", text_color="#EF4444")
            return
            
        self.status_label.configure(text="AUTHENTICATING...", text_color=C_CYAN)
        self.update()
        
        if self.is_login_mode: success, msg = self.supabase_client.login(email, password)
        else: success, msg = self.supabase_client.sign_up(email, password)
        
        if success:
            self.settings.set_credentials(email, password)
            self.status_label.configure(text="SYNCHRONIZING...", text_color=C_CYAN)
            self.update()
            self.supabase_client.register_device("Terminal Alpha")
            self.supabase_client.start_listening()
            self.auth_container.place_forget()
            self.check_permissions()
        else:
            if "confirme seu e-mail" in msg.lower() or "verifique" in msg.lower():
                self.status_label.configure(text="EMAIL CONFIRMATION PENDING", text_color="#F59E0B")
            else:
                self.status_label.configure(text=f"ERROR: {msg}", text_color="#EF4444")

    # ==========================================
    # PERMISSÃO DE MICROFONE
    # ==========================================
    def check_permissions(self):
        if not self.settings.get_mic_permission():
            self.build_permission_screen()
        else:
            self.build_main_screen()

    def build_permission_screen(self):
        self.perm_frame = ctk.CTkFrame(self, fg_color=C_PANEL, border_width=1, border_color="#F59E0B", corner_radius=10)
        self.perm_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        icon_label = ctk.CTkLabel(self.perm_frame, text="🎤", font=ctk.CTkFont(size=40))
        icon_label.pack(pady=(30, 10))

        title = ctk.CTkLabel(self.perm_frame, text="HARDWARE AUTHORIZATION", font=self.font_title, text_color="#F59E0B")
        title.pack(pady=(0, 10), padx=40)

        desc = ctk.CTkLabel(self.perm_frame, text="J.A.R.V.I.S. requires audio input\nto receive local commands.", 
                            font=self.font_text, text_color="#D1D5DB", justify="center")
        desc.pack(pady=(0, 30))

        btn_frame = ctk.CTkFrame(self.perm_frame, fg_color="transparent")
        btn_frame.pack(pady=(0, 30))

        btn_allow = ctk.CTkButton(btn_frame, text="ALLOW", font=ctk.CTkFont(family="Courier New", weight="bold"),
                                  fg_color="#F59E0B", text_color="#000", hover_color="#D97706", command=self.grant_mic, width=120)
        btn_allow.pack(side="left", padx=10)

        btn_deny = ctk.CTkButton(btn_frame, text="DENY", font=ctk.CTkFont(family="Courier New", weight="bold"),
                                 fg_color="transparent", border_color="#EF4444", border_width=1, hover_color="#7F1D1D", command=self.deny_mic, width=120)
        btn_deny.pack(side="left", padx=10)

    def grant_mic(self):
        self.settings.set_mic_permission(True)
        self.perm_frame.place_forget()
        self.build_main_screen()

    def deny_mic(self):
        self.settings.set_mic_permission(False)
        self.perm_frame.place_forget()
        self.build_main_screen()

    # ==========================================
    # TELA PRINCIPAL (SISTEMA ONLINE)
    # ==========================================
    def build_main_screen(self):
        # 1. Background Grid Canvas
        self.bg_canvas = tk.Canvas(self, bg=C_BG, highlightthickness=0)
        self.bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        # Delay drawing grid to get proper window size
        self.after(200, self.draw_grid)

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True)

        # TOP BAR
        self.top_bar = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=60, corner_radius=0)
        self.top_bar.pack(fill="x", pady=10)

        # Header Esq
        header_left = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        header_left.pack(side="left", padx=30)
        
        lbl_jarvis = ctk.CTkLabel(header_left, text="JARVIS", font=ctk.CTkFont(family="Courier New", size=24, weight="bold"), text_color=C_CYAN)
        lbl_jarvis.pack(anchor="w")
        lbl_sys = ctk.CTkLabel(header_left, text="SISTEMA ONLINE", font=self.font_sub, text_color=C_TEXT_DIM)
        lbl_sys.pack(anchor="w", pady=(0,0))

        # Header Dir
        header_right = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        header_right.pack(side="right", padx=30)
        
        srv_badge = ctk.CTkLabel(header_right, text="[ SRV: ON ]", font=self.font_sub, text_color="#10B981")
        srv_badge.pack(side="left", padx=10)
        
        key_badge = ctk.CTkLabel(header_right, text="[ CHAVE: OK ]", font=self.font_sub, text_color="#10B981")
        key_badge.pack(side="left", padx=10)
        
        self.btn_logout = ctk.CTkButton(header_right, text="[ LOGOUT ]", font=self.font_sub, 
                                        fg_color="transparent", hover_color="#1A0000", text_color="#EF4444", 
                                        border_width=1, border_color="#7F1D1D", width=60, height=24, command=self.process_logout)
        self.btn_logout.pack(side="left", padx=10)

        # CONTAINER CENTRAL
        self.center_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.center_container.place(relx=0.5, rely=0.5, anchor="center")

        # CÉREBRO
        self.canvas_size = 400
        self.brain_canvas = tk.Canvas(self.center_container, width=self.canvas_size, height=self.canvas_size, 
                                      bg=C_BG, highlightthickness=0)
        self.brain_canvas.pack()

        # TEXTOS ABAIXO DO CÉREBRO
        self.status_main = ctk.CTkLabel(self.center_container, text="AGUARDANDO", font=ctk.CTkFont(family="Courier New", size=18), text_color="#A1A1AA")
        self.status_main.pack(pady=(10, 5))
        
        self.status_sub = ctk.CTkLabel(self.center_container, text="🎤 DIGA 'INICIALIZAR' PARA COMEÇAR", font=self.font_sub, text_color=C_TEXT_DIM)
        self.status_sub.pack()

        # BOTÃO INICIALIZAR
        self.btn_mic = ctk.CTkButton(self.center_container, text="🎤 INICIALIZAR", font=ctk.CTkFont(family="Courier New", size=14, weight="bold"),
                                     fg_color="transparent", border_width=1, border_color=C_CYAN_DARK, text_color=C_CYAN,
                                     corner_radius=20, height=45, hover_color="#002233", command=self.trigger_ai_input)
        self.btn_mic.pack(pady=30)
        
        self.response_label = ctk.CTkLabel(self.center_container, text="", font=self.font_text, text_color=C_CYAN, wraplength=450, justify="center")
        self.response_label.pack(pady=5)

        self.angle = 0
        self.pulse = 0
        self.brain_state = "idle" 
        
        # Inicializa e liga o ouvido do Jarvis (apenas se já não existir)
        if not hasattr(self, 'audio_manager'):
            self.audio_manager = AudioManager(
                on_wake_word_detected=self.on_wake_word_detected,
                on_command_received=self.on_voice_command_received,
                get_wake_words_func=self.settings.get_wake_words
            )
            self.audio_manager.start_background_listening()
        
        self.animate_brain()

    def draw_grid(self):
        w = self.winfo_width()
        h = self.winfo_height()
        self.bg_canvas.delete("grid")
        grid_color = "#080C14" # Linha quase invisível
        spacing = 50
        for x in range(0, w, spacing):
            self.bg_canvas.create_line(x, 0, x, h, fill=grid_color, tags="grid")
        for y in range(0, h, spacing):
            self.bg_canvas.create_line(0, y, w, y, fill=grid_color, tags="grid")

    def animate_brain(self):
        if not hasattr(self, 'brain_canvas'): return
        
        self.brain_canvas.delete("all")
        cx = self.canvas_size / 2
        cy = self.canvas_size / 2

        self.angle += 1 if self.brain_state == "idle" else 4
        self.pulse = (self.pulse + (2 if self.brain_state == "idle" else 10)) % 360

        # EFEITO DE GLOW (Desenhando círculos translúcidos via degradê)
        glow_radius_max = 140 + math.sin(math.radians(self.pulse)) * 10
        glow_steps = 15
        for i in range(glow_steps):
            r = glow_radius_max - (i * (glow_radius_max/glow_steps))
            # Vai do Preto pro Ciano
            ratio = (i / glow_steps) * (0.8 if self.brain_state == "processing" else 0.4)
            color = mix_color(C_BG, C_CYAN, ratio)
            self.brain_canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline="", fill=color)

        # ANEL ESCURO DE FUNDO DO NÚCLEO
        r_dark = 70
        self.brain_canvas.create_oval(cx - r_dark, cy - r_dark, cx + r_dark, cy + r_dark, outline="", fill="#000A12")

        # NÚCLEO SÓLIDO (Core)
        core_radius = 35 + (math.sin(math.radians(self.pulse)) * (3 if self.brain_state == "idle" else 8))
        self.brain_canvas.create_oval(cx - core_radius, cy - core_radius, cx + core_radius, cy + core_radius, 
                                      outline="", fill=C_WHITE_GLOW)

        # ANEL TRACEJADO
        r_dash = 85
        self.brain_canvas.create_oval(cx - r_dash, cy - r_dash, cx + r_dash, cy + r_dash, 
                                      outline=C_TEXT_DIM, width=2, dash=(6, 8))

        # ANEL CIANO EXTERNO (Giratório com gaps)
        r_out = 110
        arc_start = self.angle % 360
        ext = 160 # extent
        self.brain_canvas.create_arc(cx - r_out, cy - r_out, cx + r_out, cy + r_out, 
                                     start=arc_start, extent=ext, outline=C_CYAN, width=3, style=tk.ARC)
        self.brain_canvas.create_arc(cx - r_out, cy - r_out, cx + r_out, cy + r_out, 
                                     start=arc_start+180, extent=ext, outline=C_CYAN, width=3, style=tk.ARC)

        self.after(30, self.animate_brain)

    def on_process_start(self):
        self.brain_state = "processing"
        if hasattr(self, 'status_main'):
            self.status_main.configure(text="[ PROCESSANDO ]", text_color=C_CYAN)

    def on_process_end(self):
        self.brain_state = "idle"
        if hasattr(self, 'status_main'):
            self.status_main.configure(text="AGUARDANDO", text_color="#A1A1AA")

    def trigger_ai_input(self):
        if getattr(self, 'genai_client', None) is None:
            self.status_sub.configure(text="ERRO: CHAVE GEMINI NÃO CONFIGURADA.", text_color="#EF4444")
            return
            
        # Ativa o modo de escuta direta (Wake word ignorada por uma vez)
        self.audio_manager.is_awake = True
        self.brain_state = "processing"
        self.status_sub.configure(text="SISTEMA ATENTO: DIGA SEU COMANDO", text_color=C_CYAN)
        threading.Thread(target=self.audio_manager.speak, args=("Estou ouvindo, senhor.",), daemon=True).start()

    def on_wake_word_detected(self):
        self.brain_state = "processing"
        self.status_sub.configure(text="SISTEMA ATENTO: DIGA SEU COMANDO", text_color=C_CYAN)
        
        # Respostas aleatórias e amigáveis (como um amigo)
        import random
        respostas = [
            "Opa! O que manda?",
            "Tô ouvindo, fala aí.",
            "Diga lá, meu amigo.",
            "Em que posso ajudar?",
            "Sim, senhor?",
            "Pode falar."
        ]
        resposta = random.choice(respostas)
        threading.Thread(target=self.audio_manager.speak, args=(resposta,), daemon=True).start()

    def on_voice_command_received(self, command):
        self.on_process_start()
        self.status_sub.configure(text=f"VOCÊ: {command[:30]}...")
        self.response_label.configure(text="")
        threading.Thread(target=self.fetch_ai_response, args=(command,), daemon=True).start()

    def fetch_ai_response(self, prompt):
        try:
            # Pede para a IA responder rápido e agir como o Jarvis
            import datetime
            now = datetime.datetime.now()
            current_time_str = now.strftime("%H:%M")
            sys_prompt = ("Você é o assistente J.A.R.V.I.S do Homem de Ferro. Responda de forma curta, amigável e natural. "
                          f"O horário atual local do usuário é {current_time_str}. "
                          "Evite usar a palavra 'Senhor' toda vez. Trate o usuário como um amigo ou parceiro. Use gírias leves ou respostas diretas quando apropriado. "
                          "Você tem acesso à pesquisa do Google em tempo real. Se o usuário perguntar algo como cotações ou clima, responda FALANDO diretamente a resposta. "
                          "Apenas use a tag de comando [CMD:SEARCH:termo] se o usuário pedir explicitamente para MOSTRAR o resultado no navegador (ex: 'me mostre a cotação', 'pesquise na tela'). "
                          "Para outras ações, use as tags: [CMD:OPEN_APP:nome_do_app], [CMD:CLOSE_APP:nome_do_app] ou [CMD:GET_STORAGE]. "
                          "O usuário pergunta: ")
            
            response = self.genai_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=sys_prompt + prompt,
                config={"tools": [{"google_search": {}}]}
            )
            self.after(0, self.update_ai_response, response.text)
        except Exception as e:
            self.after(0, self.update_ai_response, f"[FALHA DE COMUNICAÇÃO]: {str(e)}")

    def update_ai_response(self, text):
        self.on_process_end()
        self.status_sub.configure(text="SISTEMA PRONTO", text_color=C_TEXT_DIM)
        
        # Procura por comandos embutidos
        cmd_match = re.search(r'\[CMD:(.*?)\]', text)
        clean_text = text
        if cmd_match:
            full_cmd = cmd_match.group(1)
            parts = full_cmd.split(':')
            cmd_type = parts[0]
            cmd_arg = parts[1] if len(parts) > 1 else ""
            clean_text = text.replace(cmd_match.group(0), "").strip()
            
            # Executa a ação no Windows
            if cmd_type == "OPEN_APP":
                os_controller.execute_command("OPEN_APP", {"app": cmd_arg})
            elif cmd_type == "CLOSE_APP":
                os_controller.execute_command("CLOSE_APP", {"app": cmd_arg})
            elif cmd_type == "SEARCH":
                os_controller.execute_command("SEARCH", {"query": cmd_arg})
            elif cmd_type == "OPEN_WEBSITE":
                os_controller.execute_command("OPEN_WEBSITE", {"url": cmd_arg})
            elif cmd_type == "GET_STORAGE":
                success, msg = os_controller.execute_command("GET_STORAGE", {})
                if success:
                    clean_text = msg + "\n" + clean_text

        # Limpa o markdown básico caso a IA use para ficar mais bonito na UI do app
        clean_text = clean_text.replace('**', '').replace('*', '').strip()
        self.response_label.configure(text=clean_text)
        
        # O Jarvis responde falando
        threading.Thread(target=self.audio_manager.speak, args=(clean_text,), daemon=True).start()

    def process_logout(self):
        self.settings.clear_credentials()
        self.main_frame.pack_forget()
        self.bg_canvas.place_forget()
        self.is_login_mode = True
        self.email_entry.delete(0, 'end')
        self.password_entry.delete(0, 'end')
        self.status_label.configure(text="")
        self.toggle_auth_mode() # Reset to login text
        self.toggle_auth_mode() # Back to normal login text
        self.build_auth_screen()

    def toggle_password_visibility(self):
        if self.password_entry.cget('show') == '*':
            self.password_entry.configure(show='')
            self.btn_show_pass.configure(text="👁‍🗨")
        else:
            self.password_entry.configure(show='*')
            self.btn_show_pass.configure(text="👁")

if __name__ == "__main__":
    app = JarvisApp()
    app.mainloop()
