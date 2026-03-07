# backend/app/api/routes_metrics.py
from fastapi import APIRouter, HTTPException
from typing import Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.app.ml.metrics import MetricsCalculator

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get("/{job_id}")
async def get_training_results(job_id: str):
    comparison_data = MetricsCalculator.get_comparison_data(job_id)
    
    if "error" in comparison_data:
        raise HTTPException(status_code=404, detail=comparison_data["error"])
    
    return comparison_data

@router.get("/{job_id}/model/{model_name}")
async def get_model_details(job_id: str, model_name: str):
    comparison_data = MetricsCalculator.get_comparison_data(job_id)
    
    if "error" in comparison_data:
        raise HTTPException(status_code=404, detail=comparison_data["error"])
    
    for model in comparison_data["models"]:
        if model["name"] == model_name:
            return model
    
    raise HTTPException(status_code=404, detail=f"Modelo {model_name} não encontrado")