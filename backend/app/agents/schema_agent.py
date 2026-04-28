import pandas as pd
from typing import List, Dict
from app.service.gemini_service import GeminiService

class SchemaAgent:
    def __init__(self):
        self.gemini = GeminiService()

    def retrieve_tables(self, df: pd.DataFrame) -> List[Dict]:
        """Auto-detect table names using LLM"""
        columns = df.columns.tolist()
        column_info = [f"{col} ({df[col].dtype})" for col in columns]
        
        prompt = f"""You are a database schema expert. Given these columns, suggest 2-3 logical table names.
        
Columns: {column_info}
Sample: {df.head(2).to_dict()}

Return ONLY table names as comma-separated list:"""

        try:
            response = self.gemini.generate_response(prompt)
            tables = [t.strip() for t in response.split(',')]
            return [{
                "table_name": t,
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": df.columns.tolist()
            } for t in tables]
        except:
            return self._fallback_tables(df)

    def _fallback_tables(self, df: pd.DataFrame) -> List[Dict]:
        """Rule-based table name detection"""
        cols_lower = [c.lower() for c in df.columns]
        
        if any('loan' in c for c in cols_lower):
            name = "loan_applications"
        elif any('patient' in c for c in cols_lower):
            name = "patient_records"
        elif any('employee' in c for c in cols_lower):
            name = "employee_data"
        elif any('student' in c for c in cols_lower):
            name = "student_records"
        else:
            name = "main_dataset"
            
        return [{
            "table_name": name,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist()
        }]