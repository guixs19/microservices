# backend/app/ml/predict.py
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from typing import Dict, Any, List, Union, Optional, Tuple
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.app.utils.file_handler import MODELS_DIR, PROCESSED_DIR

class ModelPredictor:
    def __init__(self, job_id: str, model_name: Optional[str] = None):
        self.job_id = job_id
        self.model_name = model_name
        self.model = None
        self.artifacts = None
        self.feature_columns = None
        self.target_encoder = None
        self.problem_type = None
        
        self._load_model_and_artifacts()
    
    def _load_model_and_artifacts(self):
        job_dir = MODELS_DIR / self.job_id
        
        if not job_dir.exists():
            raise ValueError(f"Job {self.job_id} não encontrado")
        
        if self.model_name is None:
            self.model_name = self._get_best_model_name()
        
        if self.model_name is None:
            raise ValueError("Nenhum modelo encontrado para este job")
        
        model_path = job_dir / f"{self.model_name}.pkl"
        artifacts_path = job_dir / f"{self.model_name}_artifacts.pkl"
        
        if not model_path.exists():
            raise ValueError(f"Modelo {self.model_name} não encontrado")
        
        self.model = joblib.load(model_path)
        
        if artifacts_path.exists():
            self.artifacts = joblib.load(artifacts_path)
            self.feature_columns = self.artifacts.get('feature_columns', [])
            self.target_encoder = self.artifacts.get('target_encoder')
            self.problem_type = self.artifacts.get('problem_type')
    
    def _get_best_model_name(self) -> Optional[str]:
        job_dir = MODELS_DIR / self.job_id
        results_path = job_dir / 'training_results.json'
        
        if results_path.exists():
            with open(results_path, 'r') as f:
                results = json.load(f)
                return results.get('best_model')
        
        return None
    
    def _preprocess_features(self, features: Dict[str, Any]) -> pd.DataFrame:
        df = pd.DataFrame([features])
        
        if self.feature_columns:
            processed_df = pd.DataFrame(columns=self.feature_columns)
            
            for col in self.feature_columns:
                if col in df.columns:
                    processed_df[col] = df[col].values
                else:
                    processed_df[col] = 0
            
            df = processed_df
        
        for col in df.columns:
            if df[col].dtype == 'bool':
                df[col] = df[col].astype(int)
            
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_numeric(df[col])
                except:
                    pass
        
        return df
    
    def _postprocess_prediction(self, prediction: np.ndarray) -> Any:
        if isinstance(prediction, np.ndarray):
            if len(prediction) == 1:
                prediction = prediction[0]
            else:
                prediction = prediction.tolist()
        
        if self.target_encoder is not None:
            try:
                if isinstance(prediction, (int, np.integer)):
                    prediction = self.target_encoder.inverse_transform([int(prediction)])[0]
                elif isinstance(prediction, list):
                    prediction = self.target_encoder.inverse_transform(prediction).tolist()
            except:
                pass
        
        return prediction
    
    def _get_probabilities(self, df: pd.DataFrame) -> Optional[Dict[str, float]]:
        if hasattr(self.model, 'predict_proba'):
            try:
                proba = self.model.predict_proba(df)[0]
                
                if self.target_encoder is not None:
                    class_names = self.target_encoder.classes_
                    return dict(zip(class_names, proba))
                else:
                    return {f"class_{i}": p for i, p in enumerate(proba)}
            except:
                return None
        return None
    
    def predict_single(self, features: Dict[str, Any]) -> Dict[str, Any]:
        if self.model is None:
            raise ValueError("Modelo não carregado")
        
        df = self._preprocess_features(features)
        prediction = self.model.predict(df)
        processed_prediction = self._postprocess_prediction(prediction)
        probabilities = self._get_probabilities(df)
        
        result = {
            'prediction': processed_prediction,
            'model_used': self.model_name,
            'job_id': self.job_id
        }
        
        if probabilities is not None:
            result['probabilities'] = probabilities
            result['confidence'] = max(probabilities.values())
        
        return result
    
    def predict_batch(self, features_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        
        for features in features_list:
            try:
                result = self.predict_single(features)
                results.append(result)
            except Exception as e:
                results.append({
                    'error': str(e),
                    'features': features,
                    'model_used': self.model_name,
                    'job_id': self.job_id
                })
        
        return results
    
    def predict_from_csv(self, csv_path: str, id_column: Optional[str] = None) -> Dict[str, Any]:
        df = pd.read_csv(csv_path)
        
        if self.feature_columns:
            missing_cols = set(self.feature_columns) - set(df.columns)
            for col in missing_cols:
                df[col] = 0
            
            feature_df = df[self.feature_columns]
        else:
            feature_df = df.select_dtypes(include=[np.number])
        
        predictions = self.model.predict(feature_df)
        processed_predictions = self._postprocess_prediction(predictions)
        
        results = []
        for i in range(len(df)):
            result = {
                'prediction': processed_predictions[i] if isinstance(processed_predictions, list) else processed_predictions,
            }
            
            if id_column and id_column in df.columns:
                result['id'] = df.iloc[i][id_column]
            
            results.append(result)
        
        return {
            'job_id': self.job_id,
            'model_used': self.model_name,
            'predictions': results,
            'total_rows': len(df)
        }

def load_predictor(job_id: str, model_name: Optional[str] = None) -> ModelPredictor:
    return ModelPredictor(job_id, model_name)

def get_available_models(job_id: str) -> List[str]:
    job_dir = MODELS_DIR / job_id
    
    if not job_dir.exists():
        return []
    
    models = []
    for file_path in job_dir.glob("*.pkl"):
        if "_artifacts" not in file_path.name:
            models.append(file_path.stem)
    
    return models

def get_model_info(job_id: str, model_name: str) -> Dict[str, Any]:
    predictor = ModelPredictor(job_id, model_name)
    
    info = {
        'model_name': model_name,
        'job_id': job_id,
        'problem_type': predictor.problem_type,
        'feature_columns': predictor.feature_columns
    }
    
    if predictor.artifacts and 'metrics' in predictor.artifacts:
        info['metrics'] = predictor.artifacts['metrics']
    
    return info

def compare_model_predictions(job_id: str, features: Dict[str, Any]) -> Dict[str, Any]:
    available_models = get_available_models(job_id)
    
    results = {}
    for model_name in available_models:
        try:
            predictor = ModelPredictor(job_id, model_name)
            prediction = predictor.predict_single(features)
            results[model_name] = prediction
        except Exception as e:
            results[model_name] = {'error': str(e)}
    
    return {
        'job_id': job_id,
        'features': features,
        'predictions': results
    }