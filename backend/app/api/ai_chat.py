"""
POST /api/ai/chat
Authenticated endpoint – calls MedicalAIService only.
FastAPI routes must NEVER interact with CrewAI directly.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
import structlog

from backend.app.ai.schemas import ChatRequest, MedicalResponse
from backend.app.ai.services.medical_ai_service import medical_ai_service
from backend.app.deps import get_current_user

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/ai", tags=["AI Chat"])


from backend.app.database import get_db
from sqlalchemy.orm import Session

@router.post(
    "/chat",
    response_model=MedicalResponse,
    summary="AI Medical Chat",
    description="Send a message to the MediMind AI multi-agent system. Requires authentication.",
)
async def ai_chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MedicalResponse:
    """
    Process a user message through the full AI pipeline.

    - **message**: The user's message (required, min 1 char)

    Returns a structured response with intent, agents used, emergency level, and the composed reply.
    """
    user_id = current_user.get("sub", "unknown")
    logger.info("POST /api/ai/chat received", user_id=user_id)

    response = await medical_ai_service.process_request(
        message=request.message,
        user_id=user_id,
        db=db,
    )
    return response
