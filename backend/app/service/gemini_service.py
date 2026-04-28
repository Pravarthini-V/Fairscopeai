import google.generativeai as genai
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class GeminiService:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def generate_response(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate response from Gemini"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": temperature,
                    "top_p": 0.95,
                    "top_k": 40,
                }
            )
            return response.text.strip()
        except Exception as e:
            print(f"Gemini API error: {e}")
            return ""
    
    def analyze_fairness_text(self, fairness_data: Dict[str, Any]) -> str:
        """Specialized fairness analysis with Gemini"""
        prompt = f"""You are a fairness auditor. Analyze this fairness report and provide a concise executive summary:

Report:
{fairness_data}

Provide: 1) Overall assessment, 2) Key issues, 3) Top 2 recommendations"""
        
        return self.generate_response(prompt, temperature=0.3)