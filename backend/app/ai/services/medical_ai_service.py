"""
MedicalAIService – the only entry point for FastAPI routes to the AI layer.
FastAPI routes must NEVER interact with CrewAI directly.
"""
from __future__ import annotations

import structlog
from fastapi import HTTPException, status

from backend.app.ai.crews.medical_crew import MedicalCrew
from backend.app.ai.schemas import MedicalResponse
from backend.app.ai.services.consultation_engine import ConsultationEngine

logger = structlog.get_logger(__name__)

# Module-level crew instance (reused across requests)
_crew = MedicalCrew()
_engine = ConsultationEngine()


from sqlalchemy.orm import Session

class MedicalAIService:
    """Facade over the MedicalCrew – the only public AI interface."""

    async def process_request(self, message: str, user_id: str, db: Session | None = None) -> MedicalResponse:
        """Process a user message through the full AI pipeline.

        Args:
            message: The raw user message.
            user_id: Authenticated user ID (for logging / future memory).
            db: Database session.

        Returns:
            A structured MedicalResponse ready for the API.

        Raises:
            HTTPException 503 if the AI pipeline is unavailable.
        """
        logger.info("MedicalAIService.process_request", user_id=user_id, message_preview=message[:80])

        try:
            # 1. Run Consultation Engine
            state, next_question, action = await _engine.process_message(user_id, message)
            
            # 2. Enhance message for CrewAI
            enhanced_message = (
                f"--- STRUCTURED CONSULTATION STATE ---\n"
                f"{state.model_dump_json(indent=2)}\n"
                f"-------------------------------------\n\n"
                f"USER MESSAGE: {message}\n\n"
            )
            
            if action == "summarize":
                enhanced_message += "SYSTEM INSTRUCTION: All required clinical slots are completed. Generate a comprehensive clinical consultation summary based on the structured state."
            else:
                enhanced_message += f"SYSTEM INSTRUCTION: You must ask the following next question to the patient. Do not ask anything else. Be empathetic.\nNEXT QUESTION TO ASK: {next_question}"

            response = await _crew.run(enhanced_message, db=db)
            return response
        except RuntimeError as exc:
            logger.error("AI pipeline error", user_id=user_id, error=str(exc))
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"AI service temporarily unavailable: {exc}",
            ) from exc
        except Exception as exc:
            logger.error("Unexpected AI error", user_id=user_id, error=str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred in the AI pipeline.",
            ) from exc


# Module-level singleton
medical_ai_service = MedicalAIService()
