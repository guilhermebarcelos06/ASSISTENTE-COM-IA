<h1 align="center">🤖 J.A.R.V.I.S. Core System</h1>

<p align="center">
  <strong>Assistente Virtual Inteligente com Automação de Sistema e Controlo via Cloud</strong>
</p>

<p align="center">
  O J.A.R.V.I.S. Core System é uma aplicação de desktop para Windows desenvolvida em Python. Inspirado no assistente do Homem de Ferro, este projeto combina a potência dos Modelos de Linguagem de Grande Escala (LLMs) com o controlo nativo do sistema operativo, permitindo uma interação natural por voz e a capacidade de executar ações complexas tanto localmente como remotamente através da nuvem.
</p>

<hr />

<h2>📋 Índice</h2>
<ul>
  <li><a href="#-funcionalidades">Funcionalidades</a></li>
  <li><a href="#-arquitetura-e-tecnologias">Arquitetura e Tecnologias</a></li>
  <li><a href="#-instalação-e-configuração">Instalação e Configuração</a></li>
  <li><a href="#-como-utilizar">Como Utilizar</a></li>
  <li><a href="#-estrutura-de-ficheiros">Estrutura de Ficheiros</a></li>
  <li><a href="#-privacidade-e-segurança">Privacidade e Segurança</a></li>
</ul>

<hr />

<h2>✨ Funcionalidades</h2>

<h3>🗣️ Comunicação por Voz Natural</h3>
<ul>
  <li>Escuta passiva em segundo plano com deteção de wake words (ex: "Jarvis", "Computador").</li>
  <li>Respostas áudio de alta qualidade utilizando vozes neurais da Microsoft (<code>edge-tts</code>).</li>
</ul>

<h3>🧠 Cérebro de Inteligência Artificial</h3>
<ul>
  <li>Integrado com a API <strong>Google Gemini 2.5 Flash</strong> para contexto, raciocínio lógico e respostas rápidas e humanizadas.</li>
  <li>Capacidade de pesquisar na web em tempo real (Grounding) para dados atualizados (clima, cotações, etc.).</li>
</ul>

<h3>💻 Controlo do Sistema Operativo (Windows)</h3>
<ul>
  <li>Abrir/Fechar aplicações (Spotify, Chrome, Bloco de Notas, Calculadora, etc.).</li>
  <li>Realizar pesquisas automáticas no navegador.</li>
  <li>Consultar o estado do armazenamento local.</li>
</ul>

<h3>☁️ Sincronização e Controlo Remoto</h3>
<ul>
  <li>Autenticação segura de utilizadores gerida pelo <strong>Supabase</strong>.</li>
  <li>Registo de dispositivos e base de dados em tempo real (Realtime Database).</li>
  <li><strong>Comandos à distância:</strong> Permite que uma interface web/externa envie comandos que o computador executa instantaneamente.</li>
</ul>

<h3>🖥️ Interface Futurista (GUI)</h3>
<ul>
  <li>Desenvolvida com <code>customtkinter</code>, apresenta um design "Hacker/Cyberpunk" escuro com um núcleo central animado que reage aos estados do assistente (Ouvindo, Processando, Ocioso).</li>
</ul>

<hr />

<h2>🏗 Arquitetura e Tecnologias</h2>
<p>O projeto está estruturado em módulos independentes para facilitar a escalabilidade:</p>
<ul>
  <li><strong>Frontend (GUI):</strong> <code>customtkinter</code> e <code>tkinter</code> (Canvas).</li>
  <li><strong>IA & LLM:</strong> <code>google-genai</code> (SDK Oficial da Google).</li>
  <li><strong>Processamento de Áudio:</strong> <code>sounddevice</code>, <code>numpy</code>, <code>scipy</code> (Captação e VAD), <code>SpeechRecognition</code> (STT), <code>edge-tts</code> (TTS).</li>
  <li><strong>Backend as a Service (BaaS):</strong> <code>supabase</code> (Autenticação, PostgreSQL, Realtime WebSockets).</li>
  <li><strong>Integração OS:</strong> Subprocessos do Windows (<code>os</code>, <code>subprocess</code>, <code>webbrowser</code>, <code>shutil</code>).</li>
</ul>

<hr />

<h2>🚀 Instalação e Configuração</h2>

<h3>1. Pré-requisitos</h3>
<ul>
  <li>Sistema Operativo Windows (necessário para os comandos nativos de áudio e automação de janelas).</li>
  <li>Python 3.8 ou superior.</li>
  <li>Chaves de API do Google AI Studio e do Supabase.</li>
</ul>

<h3>2. Clonar o Repositório e Preparar o Ambiente</h3>
<pre><code># Clonar o repositório
git clone https://github.com/o-seu-utilizador/assistente-com-ia.git
cd assistente-com-ia/jarvis_app

# Criar e ativar um ambiente virtual
python -m venv venv
venv\Scripts\activate
</code></pre>

<h3>3. Instalar Dependências</h3>
<pre><code>pip install -r requirements.txt
pip install sounddevice numpy scipy SpeechRecognition edge-tts google-genai
</code></pre>

<h3>4. Configurar as Variáveis de Ambiente</h3>
<p>Crie um ficheiro <code>.env</code> na raiz da pasta <code>jarvis_app</code> e preencha com as suas credenciais:</p>
<pre><code>GEMINI_API_KEY=AIzaSySuaChaveAqui...
SUPABASE_URL=https://seuid.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6...
</code></pre>

<h3>5. Configurar a Base de Dados (Supabase)</h3>
<ol>
  <li>Aceda ao seu painel no Supabase.</li>
  <li>Navegue até ao SQL Editor.</li>
  <li>Copie o conteúdo do ficheiro <code>jarvis_supabase_schema.sql</code> fornecido na raiz do projeto e execute-o.</li>
</ol>

<hr />

<h2>🕹️ Como Utilizar</h2>
<p>Inicie a aplicação com o comando:</p>
<pre><code>python main.py</code></pre>

<p><strong>Primeiro Acesso:</strong> Clique em "CREATE NEW IDENTITY" para criar a sua conta ou faça login. Conceda permissão de acesso ao microfone.</p>
<p><strong>Interação:</strong> Diga a palavra de ativação: "Jarvis..." seguida do seu pedido, ou clique no botão "🎤 INICIALIZAR".</p>

<hr />

<h2>📂 Estrutura de Ficheiros</h2>
<pre><code>
ASSISTENTE-COM-IA/
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
</code></pre>

<hr />

<h2>🛡️ Privacidade e Segurança</h2>
<ul>
  <li><strong>Processamento de Áudio:</strong> As capturas de áudio geram ficheiros temporários que são eliminados automaticamente.</li>
  <li><strong>Segurança Supabase:</strong> O esquema inclui políticas Row Level Security (RLS) para garantir a privacidade dos dados.</li>
</ul>
