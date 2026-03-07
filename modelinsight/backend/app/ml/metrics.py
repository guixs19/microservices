# backend/app/ml/metrics.py
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.app.utils.file_handler import PROCESSED_DIR, MODELS_DIR

class MetricsCalculator:
    @staticmethod
    def load_predictions(job_id: str, model_name: str) -> Optional[pd.DataFrame]:
        pred_path = PROCESSED_DIR / job_id / f"{model_name}_predictions.csv"
        if pred_path.exists():
            return pd.read_csv(pred_path)
        return None
    
    @staticmethod
    def get_comparison_data(job_id: str) -> Dict[str, Any]:
        job_dir = PROCESSED_DIR / job_id
        models_dir = MODELS_DIR / job_id
        
        results_path = models_dir / 'training_results.json'
        if not results_path.exists():
            return {"error": "Resultados não encontrados"}
        
        with open(results_path, 'r') as f:
            training_results = json.load(f)
        
        comparison_data = {
            "job_id": job_id,
            "problem_type": training_results['problem_type'],
            "best_model": training_results['best_model'],
            "models": []
        }
        
        for model_name, model_info in training_results['results'].items():
            predictions_df = MetricsCalculator.load_predictions(job_id, model_name)
            
            model_data = {
                "name": model_name,
                "metrics": model_info.get('metrics', {}),
                "best_params": model_info.get('best_params', {}),
                "is_best": model_name == training_results['best_model']
            }
            
            if predictions_df is not None:
                sample_size = min(100, len(predictions_df))
                sample = predictions_df.sample(n=sample_size, random_state=42)
                
                model_data["predictions"] = {
                    "actual": sample['actual'].tolist(),
                    "predicted": sample['predicted'].tolist(),
                    "indices": sample.index.tolist()
                }
            
            comparison_data["models"].append(model_data)
        
        return comparison_data
    
    @staticmethod
    def calculate_feature_importance(model, feature_names: List[str]) -> Dict[str, float]:
        importance = {}
        
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            importance = dict(zip(feature_names, importances))
            
        elif hasattr(model, 'coef_'):
            coef = model.coef_
            if len(coef.shape) > 1:
                coef = np.mean(np.abs(coef), axis=0)
            else:
                coef = np.abs(coef)
            
            importance = dict(zip(feature_names, coef))
        
        importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
        
        return importance