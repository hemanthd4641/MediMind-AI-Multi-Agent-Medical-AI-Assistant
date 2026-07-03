import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
import uuid

from backend.app.database import get_db
from backend.app.deps import get_current_user
from backend.app.models.consultation import Consultation, ConsultationMessage
from backend.app.ai.crews.consultation_crew import ConsultationCrew

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/consultation", tags=["Consultation"])

# Initialize crew
_crew = ConsultationCrew()

class ConsultationMessageRequest(BaseModel):
    message: str

@router.post("/start")
async def start_consultation(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Starts a new consultation session."""
    user_id = current_user.get("sub", "unknown")
    logger.info("Starting new consultation", user_id=user_id)
    
    # Create new consultation
    consultation = Consultation(patient_id=user_id, status="active")
    db.add(consultation)
    db.commit()
    db.refresh(consultation)
    
    initial_greeting = "Hello. I am the MediMind Clinical Assistant. I'm here to help understand your symptoms and provide a summary for your doctor. What is the primary reason you are seeking medical help today?"
    
    # Save AI greeting
    msg = ConsultationMessage(
        consultation_id=consultation.id,
        sender="ai",
        content=initial_greeting
    )
    db.add(msg)
    db.commit()
    
    return {
        "consultation_id": str(consultation.id),
        "response": initial_greeting,
        "stage": "Chief Complaint",
        "progress": 0,
        "urgency": "Routine",
        "symptoms": []
    }

@router.post("/{consultation_id}/message")
async def send_message(
    consultation_id: uuid.UUID,
    request: ConsultationMessageRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Processes a user message in the consultation."""
    user_id = current_user.get("sub", "unknown")
    
    consultation = db.query(Consultation).filter(Consultation.id == consultation_id, Consultation.patient_id == user_id).first()
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")
        
    if consultation.status == "completed":
        raise HTTPException(status_code=400, detail="Consultation is already completed")
        
    # Save user message
    user_msg = ConsultationMessage(
        consultation_id=consultation.id,
        sender="user",
        content=request.message
    )
    db.add(user_msg)
    db.commit()
    
    # Load history
    messages = db.query(ConsultationMessage).filter(ConsultationMessage.consultation_id == consultation.id).order_by(ConsultationMessage.timestamp.asc()).all()
    chat_history = [{"sender": m.sender, "content": m.content} for m in messages[:-1]] # Exclude the latest user message
    
    # Run Crew
    try:
        result = await _crew.run(chat_history=chat_history, latest_message=request.message)
        
        # Save AI response
        ai_msg = ConsultationMessage(
            consultation_id=consultation.id,
            sender="ai",
            content=result["response"]
        )
        db.add(ai_msg)
        
        if result["is_complete"]:
            consultation.status = "completed"
            
        db.commit()
        return result
        
    except Exception as e:
        logger.error("Consultation pipeline error", error=str(e))
        raise HTTPException(status_code=500, detail="Error processing consultation")

@router.get("/{consultation_id}")
def get_consultation(
    consultation_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Gets the consultation and its history."""
    user_id = current_user.get("sub", "unknown")
    consultation = db.query(Consultation).filter(Consultation.id == consultation_id, Consultation.patient_id == user_id).first()
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")
        
    messages = db.query(ConsultationMessage).filter(ConsultationMessage.consultation_id == consultation.id).order_by(ConsultationMessage.timestamp.asc()).all()
    
    return {
        "id": str(consultation.id),
        "status": consultation.status,
        "created_at": consultation.created_at,
        "messages": [{"id": str(m.id), "sender": m.sender, "content": m.content, "timestamp": m.timestamp} for m in messages]
    }

@router.get("/{consultation_id}/summary")
async def get_consultation_summary(
    consultation_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generates and returns the final summary for a completed consultation."""
    user_id = current_user.get("sub", "unknown")
    consultation = db.query(Consultation).filter(Consultation.id == consultation_id, Consultation.patient_id == user_id).first()
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")
        
    messages = db.query(ConsultationMessage).filter(ConsultationMessage.consultation_id == consultation.id).order_by(ConsultationMessage.timestamp.asc()).all()
    chat_history = [{"sender": m.sender, "content": m.content} for m in messages]
    
    # We re-run symptom extraction and urgency against the full history to get the final state.
    # Note: In a production app, this should be saved to the DB in step 4, but the instructions say "Do not store temporary AI memory."
    from backend.app.ai.agents.symptom_extraction_agent import SymptomExtractionAgent
    from backend.app.ai.agents.urgency_assessment_agent import UrgencyAssessmentAgent
    from backend.app.ai.agents.consultation_summary_agent import ConsultationSummaryAgent
    
    symptoms = await SymptomExtractionAgent().run(chat_history[:-1], chat_history[-1]["content"] if chat_history else "")
    urgency = await UrgencyAssessmentAgent().run(symptoms)
    summary = await ConsultationSummaryAgent().run(chat_history, symptoms, urgency)
    
    return summary.model_dump()
