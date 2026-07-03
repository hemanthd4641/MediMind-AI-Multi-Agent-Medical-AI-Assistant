import structlog
import json
from typing import Dict, Any
from backend.app.ai.services.groq_llm_service import groq_llm_service

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are an expert Health Comparison Agent.
Read the comparison deltas between recent and previous reports/consultations.
Highlight meaningful changes in simple language.

Return ONLY a valid JSON object:
{
  "comparison_insights": [
    {
      "title": "Short Title",
      "description": "Explanation of the change.",
      "category": "COMPARISON"
    }
  ]
}
DO NOT output any markdown blocks (like ```json).
"""

class ComparisonAgent:
    """Highlights meaningful changes between two events."""

    async def run(self, comparison_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("ComparisonAgent started")
        
        if not comparison_data.get("reports_comparison", {}).get("comparable", False) and not comparison_data.get("consultations_comparison", {}).get("comparable", False):
            return {"comparison_insights": []}
            
        comp_json = json.dumps(comparison_data, indent=2)
        prompt = f"Comparison Data:\n{comp_json}\nHighlight changes. ONLY valid JSON."
        
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
            logger.error("ComparisonAgent error", error=str(e))
            return {"comparison_insights": []}
