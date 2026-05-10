import os
import time
from dotenv import load_dotenv
from supabase import create_client, Client
from src.os_controller import execute_command

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

class JarvisSupabaseClient:
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.user = None
        self.device_id = None

    def sign_up(self, email, password):
        try:
            res = self.supabase.auth.sign_up({"email": email, "password": password})
            # Na maioria das configurações default, se o e-mail não exigir confirmação (ou autoconfirmar), 
            # o res.user já estará populado. Caso exija confirmação, o login imediato pode falhar, 
            # mas vamos tentar assumir o usuário para a interface já fluir.
            if res.user:
                self.user = res.user
                print("Conta criada com sucesso:", self.user.id)
                return True, "Conta criada! Conectando..."
            else:
                return False, "Conta criada. Por favor, confirme seu e-mail."
        except Exception as e:
            return False, str(e)

    def login(self, email, password):
        try:
            res = self.supabase.auth.sign_in_with_password({"email": email, "password": password})
            self.user = res.user
            print("Login realizado com sucesso:", self.user.id)
            return True, "Acesso autorizado."
        except Exception as e:
            return False, str(e)

    def register_device(self, device_name="Meu PC"):
        if not self.user:
            return False, "Usuário não logado"
            
        # Verifica se já existe um dispositivo com esse nome para esse usuário
        res = self.supabase.table("devices").select("*").eq("user_id", self.user.id).eq("device_name", device_name).execute()
        
        if len(res.data) > 0:
            self.device_id = res.data[0]['id']
            print("Dispositivo encontrado:", self.device_id)
        else:
            # Cria novo dispositivo
            data = {
                "user_id": self.user.id,
                "device_name": device_name,
                "is_online": True
            }
            insert_res = self.supabase.table("devices").insert(data).execute()
            self.device_id = insert_res.data[0]['id']
            print("Novo dispositivo registrado:", self.device_id)
            
        return True, "Dispositivo registrado"

    def handle_realtime_event(self, payload):
        """Callback acionado sempre que um novo registro entra na tabela device_commands"""
        record = payload.get("record", {})
        
        # Verifica se o comando é para ESTE computador
        if record.get("target_device_id") == self.device_id and record.get("status") == "PENDING":
            print(">>> NOVO COMANDO RECEBIDO:", record)
            
            command_type = record.get("command_type")
            cmd_payload = record.get("payload", {})
            command_id = record.get("id")
            
            # Executa a ação no Windows
            success, msg = execute_command(command_type, cmd_payload)
            
            # Atualiza o status no banco de dados para que o site saiba que terminou
            new_status = "EXECUTED" if success else "FAILED"
            self.supabase.table("device_commands").update({"status": new_status}).eq("id", command_id).execute()
            print(f"Comando finalizado. Status: {new_status}")

    def start_listening(self):
        """Inicia uma thread em background para escutar novos comandos"""
        if not self.device_id:
            print("Registre o dispositivo antes de escutar")
            return
            
        print("Iniciando escuta de comandos em tempo real (Background Polling)...")
        
        import threading
        import time
        
        def poll_commands():
            while True:
                try:
                    # Busca comandos pendentes para este PC
                    res = self.supabase.table("device_commands").select("*").eq("target_device_id", self.device_id).eq("status", "PENDING").execute()
                    
                    for record in res.data:
                        print(">>> NOVO COMANDO RECEBIDO:", record)
                        
                        # Dispara a animação de "Pensando" na UI
                        if hasattr(self, 'on_process_start') and callable(self.on_process_start):
                            self.on_process_start()
                            
                        command_type = record.get("command_type")
                        cmd_payload = record.get("payload", {})
                        command_id = record.get("id")
                        
                        self.supabase.table("device_commands").update({"status": "PROCESSING"}).eq("id", command_id).execute()
                        
                        success, msg = execute_command(command_type, cmd_payload)
                        
                        new_status = "EXECUTED" if success else "FAILED"
                        self.supabase.table("device_commands").update({"status": new_status}).eq("id", command_id).execute()
                        print(f"Comando finalizado. Status: {new_status}")
                        
                        # Retorna a animação para "Ocioso"
                        if hasattr(self, 'on_process_end') and callable(self.on_process_end):
                            self.on_process_end()
                        
                except Exception as e:
                    pass # Ignora erros de rede temporários
                    
                time.sleep(2) # Checa a cada 2 segundos

        # Inicia a thread que vai rodar infinitamente em paralelo com a interface gráfica
        listener_thread = threading.Thread(target=poll_commands, daemon=True)
        listener_thread.start()
