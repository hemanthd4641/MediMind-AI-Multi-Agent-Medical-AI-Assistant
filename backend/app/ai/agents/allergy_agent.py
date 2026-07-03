import structlog
import json
from typing import List, Dict, Any
from backend.app.ai.services.groq_llm_service import groq_llm_service

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are an expert Allergy Detection Agent.
Your job is to compare a list of newly prescribed medicines with the patient's known allergies.

Identify any potential allergic reactions or cross-reactivities.
Provide educational warnings. Do NOT provide medical advice.

You must return a valid JSON object matching this structure:
{
  "allergy_warnings": [
    {
      "medicine": "Name",
      "allergen": "Known Allergy",
      "warning": "Educational warning about potential reaction..."
    }
  ]
}

If no allergy conflicts are found, return {"allergy_warnings": []}.
DO NOT output any markdown blocks (like ```json), just output the raw JSON object.
"""

class AllergyAgent:
    """Detects potential allergies based on patient profile."""

    async def run(self, new_medicines: List[str], allergies: List[str]) -> Dict[str, Any]:
        logger.info("AllergyAgent started")
        
        if not new_medicines or not allergies:
            return {"allergy_warnings": []}
            
        prompt = f"""
New Prescribed Medicines: {', '.join(new_medicines)}
Patient Allergies: {', '.join(allergies)}

Identify potential allergy conflicts. Remember: ONLY output a valid JSON object.
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
            logger.error("AllergyAgent JSON parse error", error=str(e), response=result)
            return {"allergy_warnings": []}
        except Exception as e:
            logger.error("AllergyAgent error", error=str(e))
            return {"allergy_warnings": []}
