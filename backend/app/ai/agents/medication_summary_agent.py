import structlog
import json
from typing import Dict, Any
from backend.app.ai.services.groq_llm_service import groq_llm_service

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are an expert Medication Summary Agent.
Your job is to generate a final summary of the prescription analysis.
It should include:
- A brief prescription summary
- Key warnings (from interactions, allergies, contraindications)
- Questions to discuss with the healthcare provider
- A mandatory medical disclaimer

You must return a valid JSON object matching this structure:
{
  "prescription_summary": "Summary text...",
  "warnings": ["Warning 1", "Warning 2"],
  "questions_to_ask": ["Question 1", "Question 2"],
  "medical_disclaimer": "This is an AI generated analysis..."
}

DO NOT output any markdown blocks (like ```json), just output the raw JSON object.
"""

class MedicationSummaryAgent:
    """Generates the final comprehensive summary."""

    async def run(self, extracted_data: Dict[str, Any], interaction_data: Dict[str, Any], allergy_data: Dict[str, Any], contra_data: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("MedicationSummaryAgent started")
        
        prompt = f"""
Prescription Data: {json.dumps(extracted_data)}
Interactions: {json.dumps(interaction_data)}
Allergies: {json.dumps(allergy_data)}
Contraindications: {json.dumps(contra_data)}

Generate the summary. Remember: ONLY output a valid JSON object.
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
            logger.error("MedicationSummaryAgent JSON parse error", error=str(e), response=result)
            return {
                "prescription_summary": "Failed to generate summary.",
                "warnings": [],
                "questions_to_ask": [],
                "medical_disclaimer": "This tool does not provide medical advice."
            }
        except Exception as e:
            logger.error("MedicationSummaryAgent error", error=str(e))
            return {
                "prescription_summary": "Error generating summary.",
                "warnings": [],
                "questions_to_ask": [],
                "medical_disclaimer": "This tool does not provide medical advice."
            }
