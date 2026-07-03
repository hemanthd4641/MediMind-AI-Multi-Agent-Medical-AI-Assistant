import structlog
import json
from typing import Dict, Any, List
from backend.app.ai.services.groq_llm_service import groq_llm_service

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are an expert Risk Insight Agent.
Analyze the patient's lifestyle, chronic conditions, medication history, and recent trends to generate personalized, educational health insights.
Never diagnose. State clearly that these are general observations.

Return ONLY a valid JSON object:
{
  "risk_insights": [
    {
      "title": "Short Title (e.g. Cardiovascular Risk Factor)",
      "description": "Detailed educational explanation.",
      "category": "RISK"
    }
  ]
}
DO NOT output any markdown blocks (like ```json).
"""

class RiskInsightAgent:
    """Generates health risk insights based on history."""

    async def run(self, profile: Any, trends: Dict[str, Any], history: List[str]) -> Dict[str, Any]:
        logger.info("RiskInsightAgent started")
        
        prompt = f"""
Age: {profile.age if profile else 'Unknown'}
Gender: {profile.gender if profile else 'Unknown'}
Chronic Conditions: {profile.chronic_conditions if profile else 'None'}
Allergies: {profile.allergies if profile else 'None'}
Medication History: {', '.join(history) if history else 'None'}
Trends: {json.dumps(trends)}

Generate risk insights. ONLY valid JSON.
"""
        try:
            result = await groq_llm_service.generate(prompt, system_prompt=SYSTEM_PROMPT)
            
            result = result.strip()
            if result.startswith("```json"):
                result = result[7:]
            if result.startswith("```"):
                result = result[3:]
            if result.endswith("```"):
                result = result[:-3]
            result = result.strip()
            
            return json.loads(result)
        except Exception as e:
            logger.error("RiskInsightAgent error", error=str(e))
            return {"risk_insights": []}
