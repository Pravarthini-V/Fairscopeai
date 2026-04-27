# correction_agent.py
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any

class CorrectionAgent:
    def __init__(self):
        self.correction_methods = ["reweight", "resample", "transform"]
    
    def correct_bias(self, df: pd.DataFrame, correction_type: str = "reset") -> Tuple[pd.DataFrame, bool]:
        """
        Correct biased data - asks user before resetting
        Returns: (corrected_df, success_flag)
        """
        
        # In production, this would ask user through API
        # For now, simulate user response
        user_approved = self._ask_user_permission()
        
        if not user_approved:
            return df, False
        
        if correction_type == "reset":
            return self._reset_data(df), True
        elif correction_type == "reweight":
            return self._reweight_samples(df), True
        elif correction_type == "resample":
            return self._resample_data(df), True
        else:
            return df, False
    
    def _ask_user_permission(self) -> bool:
        """Ask user permission to reset/correct data"""
        # In API context, this will be handled via frontend
        # Return True for simulation
        return True
    
    def _reset_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Reset data by removing bias"""
        df_corrected = df.copy()
        
        # Find sensitive columns and rebalance
        for col in df.columns:
            if df[col].dtype == 'object':
                # Balance categorical columns
                value_counts = df[col].value_counts()
                if len(value_counts) > 1 and value_counts.max() / value_counts.min() > 2:
                    # Resample minority classes
                    target_size = int(value_counts.mean())
                    balanced_df = []
                    for val in value_counts.index:
                        subset = df[df[col] == val]
                        if len(subset) > target_size:
                            subset = subset.sample(n=target_size, random_state=42)
                        balanced_df.append(subset)
                    df_corrected = pd.concat(balanced_df, ignore_index=True)
        
        return df_corrected
    
    def _reweight_samples(self, df: pd.DataFrame) -> pd.DataFrame:
        """Reweight samples to reduce bias"""
        df_corrected = df.copy()
        
        # Add weight column
        weights = np.ones(len(df))
        
        for col in df.columns:
            if df[col].dtype == 'object':
                value_counts = df[col].value_counts()
                target_prob = 1.0 / len(value_counts)
                for val in value_counts.index:
                    mask = df[col] == val
                    current_prob = value_counts[val] / len(df)
                    weights[mask] = target_prob / current_prob
        
        df_corrected['_fairness_weight'] = weights / weights.sum()
        return df_corrected
    
    def _resample_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Resample data using SMOTE-like technique"""
        df_corrected = df.copy()
        
        # Simple oversampling of minority classes
        for col in df.columns:
            if df[col].dtype == 'object':
                value_counts = df[col].value_counts()
                max_count = value_counts.max()
                
                balanced_dfs = []
                for val in value_counts.index:
                    subset = df[df[col] == val]
                    if len(subset) < max_count:
                        # Oversample with replacement
                        subset = subset.sample(n=max_count, replace=True, random_state=42)
                    balanced_dfs.append(subset)
                
                df_corrected = pd.concat(balanced_dfs, ignore_index=True)
                break  # Balance only first sensitive column
        
        return df_corrected