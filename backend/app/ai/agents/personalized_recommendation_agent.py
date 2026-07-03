import structlog
import json
from typing import Dict, Any, List
from backend.app.ai.services.groq_llm_service import groq_llm_service

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are an expert Personalized Recommendation Agent.
Provide general, educational recommendations based on the patient's insights and timeline.
Always remind the user to consult their doctor. NEVER prescribe or treat.

Return ONLY a valid JSON object:
{
  "recommendations": [
    {
      "title": "Short Title",
      "description": "Educational recommendation (e.g. Discuss declining hemoglobin with your doctor).",
      "category": "RECOMMENDATION"
    }
  ]
}
DO NOT output any markdown blocks (like ```json).
"""

class PersonalizedRecommendationAgent:
    """Generates safe recommendations."""

    async def run(self, insights: List[Dict[str, Any]]) -> Dict[str, Any]:
        logger.info("PersonalizedRecommendationAgent started")
        
        if not insights:
            return {"recommendations": []}
            
        ins_json = json.dumps(insights, indent=2)
        prompt = f"Insights:\n{ins_json}\nGenerate recommendations. ONLY valid JSON."
        
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
            logger.error("PersonalizedRecommendationAgent error", error=str(e))
            return {"recommendations": []}
