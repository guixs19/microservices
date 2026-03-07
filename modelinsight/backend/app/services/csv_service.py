# backend/app/services/csv_service.py
import pandas as pd
import numpy as np
from typing import Tuple, List, Optional
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.app.schemas.data_schema import ProblemType
from backend.app.utils.file_handler import load_csv

class CSVService:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None
        self.label_encoders = {}
        
    def load_and_validate(self) -> Tuple[bool, str]:
        self.df = load_csv(self.file_path)
        
        if self.df is None:
            return False, "Erro ao carregar arquivo"
        
        if self.df.empty:
            return False, "Arquivo vazio"
        
        if len(self.df.columns) < 2:
            return False, "Arquivo precisa ter pelo menos 2 colunas"
        
        return True, "Arquivo válido"
    
    def get_basic_info(self) -> dict:
        if self.df is None:
            return {}
        
        return {
            "columns": list(self.df.columns),
            "row_count": len(self.df),
            "column_types": {col: str(dtype) for col, dtype in self.df.dtypes.items()},
            "missing_values": self.df.isnull().sum().to_dict(),
            "sample_data": self.df.head(5).to_dict('records')
        }
    
    def prepare_data(self, target_column: str, problem_type: ProblemType, test_size: float = 0.2):
        if self.df is None:
            raise ValueError("DataFrame não carregado")
        
        if target_column not in self.df.columns:
            raise ValueError(f"Coluna alvo '{target_column}' não encontrada")
        
        X = self.df.drop(columns=[target_column])
        y = self.df[target_column]
        
        X = self._handle_missing_values(X)
        X = self._encode_categorical_features(X)
        
        if problem_type == ProblemType.CLASSIFICATION:
            y = self._encode_target(y)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        return X_train, X_test, y_train, y_test
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        df_clean = df.copy()
        
        for col in df_clean.columns:
            if df_clean[col].isnull().any():
                if df_clean[col].dtype in ['int64', 'float64']:
                    df_clean[col].fillna(df_clean[col].median(), inplace=True)
                else:
                    df_clean[col].fillna(df_clean[col].mode()[0] if not df_clean[col].mode().empty else "unknown", inplace=True)
        
        return df_clean
    
    def _encode_categorical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        if len(categorical_cols) > 0:
            df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)
        
        return df
    
    def _encode_target(self, y: pd.Series) -> pd.Series:
        if y.dtype == 'object':
            le = LabelEncoder()
            y_encoded = le.fit_transform(y)
            self.label_encoders['target'] = le
            return pd.Series(y_encoded, index=y.index)
        return y