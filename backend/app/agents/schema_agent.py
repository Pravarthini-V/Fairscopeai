import pandas as pd
from typing import List, Dict
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class SchemaAgent:
    def __init__(self):
        # Configure Gemini
        genai.configure(api_key=os.getenv("AIzaSyAA7LoJXfeHflHKQ1wjE3nqJExKst6-rFY"))
        self.model = genai.GenerativeModel('gemini-pro')
        
        # K-shot examples for prompt-based training
        self.k_shot_examples = [
            {"columns": "loan_amount,income,race,gender", "tables": "loan_applicants, credit_history"},
            {"columns": "diagnosis,age,ethnicity,blood_pressure", "tables": "patients, medical_records"},
            {"columns": "salary,department,religion,experience", "tables": "employees, job_history"},
            {"columns": "score,grade,race,attendance", "tables": "students, academic_records"}
        ]
    
    def extract_tables(self, df: pd.DataFrame) -> List[str]:
        """Extract table names using Gemini API"""
        columns = df.columns.tolist()
        
        # Build prompt with K-shot examples
        prompt = self._build_prompt(columns)
        
        try:
            # Call Gemini API
            response = self.model.generate_content(prompt)
            tables_text = response.text.strip()
            
            # Parse response (expecting comma-separated table names)
            tables = [t.strip() for t in tables_text.split(',')]
            return tables[:5]  # Limit to 5 tables
        
        except Exception as e:
            print(f"Gemini API error: {e}, falling back to rule-based")
            return self._fallback_extraction(columns)
    
    def _build_prompt(self, columns: List[str]) -> str:
        """Build K-shot prompt for Gemini"""
        examples = ""
        for ex in self.k_shot_examples[:3]:
            examples += f"Input columns: {ex['columns']}\nSuggested tables: {ex['tables']}\n\n"
        
        prompt = f"""You are a database schema expert. Given these column names from a dataset, suggest 2-3 appropriate table names that would organize this data.

{examples}
Input columns: {', '.join(columns)}
Suggested tables:"""
        
        return prompt
    
    def _fallback_extraction(self, columns: List[str]) -> List[str]:
        """Fallback method if Gemini fails"""
        column_str = ",".join(columns).lower()
        
        patterns = {
            "loan": ["loan", "credit", "income"],
            "medical": ["diagnosis", "patient", "treatment"],
            "employee": ["salary", "employee", "job"],
            "student": ["grade", "student", "course"]
        }
        
        tables = []
        for table_name, keywords in patterns.items():
            if any(keyword in column_str for keyword in keywords):
                tables.append(table_name)
        
        return tables if tables else ["primary_data"]