import structlog
from typing import List, Dict, Any
from backend.app.ai.services.groq_llm_service import groq_llm_service
from backend.app.ai.consultation_schemas import ConsultationSummary, SymptomDetails, UrgencyAssessment
import json

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are an expert Clinical Summary Agent.
Based on the conversation history, extracted symptoms, and urgency assessment, compile a structured clinical consultation summary.

The summary should be professional, objective, and structured.
Provide Clinical Decision Support by suggesting possible differential diagnoses, recommended specialty, and diagnostic tests.
You MUST explicitly state that the differential diagnoses are possibilities and NOT confirmed diagnoses.

You must return a valid JSON object matching this structure:
{
  "chief_complaint": "string",
  "symptoms": [{"symptom": "string", "body_location": "string"}], // Include all SymptomDetails fields if present
  "timeline": "string",
  "relevant_medical_history": "string",
  "current_medications": "string",
  "allergies": "string",
  "lifestyle_factors": "string",
  "risk_factors": ["string", "string"],
  "severity_assessment": "string",
  "risk_assessment": "string",
  "red_flag_detection": ["string", "string"],
  "triage_level": "Routine" | "Soon" | "Urgent" | "Emergency",
  "differential_diagnoses": ["string (Possibility)", "string (Possibility)"],
  "recommended_specialty": "string",
  "suggested_diagnostic_tests": ["string", "string"],
  "recommended_next_steps": ["string", "string"],
  "medical_disclaimer": "This is an AI-generated summary for informational purposes only and does not constitute medical advice or a diagnosis. Please consult a qualified healthcare professional."
}

DO NOT output any markdown blocks (like ```json), just output the raw JSON object.
"""

class ConsultationSummaryAgent:
    """Generates the final consultation summary."""

    async def run(
        self, 
        chat_history: List[Dict[str, str]], 
        symptoms: List[SymptomDetails], 
        urgency: UrgencyAssessment
    ) -> ConsultationSummary:
        logger.info("ConsultationSummaryAgent started")
        
        history_text = ""
        for msg in chat_history:
            role = "Patient" if msg["sender"] == "user" else "AI"
            history_text += f"{role}: {msg['content']}\n"
            
        symptoms_text = "\n".join([s.model_dump_json() for s in symptoms])
        
        prompt = f"""Conversation History:
---
{history_text}
---

Extracted Symptoms:
---
{symptoms_text}
---

Urgency Assessment:
Level: {urgency.level.value}
Explanation: {urgency.explanation}

Compile the consultation summary. Remember: ONLY output a valid JSON object.
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
            return ConsultationSummary(**data)
            
        except json.JSONDecodeError as e:
            logger.error("ConsultationSummaryAgent JSON parse error", error=str(e), response=result)
            return self._fallback_summary(symptoms, urgency)
        except Exception as e:
            logger.error("ConsultationSummaryAgent error", error=str(e))
            return self._fallback_summary(symptoms, urgency)

    def _fallback_summary(self, symptoms: List[SymptomDetails], urgency: UrgencyAssessment) -> ConsultationSummary:
        return ConsultationSummary(
            chief_complaint="Failed to compile summary.",
            symptoms=symptoms,
            timeline="N/A",
            relevant_medical_history="N/A",
            current_medications="N/A",
            allergies="N/A",
            lifestyle_factors="N/A",
            risk_factors=[],
            severity_assessment="Unknown",
            risk_assessment="Unknown",
            red_flag_detection=[],
            triage_level=urgency.level,
            differential_diagnoses=[],
            recommended_specialty="Unknown",
            suggested_diagnostic_tests=[],
            recommended_next_steps=["Please consult a doctor directly as the summary could not be generated."],
            medical_disclaimer="This is an AI-generated summary for informational purposes only and does not constitute medical advice or a diagnosis. Please consult a qualified healthcare professional."
        )
