# backend/app/main.py
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Agora importamos do backend usando o caminho absoluto
from backend.app.api import routes_upload, routes_metrics, routes_predict

app = FastAPI(
    title="ModelInsight API",
    description="API para treinamento automático de modelos de Machine Learning",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_upload.router, prefix="/api")
app.include_router(routes_metrics.router, prefix="/api")
app.include_router(routes_predict.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Bem-vindo ao ModelInsight API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}