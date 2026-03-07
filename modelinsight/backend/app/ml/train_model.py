# backend/app/ml/train_model.py
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, Optional
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.app.services.csv_service import CSVService
from backend.app.services.model_service import ModelTrainingService
from backend.app.schemas.data_schema import ProblemType
from backend.app.utils.file_handler import create_job_directory, save_trained_model, PROCESSED_DIR

class ModelTrainer:
    def __init__(self, file_path: str, target_column: str, problem_type: ProblemType, job_id: str):
        self.file_path = file_path
        self.target_column = target_column
        self.problem_type = problem_type
        self.job_id = job_id
        self.job_dir = create_job_directory(job_id)
        
    def run_training(self) -> Dict[str, Any]:
        try:
            print("Carregando dados...")
            csv_service = CSVService(self.file_path)
            success, message = csv_service.load_and_validate()
            
            if not success:
                return {"status": "error", "message": message}
            
            print("Preparando dados...")
            X_train, X_test, y_train, y_test = csv_service.prepare_data(
                self.target_column, self.problem_type
            )
            
            feature_columns = list(X_train.columns)
            
            print("Iniciando treinamento dos modelos...")
            model_service = ModelTrainingService(self.problem_type)
            results = model_service.train_with_gridsearch(
                X_train, y_train, X_test, y_test, cv_folds=5
            )
            
            print("Salvando modelos treinados...")
            saved_models = []
            for model_name, model_result in results.items():
                if model_result.get('model') is not None:
                    artifacts = {
                        'feature_columns': feature_columns,
                        'target_column': self.target_column,
                        'problem_type': self.problem_type.value,
                        'metrics': model_result['metrics']
                    }
                    
                    if hasattr(csv_service, 'label_encoders') and 'target' in csv_service.label_encoders:
                        artifacts['target_encoder'] = csv_service.label_encoders['target']
                        artifacts['target_classes'] = list(csv_service.label_encoders['target'].classes_)
                    
                    model_path = save_trained_model(
                        model_result['model'],
                        self.job_id,
                        model_name,
                        artifacts
                    )
                    saved_models.append(model_name)
                    
                    self._save_predictions(model_name, y_test, model_result['predictions'])
            
            results_path = model_service.save_results(self.job_id)
            best_model_name = model_service.best_model_name if hasattr(model_service, 'best_model_name') else None
            
            return {
                "status": "success",
                "job_id": self.job_id,
                "best_model": best_model_name,
                "trained_models": saved_models,
                "results_path": results_path,
                "metrics": {
                    name: res['metrics'] 
                    for name, res in results.items() 
                    if 'metrics' in res
                }
            }
            
        except Exception as e:
            print(f"Erro durante o treinamento: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "job_id": self.job_id,
                "message": str(e)
            }
    
    def _save_predictions(self, model_name: str, y_true, y_pred):
        predictions_df = pd.DataFrame({
            'actual': y_true,
            'predicted': y_pred
        })
        
        pred_path = self.job_dir / f"{model_name}_predictions.csv"
        predictions_df.to_csv(pred_path, index=False)