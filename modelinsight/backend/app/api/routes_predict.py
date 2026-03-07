# backend/app/api/routes_predict.py
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.app.schemas.data_schema import PredictionRequest, PredictionResponse
from backend.app.services.prediction_service import PredictionService

router = APIRouter(prefix="/predict", tags=["predict"])

@router.post("/{job_id}", response_model=PredictionResponse)
async def predict_single(
    job_id: str,
    request: PredictionRequest,
    model_name: Optional[str] = Query(None, description="Nome do modelo específico")
):
    try:
        model_to_use = model_name or request.model_id
        prediction_service = PredictionService(job_id, model_to_use)
        result = prediction_service.predict(request.features)
        
        return PredictionResponse(
            prediction=result['prediction'],
            model_used=result['model_used'],
            confidence=result.get('confidence'),
            probabilities=result.get('probabilities')
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{job_id}/batch")
async def predict_batch(
    job_id: str,
    features_list: List[Dict[str, Any]],
    model_name: Optional[str] = Query(None, description="Nome do modelo específico")
):
    try:
        prediction_service = PredictionService(job_id, model_name)
        results = prediction_service.predict_batch(features_list)
        
        return {
            "job_id": job_id,
            "model_used": model_name or "best_model",
            "predictions": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))