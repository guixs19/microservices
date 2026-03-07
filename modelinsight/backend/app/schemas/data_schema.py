from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from enum import Enum

class ProblemType(str, Enum):
    CLASSIFICATION = "classification"
    REGRESSION = "regression"

class UploadResponse(BaseModel):
    filename: str
    columns: List[str]
    row_count: int
    target_column: str
    problem_type: ProblemType
    job_id: str
    status: str = "processing"

class JobStatusResponse(BaseModel):
    job_id: str
    status: str  # "processing", "completed", "failed"
    progress: Optional[float] = None
    message: Optional[str] = None
    results_url: Optional[str] = None

class ModelMetrics(BaseModel):
    model_name: str
    model_type: str
    metrics: Dict[str, float]
    best_params: Dict[str, Any]
    is_best: bool = False

class TrainingResultsResponse(BaseModel):
    job_id: str
    target_column: str
    problem_type: ProblemType
    models: List[ModelMetrics]
    best_model: str
    feature_importance: Optional[Dict[str, float]] = None
    predictions_path: Optional[str] = None

class PredictionRequest(BaseModel):
    features: Dict[str, Any]
    model_id: Optional[str] = None  # Se None, usa o melhor modelo

class PredictionResponse(BaseModel):
    prediction: Any
    model_used: str
    confidence: Optional[float] = None
    probabilities: Optional[Dict[str, float]] = None