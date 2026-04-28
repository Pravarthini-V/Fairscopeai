import pandas as pd
from typing import List
from app.service.gemini_service import GeminiService

class ContextAgent:
    def __init__(self):
        self.gemini = GeminiService()
        
        self.sensitive_patterns = {
            "race": ["race", "ethnicity", "color", "nationality", "origin"],
            "gender": ["gender", "sex", "male", "female"],
            "age": ["age", "dob", "birth", "year"],
            "religion": ["religion", "faith", "belief"],
            "disability": ["disability", "handicap", "disabled"],
            "income": ["income", "salary", "wage", "earnings"],
            "marital_status": ["marital", "married", "spouse"],
            "education": ["education", "degree", "qualification"],
            "location": ["zip", "postal", "address", "city", "state", "country"]
        }

    def identify_domain(self, df: pd.DataFrame) -> str:
        """Identify domain using LLM with fallback"""
        columns = df.columns.tolist()
        sample_data = df.head(3).to_dict()

        prompt = f"""Given these column names and sample data, identify the business domain.
Options: finance, healthcare, employment, education, general

Columns: {columns}
Sample Data: {sample_data}

Return ONLY one word:"""

        try:
            domain = self.gemini.generate_response(prompt).lower().strip()
            valid_domains = ["finance", "healthcare", "employment", "education", "general"]
            return domain if domain in valid_domains else self._fallback_domain(columns)
        except:
            return self._fallback_domain(columns)

    def get_sensitive_columns(self, df: pd.DataFrame) -> List[str]:
        """Identify sensitive columns using LLM with fallback"""
        columns = df.columns.tolist()
        
        prompt = f"""From these column names, identify which are sensitive/protected attributes 
(like race, gender, age, religion, disability, income, marital status).
Return ONLY the column names as comma-separated list. If none, return "none".

Columns: {columns}"""

        try:
            response = self.gemini.generate_response(prompt)
            if response.lower() == "none":
                return self._fallback_sensitive(columns)
            sensitive_cols = [col.strip() for col in response.split(',')]
            return [col for col in sensitive_cols if col in columns]
        except:
            return self._fallback_sensitive(columns)

    def _fallback_domain(self, columns: List[str]) -> str:
        """Rule-based domain detection"""
        column_str = " ".join(columns).lower()
        
        domain_keywords = {
            "finance": ["loan", "credit", "income", "bank", "salary", "wage", "approved", "interest"],
            "healthcare": ["diagnosis", "patient", "medical", "treatment", "hospital"],
            "employment": ["salary", "employee", "hire", "job", "department", "promotion"],
            "education": ["grade", "student", "course", "school", "gpa", "attendance"]
        }
        
        scores = {}
        for domain, keywords in domain_keywords.items():
            score = sum(1 for kw in keywords if kw in column_str)
            if score > 0:
                scores[domain] = score
        
        return max(scores, key=scores.get) if scores else "general"

    def _fallback_sensitive(self, columns: List[str]) -> List[str]:
        """Pattern-based sensitive column detection"""
        sensitive_cols = []
        for col in columns:
            col_lower = col.lower()
            for category, keywords in self.sensitive_patterns.items():
                if any(keyword in col_lower for keyword in keywords):
                    sensitive_cols.append(col)
                    break
        return sensitive_cols