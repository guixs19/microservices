# backend/app/api/routes_upload.py
from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
import uuid
from typing import Optional
import os
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# CORREÇÃO: Importar do backend.app
from backend.app.schemas.data_schema import UploadResponse, ProblemType, JobStatusResponse
from backend.app.utils.file_handler import save_upload_file, UPLOAD_DIR, PROCESSED_DIR
from backend.app.services.csv_service import CSVService
from backend.app.ml.train_model import ModelTrainer

router = APIRouter(prefix="/upload", tags=["upload"])
job_status = {}

@router.post("/", response_model=UploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    target_column: str = Form(...),
    problem_type: ProblemType = Form(...)
):
    job_id = str(uuid.uuid4())
    file_content = await file.read()
    file_path = save_upload_file(file_content, file.filename)
    
    csv_service = CSVService(file_path)
    success, message = csv_service.load_and_validate()
    
    if not success:
        return JSONResponse(status_code=400, content={"message": message})
    
    basic_info = csv_service.get_basic_info()
    
    background_tasks.add_task(
        train_model_background,
        job_id,
        file_path,
        target_column,
        problem_type
    )
    
    job_status[job_id] = {
        "status": "processing",
        "progress": 0,
        "message": "Treinamento iniciado"
    }
    
    return UploadResponse(
        filename=file.filename,
        columns=basic_info["columns"],
        row_count=basic_info["row_count"],
        target_column=target_column,
        problem_type=problem_type,
        job_id=job_id
    )

@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    if job_id not in job_status:
        results_path = PROCESSED_DIR / job_id
        if results_path.exists():
            return JobStatusResponse(
                job_id=job_id,
                status="completed",
                progress=100,
                message="Treinamento concluído",
                results_url=f"/api/metrics/{job_id}"
            )
        else:
            return JSONResponse(status_code=404, content={"message": "Job não encontrado"})
    
    status = job_status[job_id]
    return JobStatusResponse(
        job_id=job_id,
        status=status["status"],
        progress=status.get("progress", 0),
        message=status.get("message", ""),
        results_url=f"/api/metrics/{job_id}" if status["status"] == "completed" else None
    )

def train_model_background(job_id: str, file_path: str, target_column: str, problem_type: ProblemType):
    try:
        job_status[job_id]["message"] = "Preparando dados..."
        trainer = ModelTrainer(file_path, target_column, problem_type, job_id)
        result = trainer.run_training()
        
        if result["status"] == "success":
            job_status[job_id]["status"] = "completed"
            job_status[job_id]["progress"] = 100
            job_status[job_id]["message"] = "Treinamento concluído com sucesso!"
            job_status[job_id]["result"] = result
        else:
            job_status[job_id]["status"] = "failed"
            job_status[job_id]["message"] = f"Erro: {result.get('message', 'Erro desconhecido')}"
            
    except Exception as e:
        job_status[job_id]["status"] = "failed"
        job_status[job_id]["message"] = f"Erro: {str(e)}"
        import traceback
        traceback.print_exc()
    
    finally:
        try:
            os.remove(file_path)
        except:
            pass