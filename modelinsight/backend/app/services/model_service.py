# backend/app/services/model_service.py
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from sklearn.model_selection import GridSearchCV, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, mean_absolute_error, r2_score,
    confusion_matrix
)
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge, Lasso
from sklearn.svm import SVC, SVR
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.app.schemas.data_schema import ProblemType

class ModelTrainingService:
    def __init__(self, problem_type: ProblemType):
        self.problem_type = problem_type
        self.models = self._initialize_models()
        self.best_models = {}
        self.results = {}
        
    def _initialize_models(self) -> Dict[str, Dict]:
        # [mesmo código de antes, sem mudanças]
        if self.problem_type == ProblemType.CLASSIFICATION:
            return {
                'Logistic Regression': {
                    'model': LogisticRegression(max_iter=1000, random_state=42),
                    'pipeline': Pipeline([
                        ('scaler', StandardScaler()),
                        ('classifier', LogisticRegression(max_iter=1000, random_state=42))
                    ]),
                    'params': {
                        'classifier__C': [0.1, 1.0, 10.0],
                        'classifier__solver': ['lbfgs', 'liblinear']
                    }
                },
                'Random Forest': {
                    'model': RandomForestClassifier(random_state=42),
                    'pipeline': Pipeline([
                        ('scaler', StandardScaler()),
                        ('classifier', RandomForestClassifier(random_state=42))
                    ]),
                    'params': {
                        'classifier__n_estimators': [50, 100, 200],
                        'classifier__max_depth': [None, 10, 20],
                        'classifier__min_samples_split': [2, 5, 10]
                    }
                },
                'Gradient Boosting': {
                    'model': GradientBoostingClassifier(random_state=42),
                    'pipeline': Pipeline([
                        ('scaler', StandardScaler()),
                        ('classifier', GradientBoostingClassifier(random_state=42))
                    ]),
                    'params': {
                        'classifier__n_estimators': [50, 100],
                        'classifier__learning_rate': [0.01, 0.1],
                        'classifier__max_depth': [3, 5]
                    }
                },
                'SVM': {
                    'model': SVC(random_state=42, probability=True),
                    'pipeline': Pipeline([
                        ('scaler', StandardScaler()),
                        ('classifier', SVC(random_state=42, probability=True))
                    ]),
                    'params': {
                        'classifier__C': [0.1, 1.0, 10.0],
                        'classifier__kernel': ['rbf', 'linear'],
                        'classifier__gamma': ['scale', 'auto']
                    }
                },
                'Naive Bayes': {
                    'model': GaussianNB(),
                    'pipeline': Pipeline([
                        ('scaler', StandardScaler()),
                        ('classifier', GaussianNB())
                    ]),
                    'params': {
                        'classifier__var_smoothing': [1e-9, 1e-8, 1e-7]
                    }
                }
            }
        else:
            # Regression models
            return {
                'Linear Regression': {
                    'model': LinearRegression(),
                    'pipeline': Pipeline([
                        ('scaler', StandardScaler()),
                        ('regressor', LinearRegression())
                    ]),
                    'params': {}
                },
                'Ridge Regression': {
                    'model': Ridge(random_state=42),
                    'pipeline': Pipeline([
                        ('scaler', StandardScaler()),
                        ('regressor', Ridge(random_state=42))
                    ]),
                    'params': {
                        'regressor__alpha': [0.1, 1.0, 10.0]
                    }
                },
                'Lasso Regression': {
                    'model': Lasso(random_state=42),
                    'pipeline': Pipeline([
                        ('scaler', StandardScaler()),
                        ('regressor', Lasso(random_state=42))
                    ]),
                    'params': {
                        'regressor__alpha': [0.1, 1.0, 10.0]
                    }
                },
                'Random Forest': {
                    'model': RandomForestRegressor(random_state=42),
                    'pipeline': Pipeline([
                        ('scaler', StandardScaler()),
                        ('regressor', RandomForestRegressor(random_state=42))
                    ]),
                    'params': {
                        'regressor__n_estimators': [50, 100, 200],
                        'regressor__max_depth': [None, 10, 20],
                        'regressor__min_samples_split': [2, 5, 10]
                    }
                },
                'Gradient Boosting': {
                    'model': GradientBoostingRegressor(random_state=42),
                    'pipeline': Pipeline([
                        ('scaler', StandardScaler()),
                        ('regressor', GradientBoostingRegressor(random_state=42))
                    ]),
                    'params': {
                        'regressor__n_estimators': [50, 100],
                        'regressor__learning_rate': [0.01, 0.1],
                        'regressor__max_depth': [3, 5]
                    }
                },
                'SVR': {
                    'model': SVR(),
                    'pipeline': Pipeline([
                        ('scaler', StandardScaler()),
                        ('regressor', SVR())
                    ]),
                    'params': {
                        'regressor__C': [0.1, 1.0, 10.0],
                        'regressor__kernel': ['rbf', 'linear'],
                        'regressor__gamma': ['scale', 'auto']
                    }
                }
            }
    
    def train_with_gridsearch(self, X_train, y_train, X_test, y_test, cv_folds: int = 5) -> Dict[str, Any]:
        results = {}
        best_score = -np.inf
        best_model_name = None
        
        for model_name, model_info in self.models.items():
            print(f"Treinando {model_name}...")
            
            try:
                if not model_info['params']:
                    model_info['pipeline'].fit(X_train, y_train)
                    best_estimator = model_info['pipeline']
                    best_params = {}
                    
                    cv_scores = cross_val_score(
                        best_estimator, X_train, y_train, cv=cv_folds,
                        scoring='accuracy' if self.problem_type == ProblemType.CLASSIFICATION else 'r2'
                    )
                    
                else:
                    grid_search = GridSearchCV(
                        model_info['pipeline'],
                        model_info['params'],
                        cv=cv_folds,
                        scoring='accuracy' if self.problem_type == ProblemType.CLASSIFICATION else 'r2',
                        n_jobs=-1,
                        verbose=1
                    )
                    
                    grid_search.fit(X_train, y_train)
                    best_estimator = grid_search.best_estimator_
                    best_params = grid_search.best_params_
                    cv_scores = grid_search.cv_results_['mean_test_score']
                
                y_pred = best_estimator.predict(X_test)
                metrics = self._calculate_metrics(y_test, y_pred)
                
                metrics['cv_mean'] = cv_scores.mean() if len(cv_scores) > 0 else None
                metrics['cv_std'] = cv_scores.std() if len(cv_scores) > 0 else None
                
                main_metric = metrics.get('accuracy' if self.problem_type == ProblemType.CLASSIFICATION else 'r2', 0)
                if main_metric > best_score:
                    best_score = main_metric
                    best_model_name = model_name
                
                results[model_name] = {
                    'model': best_estimator,
                    'metrics': metrics,
                    'best_params': best_params,
                    'predictions': y_pred.tolist() if hasattr(y_pred, 'tolist') else y_pred
                }
                
                print(f"{model_name} concluído. Métricas: {metrics}")
                
            except Exception as e:
                print(f"Erro ao treinar {model_name}: {e}")
                results[model_name] = {
                    'model': None,
                    'error': str(e),
                    'metrics': {},
                    'best_params': {}
                }
        
        self.results = results
        self.best_model_name = best_model_name
        
        return results
    
    def _calculate_metrics(self, y_true, y_pred) -> Dict[str, float]:
        metrics = {}
        
        if self.problem_type == ProblemType.CLASSIFICATION:
            metrics['accuracy'] = accuracy_score(y_true, y_pred)
            metrics['precision'] = precision_score(y_true, y_pred, average='weighted', zero_division=0)
            metrics['recall'] = recall_score(y_true, y_pred, average='weighted', zero_division=0)
            metrics['f1_score'] = f1_score(y_true, y_pred, average='weighted', zero_division=0)
            
            cm = confusion_matrix(y_true, y_pred)
            metrics['confusion_matrix'] = cm.tolist()
            
        else:
            metrics['mse'] = mean_squared_error(y_true, y_pred)
            metrics['rmse'] = np.sqrt(metrics['mse'])
            metrics['mae'] = mean_absolute_error(y_true, y_pred)
            metrics['r2'] = r2_score(y_true, y_pred)
        
        return metrics
    
    def get_best_model(self):
        if hasattr(self, 'best_model_name') and self.best_model_name:
            return self.results[self.best_model_name]['model']
        return None
    
    def save_results(self, job_id: str) -> str:
        from backend.app.utils.file_handler import MODELS_DIR
        
        job_dir = MODELS_DIR / job_id
        job_dir.mkdir(exist_ok=True)
        
        serializable_results = {}
        for model_name, result in self.results.items():
            serializable_results[model_name] = {
                'metrics': result.get('metrics', {}),
                'best_params': result.get('best_params', {}),
                'error': result.get('error', None)
            }
        
        results_path = job_dir / 'training_results.json'
        with open(results_path, 'w') as f:
            json.dump({
                'problem_type': self.problem_type.value,
                'best_model': self.best_model_name if hasattr(self, 'best_model_name') else None,
                'results': serializable_results
            }, f, indent=2)
        
        return str(results_path)