import os
import uuid
import pandas as pd
from pathlib import Path
from typing import Optional

# Configurações de diretórios
BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
MODELS_DIR = BASE_DIR / "models"

# Criar diretórios se não existirem
for dir_path in [UPLOAD_DIR, PROCESSED_DIR, MODELS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

def save_upload_file(file_content: bytes, filename: str) -> str:
    """Salva o arquivo upload e retorna o caminho completo"""
    # Gerar um nome único para evitar conflitos
    file_id = str(uuid.uuid4())
    safe_filename = f"{file_id}_{filename}"
    file_path = UPLOAD_DIR / safe_filename
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    return str(file_path)

def load_csv(file_path: str) -> Optional[pd.DataFrame]:
    """Carrega um arquivo CSV como DataFrame"""
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"Erro ao carregar CSV: {e}")
        return None

def create_job_directory(job_id: str) -> Path:
    """Cria diretório específico para um job"""
    job_dir = PROCESSED_DIR / job_id
    job_dir.mkdir(exist_ok=True)
    return job_dir

def save_trained_model(model, job_id: str, model_name: str, artifacts: dict = None):
    """Salva o modelo treinado e seus artefatos"""
    import joblib
    
    job_dir = MODELS_DIR / job_id
    job_dir.mkdir(exist_ok=True)
    
    # Salvar o modelo
    model_path = job_dir / f"{model_name}.pkl"
    joblib.dump(model, model_path)
    
    # Salvar artefatos adicionais (scaler, colunas, etc)
    if artifacts:
        artifacts_path = job_dir / f"{model_name}_artifacts.pkl"
        joblib.dump(artifacts, artifacts_path)
    
    return str(model_path)