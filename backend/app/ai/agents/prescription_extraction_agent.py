import structlog
import json
from typing import Dict, Any
from backend.app.ai.services.groq_llm_service import groq_llm_service

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are an expert Medical Prescription Extraction Agent.
Your job is to read raw OCR text from a handwritten or printed prescription and extract the structured data.

You must return a valid JSON object matching this structure:
{
  "doctor_name": "string or null",
  "hospital_name": "string or null",
  "medicines": [
    {
      "medicine_name": "string (e.g. Paracetamol)",
      "strength": "string (e.g. 500mg)",
      "unit": "string (e.g. Tablet)",
      "frequency": "string (e.g. 1-0-1 or twice a day)",
      "duration": "string (e.g. 5 days)",
      "route": "string (e.g. Oral)",
      "instructions": "string (e.g. After meals)"
    }
  ]
}

If no medicines are found, return {"medicines": []}.
DO NOT output any markdown blocks (like ```json), just output the raw JSON object.
"""

class PrescriptionExtractionAgent:
    """Extracts structured medicine data from raw OCR text."""

    async def run(self, raw_text: str) -> Dict[str, Any]:
        logger.info("PrescriptionExtractionAgent started")
        
        prompt = f"""Raw OCR Text:
---
{raw_text}
---

Extract the structured prescription data. Remember: ONLY output a valid JSON object.
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
            logger.error("PrescriptionExtractionAgent JSON parse error", error=str(e), response=result)
            return {"medicines": []}
        except Exception as e:
            logger.error("PrescriptionExtractionAgent error", error=str(e))
            return {"medicines": []}
