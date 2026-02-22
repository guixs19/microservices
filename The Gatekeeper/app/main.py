"""
Arquivo principal do Sistema de Créditos
FastAPI + SQLite + JWT
"""

import os
import sys
import logging
from datetime import timedelta, datetime
from typing import Optional

# FastAPI imports
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse

# SQLAlchemy
from sqlalchemy.orm import Session

# ============================================
# CONFIGURAÇÃO DE LOGGING
# ============================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ============================================
# CONFIGURAÇÃO DE PATH (IMPORTANTE PARA WINDOWS)
# ============================================

# Adicionar o diretório raiz ao PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

logger.info(f"📂 Diretório atual: {current_dir}")
logger.info(f"📂 Diretório pai: {parent_dir}")

# ============================================
# IMPORTS DO PROJETO (CORRIGIDOS - ABSOLUTOS)
# ============================================

try:
    from app.database import engine, get_db, SessionLocal, Base
    from app import models, schemas, crud, auth
    from app.routes import users, payments
    logger.info("✅ Imports do projeto carregados com sucesso")
except ImportError as e:
    logger.error(f"❌ Erro nos imports: {e}")
    logger.info("📋 Verifique se todos os arquivos __init__.py existem")
    raise

# ============================================
# CRIAÇÃO DO APP FASTAPI
# ============================================

# Criar tabelas no banco de dados (apenas uma vez)
try:
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Tabelas criadas/verificadas no banco de dados")
except Exception as e:
    logger.error(f"❌ Erro ao criar tabelas: {e}")

# Instância principal do FastAPI
app = FastAPI(
    title="Sistema de Créditos",
    description="API para gerenciamento de créditos com saldo negativo proibido",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# ARQUIVOS ESTÁTICOS E TEMPLATES
# ============================================

# Configurar caminhos absolutos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
DATA_DIR = os.path.join(parent_dir, "data")

# Criar diretórios se não existirem
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "css"), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "js"), exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

logger.info(f"📁 Diretório estático: {STATIC_DIR}")
logger.info(f"📁 Diretório templates: {TEMPLATES_DIR}")
logger.info(f"📁 Diretório dados: {DATA_DIR}")

# Montar arquivos estáticos
try:
    if os.path.exists(STATIC_DIR):
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
        logger.info(f"✅ Arquivos estáticos montados")
    else:
        logger.warning(f"⚠️ Diretório estático não encontrado")
except Exception as e:
    logger.error(f"❌ Erro ao montar estáticos: {e}")

# Configurar templates
try:
    if os.path.exists(TEMPLATES_DIR):
        templates = Jinja2Templates(directory=TEMPLATES_DIR)
        logger.info(f"✅ Templates carregados")
    else:
        logger.warning(f"⚠️ Diretório de templates não encontrado")
        templates = None
except Exception as e:
    logger.error(f"❌ Erro ao carregar templates: {e}")
    templates = None

# ============================================
# ROTAS DE PÁGINAS
# ============================================

@app.get("/", tags=["Pages"])
async def root(request: Request):
    """Página inicial com login/registro"""
    if templates:
        try:
            return templates.TemplateResponse(
                "index.html", 
                {"request": request, "datetime": datetime}
            )
        except Exception as e:
            logger.error(f"Erro ao renderizar index: {e}")
            return JSONResponse({
                "error": "Erro ao carregar página",
                "detail": str(e)
            })
    else:
        return JSONResponse({
            "error": "Templates não disponíveis",
            "message": "Verifique se a pasta app/templates existe"
        })

@app.get("/dashboard", tags=["Pages"])
async def dashboard(request: Request):
    """Dashboard do usuário"""
    if templates:
        try:
            return templates.TemplateResponse(
                "dashboard.html", 
                {"request": request, "datetime": datetime}
            )
        except Exception as e:
            logger.error(f"Erro ao renderizar dashboard: {e}")
            return JSONResponse({
                "error": "Erro ao carregar dashboard",
                "detail": str(e)
            })
    else:
        return JSONResponse({
            "error": "Templates não disponíveis",
            "message": "Verifique se a pasta app/templates existe"
        })

# ============================================
# ROTAS DE DIAGNÓSTICO
# ============================================

@app.get("/system/health", tags=["System"])
async def health_check():
    """Rota de diagnóstico para verificar o status do sistema"""
    # Verificar banco de dados
    db_status = "unknown"
    db_detail = ""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        db_status = "connected"
    except Exception as e:
        db_status = "error"
        db_detail = str(e)
    
    # Verificar arquivos
    static_files = []
    if os.path.exists(STATIC_DIR):
        static_files = os.listdir(STATIC_DIR)
    
    template_files = []
    if os.path.exists(TEMPLATES_DIR):
        template_files = os.listdir(TEMPLATES_DIR)
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "timestamp": datetime.now().isoformat(),
        "app": app.title,
        "version": app.version,
        "database": {
            "status": db_status,
            "detail": db_detail,
            "path": str(engine.url)
        },
        "directories": {
            "static_exists": os.path.exists(STATIC_DIR),
            "static_files": static_files,
            "templates_exists": os.path.exists(TEMPLATES_DIR),
            "template_files": template_files,
            "data_exists": os.path.exists(DATA_DIR)
        }
    }

@app.get("/system/info", tags=["System"])
async def system_info():
    """Informações detalhadas do sistema"""
    return {
        "app_name": app.title,
        "version": app.version,
        "python_version": sys.version,
        "platform": sys.platform,
        "current_dir": os.getcwd(),
        "endpoints": [
            {"path": route.path, "name": route.name}
            for route in app.routes if hasattr(route, "path")
        ]
    }

# ============================================
# AUTENTICAÇÃO
# ============================================

@app.post("/token", response_model=schemas.Token, tags=["Authentication"])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Endpoint de login para obter token JWT"""
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    logger.info(f"✅ Login bem-sucedido: {user.username}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# ============================================
# ROTAS DE EXPORTAÇÃO
# ============================================

@app.get("/export/transactions", tags=["Utilities"])
async def export_transactions(
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(auth.get_current_active_user)
):
    """Exporta o histórico de transações em formato CSV"""
    from io import StringIO
    import csv
    
    transactions = crud.get_user_transactions(db, current_user.id)
    
    # Criar CSV em memória
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Tipo', 'Valor', 'Descrição', 'Data', 'Status'])
    
    for t in transactions:
        writer.writerow([
            t.id,
            t.type,
            f"{t.amount:.2f}",
            t.description or "",
            t.timestamp.strftime("%d/%m/%Y %H:%M:%S"),
            t.status
        ])
    
    output.seek(0)
    
    filename = f"transactions_{current_user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/export/stats", tags=["Utilities"])
async def export_stats(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(auth.get_current_active_user)
):
    """Exporta estatísticas em formato JSON"""
    stats = crud.get_transaction_stats(db, current_user.id, days)
    daily = crud.get_daily_summary(db, current_user.id, 7)
    
    return {
        "user": current_user.username,
        "current_balance": current_user.balance,
        "stats": stats,
        "daily_summary": daily,
        "exported_at": datetime.now().isoformat()
    }

# ============================================
# ROTA DE DEBUG (OPCIONAL - REMOVER EM PRODUÇÃO)
# ============================================

@app.get("/debug/routes", tags=["Debug"])
async def debug_routes():
    """Lista todas as rotas disponíveis (apenas para desenvolvimento)"""
    routes = []
    for route in app.routes:
        routes.append({
            "path": route.path,
            "name": route.name,
            "methods": list(route.methods) if hasattr(route, "methods") else []
        })
    return {
        "total": len(routes),
        "routes": routes
    }

# ============================================
# INCLUSÃO DAS ROTAS DOS MÓDULOS
# ============================================

# IMPORTANTE: Incluir rotas com prefixo completo
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])

# Log das rotas incluídas
logger.info("🔄 Rotas incluídas:")
logger.info(f"   - /api/users/*")
logger.info(f"   - /api/payments/*")

# ============================================
# EVENTOS DE INICIALIZAÇÃO
# ============================================

@app.on_event("startup")
async def startup_event():
    """Evento executado na inicialização"""
    logger.info("=" * 60)
    logger.info("🚀 SISTEMA DE CRÉDITOS INICIADO COM SUCESSO")
    logger.info("=" * 60)
    logger.info(f"📂 Diretório base: {BASE_DIR}")
    logger.info(f"📊 Documentação: http://localhost:8000/docs")
    logger.info(f"💚 Health Check: http://localhost:8000/system/health")
    logger.info(f"🔍 Debug Routes: http://localhost:8000/debug/routes")
    logger.info("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """Evento executado no desligamento"""
    logger.info("👋 Sistema de créditos finalizado")

# ============================================
# HANDLERS DE ERRO
# ============================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handler para exceções HTTP"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "detail": exc.detail,
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handler para exceções não tratadas"""
    logger.error(f"Erro não tratado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "detail": "Erro interno do servidor",
            "message": str(exc) if app.debug else None,
            "path": str(request.url)
        }
    )

# ============================================
# EXECUÇÃO DIRETA
# ============================================

if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 60)
    print("🚀 INICIANDO SERVIDOR DE DESENVOLVIMENTO")
    print("=" * 60)
    print(f"\n📂 Diretório: {os.getcwd()}")
    print(f"🐍 Python: {sys.executable}")
    print("\n📌 Acesse:")
    print("   • Aplicação: http://localhost:8000")
    print("   • Documentação: http://localhost:8000/docs")
    print("   • Health Check: http://localhost:8000/system/health")
    print("   • Debug Routes: http://localhost:8000/debug/routes")
    print("\n" + "=" * 60 + "\n")
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=["app"]
    )