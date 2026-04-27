# user_memory.py
import pandas as pd
from typing import Dict
from datetime import datetime
import json

class UserMemory:
    def __init__(self):
        self.user_data: Dict[str, pd.DataFrame] = {}
        self.user_metadata: Dict[str, Dict] = {}
    
    def store_data(self, user_id: str, df: pd.DataFrame):
        """Store user data in memory"""
        self.user_data[user_id] = df
        self.user_metadata[user_id] = {
            "timestamp": datetime.now().isoformat(),
            "rows": len(df),
            "columns": df.columns.tolist()
        }
    
    def get_data(self, user_id: str) -> pd.DataFrame:
        """Retrieve user data"""
        return self.user_data.get(user_id, pd.DataFrame())
    
    def update_data(self, user_id: str, df: pd.DataFrame):
        """Update user data"""
        self.user_data[user_id] = df
        self.user_metadata[user_id]["updated_at"] = datetime.now().isoformat()
    
    def delete_data(self, user_id: str):
        """Delete user data"""
        if user_id in self.user_data:
            del self.user_data[user_id]
        if user_id in self.user_metadata:
            del self.user_metadata[user_id]
    
    def get_metadata(self, user_id: str) -> Dict:
        """Get user metadata"""
        return self.user_metadata.get(user_id, {})