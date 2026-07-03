import structlog
import json
from typing import List, Dict, Any
from backend.app.ai.services.groq_llm_service import groq_llm_service

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are an expert Medication Schedule Agent.
Your job is to read a list of structured medicines and their frequency, and generate a daily schedule categorized by Morning, Afternoon, Evening, and Night.

You must return a valid JSON object matching this structure:
{
  "schedule": {
    "Morning": ["Medicine 1 (Instructions)", "Medicine 2 (Instructions)"],
    "Afternoon": [],
    "Evening": ["Medicine 1 (Instructions)"],
    "Night": []
  }
}

DO NOT output any markdown blocks (like ```json), just output the raw JSON object.
"""

class MedicationScheduleAgent:
    """Generates a structured daily medication schedule."""

    async def run(self, medicines: List[Dict[str, Any]]) -> Dict[str, Any]:
        logger.info("MedicationScheduleAgent started")
        
        if not medicines:
            return {"schedule": {"Morning": [], "Afternoon": [], "Evening": [], "Night": []}}
            
        meds_json = json.dumps(medicines, indent=2)
        
        prompt = f"""
Extracted Medicines:
---
{meds_json}
---

Generate the daily schedule. Remember: ONLY output a valid JSON object.
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
            logger.error("MedicationScheduleAgent JSON parse error", error=str(e), response=result)
            return {"schedule": {"Morning": [], "Afternoon": [], "Evening": [], "Night": []}}
        except Exception as e:
            logger.error("MedicationScheduleAgent error", error=str(e))
            return {"schedule": {"Morning": [], "Afternoon": [], "Evening": [], "Night": []}}
