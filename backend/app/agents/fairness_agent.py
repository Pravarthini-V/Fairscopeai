# fairness_agent.py
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from sklearn.metrics import confusion_matrix

class FairnessAgent:
    def __init__(self):
        self.fairness_threshold = 0.8
        
    def calculate_fairness(self, df: pd.DataFrame, sensitive_attrs: List[str]) -> Dict[str, Any]:
        """Calculate fairness metrics using pandas and numpy"""
        
        # Find target column (assuming last column or detect)
        target_col = df.columns[-1]
        
        fairness_metrics = {}
        
        for attr in sensitive_attrs:
            if attr in df.columns:
                metrics = self._calculate_attribute_fairness(df, attr, target_col)
                fairness_metrics[attr] = metrics
        
        # Aggregate fairness score
        scores = [metrics["score"] for metrics in fairness_metrics.values()]
        overall_score = np.mean(scores) if scores else 1.0
        
        is_fair = overall_score >= self.fairness_threshold
        
        return {
            "score": overall_score,
            "is_fair": is_fair,
            "metrics": fairness_metrics,
            "target_column": target_col,
            "sensitive_attributes": sensitive_attrs
        }
    
    def _calculate_attribute_fairness(self, df: pd.DataFrame, attr: str, target: str) -> Dict[str, Any]:
        """Calculate fairness for a single attribute"""
        groups = df[attr].unique()
        
        if len(groups) < 2:
            return {"score": 1.0, "error": "Only one group found"}
        
        # Demographic parity
        group_outcomes = {}
        for group in groups:
            group_data = df[df[attr] == group]
            if len(group_data) > 0 and target in group_data.columns:
                # If target is numeric, use mean; if binary, use positive rate
                if df[target].dtype in ['int64', 'float64']:
                    outcome_rate = group_data[target].mean()
                else:
                    outcome_rate = (group_data[target] == group_data[target].mode()[0]).mean()
                group_outcomes[group] = outcome_rate
        
        if len(group_outcomes) < 2:
            return {"score": 1.0}
        
        # Calculate disparity (ratio of min to max)
        rates = list(group_outcomes.values())
        min_rate = min(rates)
        max_rate = max(rates)
        
        if max_rate == 0:
            disparity = 1.0
        else:
            disparity = min_rate / max_rate
        
        # Calculate statistical parity difference
        parity_diff = abs(rates[0] - rates[1]) if len(rates) >= 2 else 0
        
        return {
            "score": disparity,
            "disparity": disparity,
            "parity_difference": parity_diff,
            "group_outcomes": group_outcomes,
            "is_fair": disparity >= self.fairness_threshold
        }
    
    def demographic_parity(self, df: pd.DataFrame, protected_attr: str, target: str) -> float:
        """Calculate demographic parity metric"""
        groups = df[protected_attr].unique()
        rates = []
        
        for group in groups:
            group_df = df[df[protected_attr] == group]
            if len(group_df) > 0:
                rate = group_df[target].mean() if df[target].dtype in ['int64', 'float64'] else (group_df[target] == 1).mean()
                rates.append(rate)
        
        if len(rates) >= 2:
            return abs(rates[0] - rates[1])
        return 0.0