import pandas as pd
from typing import Dict, List
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class ContextAgent:
    def __init__(self):
        # Configure Gemini
        genai.configure(api_key="AIzaSyB5bKDrUiZRYV8IyEOBE3aLp2tZoJ9Ow7I")
        self.model = genai.GenerativeModel('gemini-pro')
        
        self.sensitive_patterns = {
            "race": ["race", "ethnicity", "color"],
            "gender": ["gender", "sex"],
            "age": ["age", "dob", "birth"],
            "religion": ["religion", "faith"],
            "disability": ["disability", "handicap"],
            "income": ["income", "salary", "wage"]
        }
    
    def identify_domain(self, df: pd.DataFrame) -> str:
        """Identify domain using Gemini API"""
        columns = df.columns.tolist()
        sample_data = df.head(3).to_dict()
        
        prompt = f"""Given these column names and sample data, identify the business domain (finance, healthcare, employment, education, or general):

Columns: {', '.join(columns)}
Sample data: {sample_data}

Domain (single word):"""
        
        try:
            response = self.model.generate_content(prompt)
            domain = response.text.strip().lower()
            
            # Validate domain
            valid_domains = ["finance", "healthcare", "employment", "education", "general"]
            if domain in valid_domains:
                return domain
            
            return "general"
        
        except Exception as e:
            print(f"Gemini API error: {e}, falling back to rule-based")
            return self._fallback_domain(columns)
    
    def _fallback_domain(self, columns: List[str]) -> str:
        """Fallback domain detection"""
        column_str = " ".join(columns).lower()
        
        domain_keywords = {
            "finance": ["loan", "credit", "income", "bank"],
            "healthcare": ["diagnosis", "patient", "medical", "treatment"],
            "employment": ["salary", "employee", "hire", "job"],
            "education": ["grade", "student", "course", "school"]
        }
        
        scores = {}
        for domain, keywords in domain_keywords.items():
            score = sum(1 for kw in keywords if kw in column_str)
            if score > 0:
                scores[domain] = score
        
        return max(scores, key=scores.get) if scores else "general"
    
    def get_sensitive_columns(self, df: pd.DataFrame) -> List[str]:
        """Use Gemini to identify sensitive columns"""
        columns = df.columns.tolist()
        
        prompt = f"""From these column names, identify which are sensitive/protected attributes (like race, gender, age, religion, disability, income):
Columns: {', '.join(columns)}

Return only the sensitive column names as a comma-separated list:"""
        
        try:
            response = self.model.generate_content(prompt)
            sensitive_text = response.text.strip()
            sensitive_cols = [col.strip() for col in sensitive_text.split(',')]
            
            # Only return columns that actually exist
            return [col for col in sensitive_cols if col in columns]
        
        except Exception as e:
            print(f"Gemini API error: {e}, falling back to pattern matching")
            return self._fallback_sensitive(columns)
    
    def _fallback_sensitive(self, columns: List[str]) -> List[str]:
        """Fallback sensitive column detection"""
        sensitive_cols = []
        for col in columns:
            col_lower = col.lower()
            for category, keywords in self.sensitive_patterns.items():
                if any(keyword in col_lower for keyword in keywords):
                    sensitive_cols.append(col)
                    break
        return sensitive_cols