import structlog
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.deps import get_current_user
from backend.app.models.health_timeline import HealthEvent, HealthInsight
from backend.app.models.patient_profile import PatientProfile
from backend.app.models.prescription import MedicationHistory

from backend.app.health_timeline.timeline.sync_service import timeline_sync_service
from backend.app.health_timeline.analytics.trend_engine import trend_engine
from backend.app.health_timeline.comparison.comparison_engine import comparison_engine
from backend.app.health_timeline.services.pdf_generator import pdf_generator
from backend.app.ai.crews.health_intelligence_crew import health_intelligence_crew

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api/timeline", tags=["Timeline"])

@router.get("")
def get_timeline(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Fetches chronological health events, syncing first."""
    user_id = current_user.get("sub", "unknown")
    timeline_sync_service.sync_patient_timeline(db, user_id)
    
    events = db.query(HealthEvent).filter(HealthEvent.patient_id == user_id).order_by(HealthEvent.event_date.desc()).all()
    
    return [{
        "id": str(e.id),
        "event_type": e.event_type.value,
        "title": e.title,
        "summary": e.summary,
        "event_date": e.event_date.isoformat(),
        "metadata_json": e.metadata_json
    } for e in events]

@router.get("/insights")
def get_insights(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Fetches stored health insights."""
    user_id = current_user.get("sub", "unknown")
    insights = db.query(HealthInsight).filter(HealthInsight.patient_id == user_id).order_by(HealthInsight.created_at.desc()).all()
    
    return [{
        "id": str(i.id),
        "title": i.title,
        "description": i.description,
        "category": i.category,
        "created_at": i.created_at.isoformat()
    } for i in insights]

@router.get("/trends")
def get_trends(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Fetches lab trends."""
    user_id = current_user.get("sub", "unknown")
    trends = trend_engine.analyze_trends(db, user_id)
    return trends

@router.post("/history/compare")
async def compare_history(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Triggers the full intelligence crew to generate new insights."""
    user_id = current_user.get("sub", "unknown")
    
    # 1. Sync
    timeline_sync_service.sync_patient_timeline(db, user_id)
    
    # 2. Gather context
    profile = db.query(PatientProfile).filter(PatientProfile.user_id == user_id).first()
    med_hist = db.query(MedicationHistory).filter(MedicationHistory.patient_id == user_id).all()
    med_names = [m.medicine_name for m in med_hist]
    events_obj = db.query(HealthEvent).filter(HealthEvent.patient_id == user_id).order_by(HealthEvent.event_date.asc()).all()
    events = [{"title": e.title, "summary": e.summary, "date": e.event_date.isoformat()} for e in events_obj]
    
    # 3. Engines
    trends = trend_engine.analyze_trends(db, user_id)
    comp_data = comparison_engine.compare_history(db, user_id)
    
    # 4. Crew
    result = await health_intelligence_crew.run(db, profile, med_names, trends, comp_data, events)
    return result

@router.get("/export")
async def export_timeline_pdf(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Generates a downloadable PDF of health summary."""
    user_id = current_user.get("sub", "unknown")
    
    profile = db.query(PatientProfile).filter(PatientProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Patient profile not found.")
        
    insights = db.query(HealthInsight).filter(HealthInsight.patient_id == user_id).order_by(HealthInsight.created_at.desc()).limit(20).all()
    trends = trend_engine.analyze_trends(db, user_id)
    
    pdf_bytes = pdf_generator.generate_health_summary(profile, insights, trends)
    
    return Response(
        content=pdf_bytes, 
        media_type="application/pdf", 
        headers={"Content-Disposition": f"attachment; filename=Health_Summary.pdf"}
    )
