# backend/app/services/prediction_service.py
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, Union
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.app.schemas.data_schema import ProblemType
from backend.app.utils.file_handler import MODELS_DIR

class PredictionService:
    def __init__(self, job_id: str, model_name: str = None):
        self.job_id = job_id
        self.model_name = model_name
        self.model = None
        self.artifacts = None
        self.problem_type = None
        self._load_model()
        
    def _load_model(self):
        job_dir = MODELS_DIR / self.job_id
        
        if self.model_name is None:
            results_path = job_dir / 'training_results.json'
            if results_path.exists():
                import json
                with open(results_path, 'r') as f:
                    results = json.load(f)
                    self.model_name = results.get('best_model')
        
        if self.model_name:
            model_path = job_dir / f"{self.model_name}.pkl"
            artifacts_path = job_dir / f"{self.model_name}_artifacts.pkl"
            
            if model_path.exists():
                self.model = joblib.load(model_path)
            
            if artifacts_path.exists():
                self.artifacts = joblib.load(artifacts_path)
    
    def predict(self, features: Dict[str, Any]) -> Union[Any, Dict]:
        if self.model is None:
            raise ValueError("Modelo não carregado")
        
        df = pd.DataFrame([features])
        
        if self.artifacts and 'feature_columns' in self.artifacts:
            expected_cols = self.artifacts['feature_columns']
            for col in expected_cols:
                if col not in df.columns:
                    df[col] = 0
            df = df[expected_cols]
        
        prediction = self.model.predict(df)[0]
        
        probabilities = None
        if hasattr(self.model, 'predict_proba'):
            proba = self.model.predict_proba(df)[0]
            if self.artifacts and 'target_classes' in self.artifacts:
                probabilities = dict(zip(self.artifacts['target_classes'], proba))
            else:
                probabilities = proba.tolist()
        
        result = {
            'prediction': prediction.tolist() if isinstance(prediction, np.ndarray) else prediction,
            'model_used': self.model_name
        }
        
        if probabilities is not None:
            result['probabilities'] = probabilities
            if isinstance(probabilities, dict):
                result['confidence'] = max(probabilities.values())
            elif isinstance(probabilities, list):
                result['confidence'] = max(probabilities)
        
        return result
    
    def predict_batch(self, features_list: list) -> list:
        results = []
        for features in features_list:
            try:
                result = self.predict(features)
                results.append(result)
            except Exception as e:
                results.append({'error': str(e), 'features': features})
        
        return results