from typing import Dict, Any
from app.service.gemini_service import GeminiService

class ExplanationAgent:
    def __init__(self):
        self.gemini = GeminiService()

    def generate_explanation(self, fairness_result: Dict[str, Any], rag_insights: Dict[str, Any] = None) -> str:
        """Generate AI explanation using LLM - NOT hardcoded"""
        
        context = f"""
Fairness Analysis Results:
- Overall Score: {fairness_result.get('score', 0):.2f} (Threshold: 0.80)
- Is Fair: {fairness_result.get('is_fair', False)}
- Sensitive Attributes: {list(fairness_result.get('metrics', {}).keys())}

Detailed Metrics:
{self._format_metrics(fairness_result.get('metrics', {}))}
"""

        if rag_insights:
            context += f"""
RAG Insights:
- Similar Sessions: {rag_insights.get('similar_sessions_found', 0)}
- Bias Patterns Found: {rag_insights.get('bias_patterns_found', 0)}
"""

        if fairness_result.get('is_fair'):
            prompt = f"""You are a fairness AI expert. The fairness check PASSED.
Explain why this is good and what it means in simple terms.

{context}

Provide a clear, encouraging 3-4 sentence explanation:"""
        else:
            prompt = f"""You are a fairness AI expert. The fairness check FAILED.
Explain the issues and provide specific, actionable recommendations.

{context}

Provide: 1) Why it failed, 2) Which attributes caused issues, 3) 3 specific recommendations:"""

        try:
            explanation = self.gemini.generate_response(prompt, temperature=0.5)
            if explanation:
                return explanation
        except:
            pass
        
        # Only use fallback if LLM fails
        return self._fallback_explanation(fairness_result)

    def generate_correction_explanation(self, original: Dict, corrected: Dict, method: str) -> str:
        """Generate explanation for correction"""
        prompt = f"""Explain how bias correction was applied to a dataset.
Original score: {original.get('score', 0):.2f}
New score: {corrected.get('score', 0):.2f}
Method: {method}

Explain in 2-3 sentences what was done and the improvement achieved:"""

        try:
            explanation = self.gemini.generate_response(prompt, temperature=0.5)
            if explanation:
                return explanation
        except:
            pass
        
        return f"Data corrected using {method}. Fairness score improved from {original.get('score', 0):.2f} to {corrected.get('score', 0):.2f}."

    def _format_metrics(self, metrics: Dict) -> str:
        """Format metrics for prompt"""
        formatted = ""
        for attr, data in metrics.items():
            if isinstance(data, dict):
                formatted += f"- {attr}: score={data.get('score', 0):.2f}, is_fair={data.get('is_fair', False)}\n"
            else:
                formatted += f"- {attr}: {data}\n"
        return formatted

    def _fallback_explanation(self, fairness_result: Dict[str, Any]) -> str:
        """Fallback only used when LLM completely fails"""
        if fairness_result.get("is_fair"):
            return f"✅ Fairness Check Passed! Score: {fairness_result.get('score', 0):.2f}. Dataset shows balanced outcomes across protected attributes."
        else:
            return f"⚠️ Fairness Check Failed! Score: {fairness_result.get('score', 0):.2f}. Review data collection and consider correction methods."