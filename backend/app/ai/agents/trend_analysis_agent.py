import structlog
import json
from typing import Dict, Any
from backend.app.ai.services.groq_llm_service import groq_llm_service

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are an expert Trend Analysis Agent.
Your job is to read raw numerical lab trends and detect improvements or deteriorations over time.
Provide simple educational context for each trend. Do NOT diagnose.

Return ONLY a valid JSON object:
{
  "trend_insights": [
    {
      "parameter": "Name",
      "direction": "Increasing/Decreasing/Stable",
      "clinical_context": "Educational explanation of what this trend typically means."
    }
  ]
}
DO NOT output any markdown blocks (like ```json).
"""

class TrendAnalysisAgent:
    """Analyzes calculated trends for clinical context."""

    async def run(self, raw_trends: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("TrendAnalysisAgent started")
        
        if not raw_trends:
            return {"trend_insights": []}
            
        trends_json = json.dumps(raw_trends, indent=2)
        prompt = f"Raw Trends:\n{trends_json}\nGenerate context. ONLY valid JSON."
        
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
            logger.error("TrendAnalysisAgent error", error=str(e))
            return {"trend_insights": []}
