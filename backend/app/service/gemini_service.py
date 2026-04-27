import google.generativeai as genai
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class GeminiService:
    def __init__(self):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-pro')
        self.chat = None
    
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
    
    def start_chat(self, system_prompt: str = None):
        """Start a chat session"""
        if system_prompt:
            self.chat = self.model.start_chat(history=[
                {"role": "user", "parts": [system_prompt]},
                {"role": "model", "parts": ["I understand. I'll help with fairness analysis."]}
            ])
        else:
            self.chat = self.model.start_chat()
        return self.chat
    
    def chat_response(self, message: str) -> str:
        """Send message in chat session"""
        if not self.chat:
            self.start_chat()
        
        response = self.chat.send_message(message)
        return response.text.strip()
    
    def analyze_fairness_text(self, fairness_data: Dict[str, Any]) -> str:
        """Specialized fairness analysis with Gemini"""
        prompt = f"""You are a fairness auditor. Analyze this fairness report and provide a concise executive summary:

Report:
{fairness_data}

Provide: 1) Overall assessment, 2) Key issues, 3) Top 2 recommendations"""
        
        return self.generate_response(prompt, temperature=0.3)