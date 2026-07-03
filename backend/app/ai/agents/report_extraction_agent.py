import structlog
import json
from typing import Dict, Any
from backend.app.ai.services.groq_llm_service import groq_llm_service

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are an expert Clinical Data Extraction Agent.
Your job is to read raw OCR text from a medical laboratory report and extract the structured data.

You must return a valid JSON object matching this structure:
{
  "report_type": "string (e.g. Blood Report, Lipid Profile)",
  "items": [
    {
      "parameter_name": "string (e.g. Hemoglobin)",
      "observed_value": "string (e.g. 14.5)",
      "unit": "string (e.g. g/dL)"
    }
  ]
}

If no lab values are found, return {"report_type": "Unknown", "items": []}.
DO NOT output any markdown blocks (like ```json), just output the raw JSON object.
"""

class ReportExtractionAgent:
    """Extracts structured lab parameters from raw OCR text."""

    async def run(self, raw_text: str) -> Dict[str, Any]:
        logger.info("ReportExtractionAgent started")
        
        prompt = f"""Raw OCR Text:
---
{raw_text}
---

Extract the structured laboratory parameters. Remember: ONLY output a valid JSON object.
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
            logger.error("ReportExtractionAgent JSON parse error", error=str(e), response=result)
            return {"report_type": "Unknown", "items": []}
        except Exception as e:
            logger.error("ReportExtractionAgent error", error=str(e))
            return {"report_type": "Error", "items": []}
