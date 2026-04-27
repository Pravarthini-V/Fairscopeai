from typing import Dict, Any
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class ExplanationAgent:
    def __init__(self):
        # Configure Gemini
        genai.configure(api_key=os.getenv("AIzaSyBU7Za9jEnmnxImA3iXYVoD-lI-rO8Phig"))
        self.model = genai.GenerativeModel('gemini-pro')
    
    def generate_explanation(self, fairness_result: Dict[str, Any], rag_insights: Dict[str, Any] = None) -> str:
        """Generate explanation using Gemini API"""
        
        # Build context
        context = f"""
Fairness Analysis Results:
- Overall Score: {fairness_result['score']:.2f}
- Is Fair: {fairness_result['is_fair']}
- Sensitive Attributes: {list(fairness_result['metrics'].keys())}

Detailed Metrics:
{self._format_metrics(fairness_result['metrics'])}

RAG Insights (if available):
{self._format_rag(rag_insights) if rag_insights else 'None'}
"""
        
        if fairness_result['is_fair']:
            prompt = f"""You are a fairness explainer AI. The fairness check PASSED. Provide a clear, encouraging explanation:

{context}

Your response (2-3 sentences explaining why it's fair and what this means):"""
        else:
            prompt = f"""You are a fairness explainer AI. The fairness check FAILED. Provide a clear, actionable explanation:

{context}

Your response (include: why it failed, which attributes caused issues, and 2-3 specific recommendations to fix):"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        
        except Exception as e:
            print(f"Gemini API error: {e}, using fallback")
            return self._fallback_explanation(fairness_result)
    
    def _format_metrics(self, metrics: Dict) -> str:
        """Format metrics for prompt"""
        formatted = ""
        for attr, data in metrics.items():
            formatted += f"- {attr}: score={data['score']:.2f}, disparity={data['disparity']:.2f}\n"
        return formatted
    
    def _format_rag(self, rag_insights: Dict) -> str:
        """Format RAG insights for prompt"""
        if not rag_insights:
            return "None"
        
        text = f"- Similar sessions found: {rag_insights.get('similar_sessions_count', 0)}\n"
        text += f"- Bias patterns found: {rag_insights.get('bias_patterns_found', 0)}\n"
        
        if rag_insights.get('historical_context'):
            text += "- Historical patterns available\n"
        
        return text
    
    def _fallback_explanation(self, fairness_result: Dict[str, Any]) -> str:
        """Fallback explanation if Gemini fails"""
        if fairness_result["is_fair"]:
            return f"""✅ Fairness Check Passed! Overall fairness score: {fairness_result['score']:.2f}

The dataset shows balanced outcomes across all protected attributes. No immediate action required."""
        else:
            failed_attrs = [attr for attr, data in fairness_result["metrics"].items() if not data.get('is_fair', False)]
            return f"""⚠️ Fairness Check Failed! Overall fairness score: {fairness_result['score']:.2f}

Issues detected with: {', '.join(failed_attrs)}

Recommendations:
1. Apply correction algorithms to rebalance data
2. Review data collection process for bias
3. Consider resampling minority groups"""