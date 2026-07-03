import structlog
import json
from typing import List, Dict, Any
from backend.app.ai.services.groq_llm_service import groq_llm_service

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are an expert Drug Interaction Agent.
Your job is to check for potential drug interactions between a list of newly prescribed medicines and the patient's existing medication history and chronic conditions.

Categorize the severity of each interaction as: None, Minor, Moderate, or Major.
Provide a brief educational explanation for why the interaction exists.

Do NOT provide medical advice or recommend dosage adjustments.

You must return a valid JSON object matching this structure:
{
  "interactions": [
    {
      "medicine_1": "Name",
      "medicine_2": "Name or Condition",
      "severity": "Minor | Moderate | Major",
      "explanation": "Why interaction exists..."
    }
  ]
}

If no interactions are found, return {"interactions": []}.
DO NOT output any markdown blocks (like ```json), just output the raw JSON object.
"""

class DrugInteractionAgent:
    """Checks for drug interactions and severity."""

    async def run(self, new_medicines: List[str], current_medications: List[str], chronic_conditions: List[str]) -> Dict[str, Any]:
        logger.info("DrugInteractionAgent started")
        
        if not new_medicines:
            return {"interactions": []}
            
        prompt = f"""
New Prescribed Medicines: {', '.join(new_medicines)}
Patient Current Medications: {', '.join(current_medications) if current_medications else 'None'}
Patient Chronic Conditions: {', '.join(chronic_conditions) if chronic_conditions else 'None'}

Identify potential interactions. Remember: ONLY output a valid JSON object.
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
            logger.error("DrugInteractionAgent JSON parse error", error=str(e), response=result)
            return {"interactions": []}
        except Exception as e:
            logger.error("DrugInteractionAgent error", error=str(e))
            return {"interactions": []}
