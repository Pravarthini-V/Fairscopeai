# data_processor.py
import pandas as pd
import numpy as np
from typing import Tuple, List, Dict  # Add Dict here

class DataProcessor:
    @staticmethod
    def detect_column_types(df: pd.DataFrame) -> Dict:
        """Detect column types dynamically"""
        types = {
            "numeric": [],
            "categorical": [],
            "datetime": [],
            "other": []
        }
        
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                types["numeric"].append(col)
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                types["datetime"].append(col)
            elif pd.api.types.is_categorical_dtype(df[col]) or df[col].dtype == 'object':
                types["categorical"].append(col)
            else:
                types["other"].append(col)
        
        return types
    
    @staticmethod
    def normalize_data(df: pd.DataFrame) -> pd.DataFrame:
        """Normalize numeric columns"""
        df_normalized = df.copy()
        
        for col in df.select_dtypes(include=[np.number]).columns:
            min_val = df[col].min()
            max_val = df[col].max()
            if max_val > min_val:
                df_normalized[col] = (df[col] - min_val) / (max_val - min_val)
        
        return df_normalized
    
    @staticmethod
    def handle_missing_values(df: pd.DataFrame, strategy: str = "mean") -> pd.DataFrame:
        """Handle missing values dynamically"""
        df_clean = df.copy()
        
        for col in df.columns:
            if df[col].isnull().sum() > 0:
                if strategy == "mean" and pd.api.types.is_numeric_dtype(df[col]):
                    df_clean[col].fillna(df[col].mean(), inplace=True)
                elif strategy == "median" and pd.api.types.is_numeric_dtype(df[col]):
                    df_clean[col].fillna(df[col].median(), inplace=True)
                elif strategy == "mode":
                    df_clean[col].fillna(df[col].mode()[0] if len(df[col].mode()) > 0 else "unknown", inplace=True)
        
        return df_clean