import structlog
from typing import List, Dict, Any
from backend.app.ai.services.groq_llm_service import groq_llm_service
from backend.app.ai.consultation_schemas import UrgencyAssessment, SymptomDetails
import json

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are an expert Clinical Urgency Assessment Agent.
Your job is to analyze the extracted symptoms and determine the medical urgency level.

Urgency Levels:
- Routine: Non-urgent, standard care.
- Soon: Requires attention within a few days.
- Urgent: Requires attention within 24 hours (e.g., Urgent Care).
- Emergency: Requires immediate life-saving care (e.g., ER / 911).

Rules:
1. NEVER provide a medical diagnosis.
2. Err on the side of caution.
3. Consider severity, duration, and associated symptoms (e.g., chest pain with sweating is Emergency).

You must return a valid JSON object matching this structure:
{
  "level": "Routine" | "Soon" | "Urgent" | "Emergency",
  "explanation": "Why this urgency was assigned"
}

DO NOT output any markdown blocks (like ```json), just output the raw JSON object.
"""

class UrgencyAssessmentAgent:
    """Classifies the medical urgency based on symptoms."""

    async def run(self, symptoms: List[SymptomDetails]) -> UrgencyAssessment:
        logger.info("UrgencyAssessmentAgent started")
        
        if not symptoms:
            return UrgencyAssessment(level="Routine", explanation="No symptoms reported yet.")
            
        symptoms_text = "\n".join([s.model_dump_json() for s in symptoms])
        
        prompt = f"""Extracted Symptoms:
---
{symptoms_text}
---

Determine the urgency level. Remember: ONLY output a valid JSON object.
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
            return UrgencyAssessment(**data)
            
        except json.JSONDecodeError as e:
            logger.error("UrgencyAssessmentAgent JSON parse error", error=str(e), response=result)
            # Safe fallback
            return UrgencyAssessment(
                level="Routine",
                explanation="Failed to parse urgency, defaulting to Routine. Please consult a doctor."
            )
        except Exception as e:
            logger.error("UrgencyAssessmentAgent error", error=str(e))
            return UrgencyAssessment(
                level="Routine",
                explanation="Error processing urgency."
            )
