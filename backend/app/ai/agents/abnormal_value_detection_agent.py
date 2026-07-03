import structlog
import json
from typing import List, Dict, Any
from backend.app.ai.services.groq_llm_service import groq_llm_service

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are an expert Clinical Abnormal Value Detection Agent.
Your job is to analyze a list of evaluated medical report parameters and identify the critical or abnormal findings.

Rules:
1. Identify any parameter marked as LOW, HIGH, or CRITICAL.
2. Formulate a brief, objective clinical finding for each.
3. Determine if the overall report contains potentially critical findings that warrant immediate medical review.

You must return a valid JSON object matching this structure:
{
  "abnormal_findings": ["string", "string"],
  "has_critical_values": boolean
}

DO NOT output any markdown blocks (like ```json), just output the raw JSON object.
"""

class AbnormalValueDetectionAgent:
    """Identifies and highlights abnormal and critical values."""

    async def run(self, evaluated_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        logger.info("AbnormalValueDetectionAgent started")
        
        items_json = json.dumps(evaluated_items, indent=2)
        
        prompt = f"""Evaluated Parameters:
---
{items_json}
---

Identify the abnormal values. Remember: ONLY output a valid JSON object.
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
            
            data = json.loads(result)
            return data
            
        except json.JSONDecodeError as e:
            logger.error("AbnormalValueDetectionAgent JSON parse error", error=str(e), response=result)
            return {"abnormal_findings": ["Failed to analyze abnormal findings."], "has_critical_values": False}
        except Exception as e:
            logger.error("AbnormalValueDetectionAgent error", error=str(e))
            return {"abnormal_findings": ["Error analyzing abnormal findings."], "has_critical_values": False}
