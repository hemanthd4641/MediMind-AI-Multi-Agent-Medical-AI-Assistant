import structlog
import json
from typing import List, Dict, Any
from backend.app.ai.services.groq_llm_service import groq_llm_service

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are an expert Contraindication Agent.
Your job is to evaluate if any newly prescribed medicines are contraindicated based on the patient's medical history and chronic conditions.

Identify educational warnings. Do NOT provide medical advice.

You must return a valid JSON object matching this structure:
{
  "contraindications": [
    {
      "medicine": "Name",
      "condition": "Condition Name",
      "warning": "Educational warning..."
    }
  ]
}

If no contraindications are found, return {"contraindications": []}.
DO NOT output any markdown blocks (like ```json), just output the raw JSON object.
"""

class ContraindicationAgent:
    """Detects potential contraindications."""

    async def run(self, new_medicines: List[str], chronic_conditions: List[str]) -> Dict[str, Any]:
        logger.info("ContraindicationAgent started")
        
        if not new_medicines or not chronic_conditions:
            return {"contraindications": []}
            
        prompt = f"""
New Prescribed Medicines: {', '.join(new_medicines)}
Patient Chronic Conditions: {', '.join(chronic_conditions)}

Identify potential contraindications. Remember: ONLY output a valid JSON object.
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
            logger.error("ContraindicationAgent JSON parse error", error=str(e), response=result)
            return {"contraindications": []}
        except Exception as e:
            logger.error("ContraindicationAgent error", error=str(e))
            return {"contraindications": []}
