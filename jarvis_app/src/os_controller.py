import os
import subprocess
import webbrowser
import shutil

def execute_command(command_type: str, payload: dict):
    """
    Interpreta os comandos e executa no Windows.
    """
    print(f"Executando comando local: {command_type} com dados: {payload}")
    
    try:
        if command_type == 'OPEN_APP':
            app_name = payload.get('app', '').lower()
            if 'spotify' in app_name:
                # Usa o protocolo do Spotify (funciona com apps da Windows Store e instaladores normais)
                webbrowser.open("spotify:")
                return True, "Abri o Spotify"
            elif 'bloco de notas' in app_name or 'notepad' in app_name:
                os.system("start notepad")
                return True, "Abri o Bloco de Notas"
            elif 'chrome' in app_name or 'navegador' in app_name:
                os.system("start chrome")
                return True, "Abri o Chrome"
            elif 'calculadora' in app_name or 'calc' in app_name:
                os.system("start calc")
                return True, "Abri a Calculadora"
            elif 'youtube' in app_name:
                webbrowser.open("https://youtube.com")
                return True, "Abri o YouTube"
            else:
                # Verifica se o executável existe no PATH antes de tentar o 'start'
                # Isso evita o popup de erro visual do Windows
                check_path = subprocess.run(f"where {app_name}", shell=True, capture_output=True, text=True)
                if check_path.returncode == 0:
                    os.system(f"start {app_name}")
                    return True, f"Abri {app_name}"
                else:
                    # Se não encontrar o app, fazemos uma pesquisa no Google como fallback
                    webbrowser.open(f"https://www.google.com/search?q={app_name}")
                    return True, f"Não encontrei o app '{app_name}' instalado, então pesquisei por ele no Google."
                
        elif command_type == 'SEARCH':
            query = payload.get('query', '')
            if query:
                webbrowser.open(f"https://www.google.com/search?q={query}")
                return True, f"Pesquisa feita por {query}"
            return False, "Query de pesquisa não informada"
            
        elif command_type == 'OPEN_WEBSITE':
            url = payload.get('url', '')
            if url:
                if not url.startswith('http'):
                    url = 'https://' + url
                webbrowser.open(url)
                return True, f"Site {url} aberto"
            return False, "URL não informada"
            
        elif command_type == 'GET_STORAGE':
            total, used, free = shutil.disk_usage("C:\\")
            free_gb = free / (1024**3)
            return True, f"Você tem {free_gb:.2f} GB livres no disco C."
            
        elif command_type == 'CLOSE_APP':
            app_name = payload.get('app', '').lower()
            if 'bloco de notas' in app_name: app_name = 'notepad'
            elif 'navegador' in app_name: app_name = 'chrome'
            
            # Tenta fechar o processo pelo nome
            result = subprocess.run(f"taskkill /F /IM {app_name}.exe", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return True, f"Fechei o aplicativo {app_name}."
            else:
                return False, f"Não consegui fechar o aplicativo {app_name}. Verifique se ele está aberto."
            
        else:
            return False, f"Tipo de comando {command_type} desconhecido"
            
    except Exception as e:
        return False, str(e)
