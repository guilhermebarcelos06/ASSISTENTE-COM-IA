🤖 J.A.R.V.I.S. Core System

Assistente Virtual Inteligente com Automação de Sistema e Controlo via Cloud

Funcionalidades •
Arquitetura •
Instalação •
Como Utilizar

📌 Visão Geral

O J.A.R.V.I.S. Core System é uma aplicação de desktop para Windows desenvolvida em Python. Inspirado no assistente do Homem de Ferro, este projeto combina a potência dos Modelos de Linguagem de Grande Escala (LLMs) com o controlo nativo do sistema operativo, permitindo uma interação natural por voz e a capacidade de executar ações complexas tanto localmente como remotamente através da nuvem.

✨ Funcionalidades

🗣️ Comunicação por Voz Natural:

Escuta passiva em segundo plano com deteção de wake words (ex: "Jarvis", "Computador").

Respostas áudio de alta qualidade utilizando vozes neurais da Microsoft (edge-tts).

🧠 Cérebro de Inteligência Artificial:

Integrado com a API Google Gemini 2.5 Flash para contexto, raciocínio lógico e respostas rápidas e humanizadas.

Capacidade de pesquisar na web em tempo real (Grounding) para dados atualizados (clima, cotações, etc.).

💻 Controlo do Sistema Operativo (Windows):

Abrir/Fechar aplicações (Spotify, Chrome, Bloco de Notas, Calculadora, etc.).

Realizar pesquisas automáticas no navegador.

Consultar o estado do armazenamento local.

☁️ Sincronização e Controlo Remoto:

Autenticação segura de utilizadores gerida pelo Supabase.

Registo de dispositivos e base de dados em tempo real (Realtime Database).

Comandos à distância: Permite que uma interface web/externa envie comandos que o computador executa instantaneamente.

🖥️ Interface Futurista (GUI):

Desenvolvida com customtkinter, apresenta um design "Hacker/Cyberpunk" escuro com um núcleo central animado que reage aos estados do assistente (Ouvindo, Processando, Ocioso).

🏗 Arquitetura e Tecnologias

O projeto está estruturado em módulos independentes para facilitar a escalabilidade:

Frontend (GUI): customtkinter e tkinter (Canvas).

IA & LLM: google-genai (SDK Oficial da Google).

Processamento de Áudio: sounddevice, numpy, scipy (Captação e VAD), SpeechRecognition (STT), edge-tts (TTS), ctypes.windll (Reprodução de áudio nativa).

Backend as a Service (BaaS): supabase (Autenticação, PostgreSQL, Extensão pgvector, Realtime WebSockets).

Integração OS: Subprocessos do Windows (os, subprocess, webbrowser, shutil).

🚀 Instalação e Configuração

1. Pré-requisitos

Sistema Operativo Windows (necessário para os comandos nativos de áudio e automação de janelas).

Python 3.8 ou superior.

Chaves de API do Google AI Studio e do Supabase.

2. Clonar o Repositório e Preparar o Ambiente

# Clonar o repositório
git clone [https://github.com/o-seu-utilizador/assistente-com-ia.git](https://github.com/o-seu-utilizador/assistente-com-ia.git)
cd assistente-com-ia/jarvis_app

# Criar e ativar um ambiente virtual (Recomendado)
python -m venv venv
venv\Scripts\activate


3. Instalar Dependências

Instale as dependências base e os pacotes de processamento de áudio/IA:

pip install -r requirements.txt
pip install sounddevice numpy scipy SpeechRecognition edge-tts google-genai


4. Configurar as Variáveis de Ambiente

Crie um ficheiro .env na raiz da pasta jarvis_app e preencha com as suas credenciais:

Variável

Descrição

GEMINI_API_KEY

Chave gerada no Google AI Studio.

SUPABASE_URL

URL do seu projeto no painel do Supabase.

SUPABASE_KEY

Chave "anon/public" do seu projeto Supabase.

Exemplo do .env:

GEMINI_API_KEY=AIzaSySuaChaveAqui...
SUPABASE_URL=[https://seuid.supabase.co](https://seuid.supabase.co)
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6...


5. Configurar a Base de Dados (Supabase)

Aceda ao seu painel no Supabase.

Navegue até ao SQL Editor.

Copie o conteúdo do ficheiro jarvis_supabase_schema.sql fornecido na raiz do projeto e execute-o. Isto criará as tabelas de perfis, dispositivos, comandos e ativará as funcionalidades em tempo real (Realtime).

🕹️ Como Utilizar

Iniciar a Aplicação:
Certifique-se de que o ambiente virtual está ativo e execute:

python main.py


Primeiro Acesso:

Na interface inicial (Terminal de Acesso), clique em "CREATE NEW IDENTITY" para criar a sua conta (ou faça login se já a tiver).

Conceda permissão de acesso ao microfone.

Interação:

O sistema entrará em estado de vigília ("AGUARDANDO").

Diga a palavra de ativação: "Jarvis..." seguida do seu pedido, ou clique no botão "🎤 INICIALIZAR".

Exemplos de Comandos:

"Jarvis, abre o Spotify."

"Podes fechar o bloco de notas?"

"Faz uma pesquisa por receitas de bacalhau."

"Qual é o estado do meu armazenamento no disco C?"

"Qual é a cotação do Euro hoje?" (O Gemini pesquisa no Google e responde-lhe em voz).

📂 Estrutura de Ficheiros

📁 ASSISTENTE-COM-IA/
├── 📄 jarvis_supabase_schema.sql  # Estrutura da DB para o Supabase
└── 📁 jarvis_app/
    ├── 📄 main.py                 # Interface gráfica principal e Core Loop
    ├── 📄 config.json             # Ficheiro de configuração local (gerado automaticamente)
    ├── 📄 requirements.txt        # Dependências principais
    ├── 📄 .env                    # Variáveis de ambiente (CRIAR)
    └── 📁 src/
        ├── 📄 audio_manager.py    # Processamento STT, TTS e Wake Word
        ├── 📄 os_controller.py    # Integração de automação com o Windows
        ├── 📄 settings_manager.py # Gestão do config.json local
        └── 📄 supabase_client.py  # Conexão à Cloud, Auth e Listener em tempo real


🛡️ Privacidade e Segurança

Processamento de Áudio: As capturas de áudio para deteção de comandos e conversão de texto-para-fala (TTS) geram ficheiros temporários que são eliminados automaticamente pelo sistema após a sua utilização.

Segurança Supabase: O esquema SQL inclui políticas Row Level Security (RLS), garantindo que apenas o seu utilizador pode aceder aos seus dispositivos, mensagens e comandos remotos.
