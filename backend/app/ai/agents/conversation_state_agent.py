import structlog
from typing import List, Dict, Any
from backend.app.ai.services.groq_llm_service import groq_llm_service
from backend.app.ai.consultation_schemas import ConsultationState, ConsultationStage, SymptomDetails
import json

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are an expert Clinical Consultation State Agent.
Your job is to determine the current progress of a medical intake interview.

The interview has 7 strict stages:
1. Chief Complaint
2. Symptom Details
3. Medical History
4. Current Medication
5. Allergies
6. Lifestyle Factors
7. Summary

Analyze the extracted symptoms and the conversation history.
Determine:
1. The current stage of the consultation.
2. The percentage of completion (0-100).
3. Any critical missing information for the current or upcoming stages.
4. If the consultation is complete and ready for the final summary.

You must return a valid JSON object matching this structure:
{
  "current_stage": "Chief Complaint" | "Symptom Details" | "Medical History" | "Current Medication" | "Allergies" | "Lifestyle Factors" | "Summary",
  "progress_percentage": 50,
  "missing_information": ["string", "string"],
  "is_complete": false
}

DO NOT output any markdown blocks (like ```json), just output the raw JSON object.
"""

class ConversationStateAgent:
    """Tracks consultation progress across 7 stages."""

    async def run(self, chat_history: List[Dict[str, str]], extracted_symptoms: List[SymptomDetails]) -> ConsultationState:
        logger.info("ConversationStateAgent started")
        
        history_text = ""
        for msg in chat_history:
            role = "Patient" if msg["sender"] == "user" else "AI"
            history_text += f"{role}: {msg['content']}\n"
            
        symptoms_text = "\n".join([s.model_dump_json() for s in extracted_symptoms])
        
        prompt = f"""Conversation History:
---
{history_text}
---

Extracted Symptoms:
---
{symptoms_text}
---

Determine the consultation state. Remember: ONLY output a valid JSON object.
"""
        try:
            result = await groq_llm_service.generate(prompt, system_prompt=SYSTEM_PROMPT)
            
            # Clean up response in case of markdown formatting
            result = result.strip()
            if result.startswith("```json"):
                result = result[7:]
            if result.startswith("```"):
                result = result[3:]
            if result.endswith("```"):
                result = result[:-3]
            result = result.strip()
            
            data = json.loads(result)
            return ConsultationState(**data)
            
        except json.JSONDecodeError as e:
            logger.error("ConversationStateAgent JSON parse error", error=str(e), response=result)
            # Fallback to initial state
            return ConsultationState(
                current_stage=ConsultationStage.CHIEF_COMPLAINT,
                progress_percentage=10,
                missing_information=["Chief complaint", "Main symptoms"],
                is_complete=False
            )
        except Exception as e:
            logger.error("ConversationStateAgent error", error=str(e))
            return ConsultationState(
                current_stage=ConsultationStage.CHIEF_COMPLAINT,
                progress_percentage=10,
                missing_information=[],
                is_complete=False
            )
