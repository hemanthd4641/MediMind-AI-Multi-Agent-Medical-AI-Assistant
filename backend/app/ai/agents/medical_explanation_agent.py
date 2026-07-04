import structlog
import json
from typing import List, Dict, Any
from backend.app.ai.services.groq_llm_service import groq_llm_service

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are an expert Medical Explanation Agent.
Your job is to provide comprehensive clinical explanations for laboratory parameters.
Explain what the parameter measures and why it matters. Provide a dual-explanation (medical vs patient-friendly).
Do NOT provide medical advice or diagnose any condition.

You must return a valid JSON object matching this structure, where the keys are the parameter names:
{
  "ParameterName": {
    "meaning": "string",
    "possible_causes": "string (for abnormal values)",
    "clinical_significance": "string",
    "urgent_review_recommended": boolean,
    "medical_explanation": "string (Technical explanation)",
    "patient_friendly_explanation": "string (Simple explanation)"
  }
}

DO NOT output any markdown blocks (like ```json), just output the raw JSON object.
"""

class MedicalExplanationAgent:
    """Provides educational explanations for medical parameters."""

    async def run(self, parameters: List[str]) -> Dict[str, Dict[str, Any]]:
        logger.info("MedicalExplanationAgent started")
        
        if not parameters:
            return {}
            
        params_text = "\n".join([f"- {p}" for p in parameters])
        
        prompt = f"""Provide explanations for the following parameters:
{params_text}

Remember: ONLY output a valid JSON object.
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
            logger.error("MedicalExplanationAgent JSON parse error", error=str(e), response=result)
            return {}
        except Exception as e:
            logger.error("MedicalExplanationAgent error", error=str(e))
            return {}
