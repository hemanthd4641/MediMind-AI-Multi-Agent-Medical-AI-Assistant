import structlog
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.models.health_timeline import HealthEvent, EventType
import json

logger = structlog.get_logger(__name__)

class ComparisonEngine:
    """Compares the most recent health events against historical ones to find deltas."""

    def compare_history(self, db: Session, patient_id: str) -> Dict[str, Any]:
        logger.info("Starting historical comparison", patient_id=patient_id)
        
        events = db.query(HealthEvent).filter(HealthEvent.patient_id == patient_id).order_by(HealthEvent.event_date.desc()).all()
        
        if len(events) < 2:
            return {"status": "insufficient_data", "message": "Need at least two events to perform comparison."}
            
        reports = [e for e in events if e.event_type == EventType.REPORT]
        consultations = [e for e in events if e.event_type == EventType.CONSULTATION]
        
        report_delta = self._compare_events(reports)
        consultation_delta = self._compare_events(consultations)
        
        return {
            "reports_comparison": report_delta,
            "consultations_comparison": consultation_delta
        }

    def _compare_events(self, typed_events: List[HealthEvent]) -> Dict[str, Any]:
        if len(typed_events) < 2:
            return {"comparable": False}
            
        recent = typed_events[0]
        previous = typed_events[1]
        
        return {
            "comparable": True,
            "recent_event": {
                "id": str(recent.id),
                "date": recent.event_date.isoformat(),
                "title": recent.title,
                "summary": recent.summary
            },
            "previous_event": {
                "id": str(previous.id),
                "date": previous.event_date.isoformat(),
                "title": previous.title,
                "summary": previous.summary
            }
        }

comparison_engine = ComparisonEngine()
