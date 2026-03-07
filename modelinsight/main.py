# main.py na raiz do projeto
import sys
import os
import subprocess
import webbrowser
import time
import threading
import signal
from pathlib import Path

# Configurações
BACKEND_PORT = 8000
FRONTEND_PORT = 8001
BACKEND_DIR = Path(__file__).parent / "backend"
FRONTEND_DIR = Path(__file__).parent / "frontend"

# Processos globais
backend_process = None
frontend_process = None

def print_header():
    """Imprime cabeçalho bonito"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║   ███╗   ███╗ ██████╗ ██████╗ ███████╗██╗               ║
    ║   ████╗ ████║██╔═══██╗██╔══██╗██╔════╝██║               ║
    ║   ██╔████╔██║██║   ██║██║  ██║█████╗  ██║               ║
    ║   ██║╚██╔╝██║██║   ██║██║  ██║██╔══╝  ██║               ║
    ║   ██║ ╚═╝ ██║╚██████╔╝██████╔╝███████╗███████╗          ║
    ║   ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝╚══════╝          ║
    ║                                                          ║
    ║              🚀 INICIANDO MODELINSIGHT                   ║
    ╚══════════════════════════════════════════════════════════╝
    """)

def start_backend():
    """Inicia o servidor backend FastAPI"""
    global backend_process
    
    print("\n📡 Iniciando Backend...")
    print(f"   Diretório: {BACKEND_DIR}")
    
    # Verifica se o diretório existe
    if not BACKEND_DIR.exists():
        print(f"❌ Erro: Diretório backend não encontrado em {BACKEND_DIR}")
        return False
    
    # Comando para iniciar o backend
    if sys.platform == "win32":
        cmd = f"cd /d {BACKEND_DIR} && uvicorn app.main:app --reload --host 0.0.0.0 --port {BACKEND_PORT}"
        backend_process = subprocess.Popen(cmd, shell=True)
    else:
        cmd = ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", str(BACKEND_PORT)]
        backend_process = subprocess.Popen(cmd, cwd=str(BACKEND_DIR))
    
    print(f"✅ Backend iniciado em http://localhost:{BACKEND_PORT}")
    print(f"📚 Documentação: http://localhost:{BACKEND_PORT}/docs")
    return True

def start_frontend():
    """Inicia o servidor frontend com Python HTTP server"""
    global frontend_process
    
    print("\n🌐 Iniciando Frontend...")
    print(f"   Diretório: {FRONTEND_DIR}")
    
    # Verifica se o diretório existe
    if not FRONTEND_DIR.exists():
        print(f"❌ Erro: Diretório frontend não encontrado em {FRONTEND_DIR}")
        return False
    
    # Inicia servidor HTTP simples do Python
    if sys.platform == "win32":
        cmd = f"cd /d {FRONTEND_DIR} && python -m http.server {FRONTEND_PORT}"
        frontend_process = subprocess.Popen(cmd, shell=True)
    else:
        cmd = ["python", "-m", "http.server", str(FRONTEND_PORT)]
        frontend_process = subprocess.Popen(cmd, cwd=str(FRONTEND_DIR))
    
    print(f"✅ Frontend iniciado em http://localhost:{FRONTEND_PORT}")
    return True

def open_browser():
    """Abre o navegador automaticamente"""
    print("\n🌍 Abrindo navegador...")
    time.sleep(2)  # Aguarda os servidores iniciarem
    
    # Tenta abrir o frontend
    frontend_url = f"http://localhost:{FRONTEND_PORT}"
    webbrowser.open(frontend_url)
    print(f"✅ Navegador aberto em {frontend_url}")

def check_backend_health():
    """Verifica se o backend está saudável"""
    import urllib.request
    import json
    
    try:
        with urllib.request.urlopen(f"http://localhost:{BACKEND_PORT}/health", timeout=2) as response:
            data = json.loads(response.read().decode())
            return data.get("status") == "healthy"
    except:
        return False

def wait_for_backend():
    """Aguarda o backend ficar pronto"""
    print("\n⏳ Aguardando backend inicializar...")
    for i in range(10):
        if check_backend_health():
            print("✅ Backend pronto!")
            return True
        print(f"   Tentativa {i+1}/10...")
        time.sleep(1)
    
    print("⚠️  Backend pode não estar totalmente pronto, mas continuando...")
    return False

def signal_handler(sig, frame):
    """Handler para Ctrl+C"""
    print("\n\n🛑 Encerrando ModelInsight...")
    
    global backend_process, frontend_process
    
    # Encerra processos
    if backend_process:
        print("   Encerrando backend...")
        if sys.platform == "win32":
            backend_process.terminate()
        else:
            backend_process.terminate()
    
    if frontend_process:
        print("   Encerrando frontend...")
        if sys.platform == "win32":
            frontend_process.terminate()
        else:
            frontend_process.terminate()
    
    print("✅ ModelInsight encerrado!")
    sys.exit(0)

def create_directories():
    """Cria diretórios necessários"""
    print("\n📁 Verificando diretórios...")
    
    dirs = [
        Path(__file__).parent / "data" / "uploads",
        Path(__file__).parent / "data" / "processed",
        Path(__file__).parent / "models",
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {dir_path}")
    
    return True

def install_dependencies():
    """Verifica e instala dependências se necessário"""
    print("\n📦 Verificando dependências...")
    
    try:
        import fastapi
        import uvicorn
        import pandas
        import sklearn
        print("   ✅ Todas as dependências estão instaladas!")
        return True
    except ImportError as e:
        print(f"   ⚠️  Dependência faltando: {e}")
        print("\n   Instalando dependências...")
        
        requirements_file = BACKEND_DIR / "requirements.txt"
        if requirements_file.exists():
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
            print("   ✅ Dependências instaladas!")
            return True
        else:
            print(f"   ❌ Arquivo requirements.txt não encontrado em {requirements_file}")
            return False

def main():
    """Função principal"""
    
    # Configurar handler para Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Imprime cabeçalho
    print_header()
    
    # Cria diretórios
    create_directories()
    
    # Verifica dependências
    if not install_dependencies():
        print("\n❌ Erro ao verificar dependências. Continuando mesmo assim...")
    
    # Inicia backend
    if not start_backend():
        print("\n❌ Erro ao iniciar backend. Abortando.")
        return
    
    # Aguarda backend
    wait_for_backend()
    
    # Inicia frontend
    if not start_frontend():
        print("\n❌ Erro ao iniciar frontend. Abortando.")
        return
    
    # Abre navegador
    open_browser()
    
    # Mantém o programa rodando
    print("\n" + "="*60)
    print("🎯 ModelInsight está rodando!")
    print("="*60)
    print(f"📊 Frontend: http://localhost:{FRONTEND_PORT}")
    print(f"⚙️  Backend:  http://localhost:{BACKEND_PORT}")
    print(f"📚 Docs:     http://localhost:{BACKEND_PORT}/docs")
    print("\n✅ Pressione Ctrl+C para encerrar todos os serviços")
    print("="*60)
    
    # Mantém o processo principal vivo
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()