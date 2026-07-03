import structlog
from sqlalchemy.orm import Session
from backend.app.models.health_timeline import HealthEvent, EventType
from backend.app.models.medical_report import MedicalReport
from backend.app.models.consultation import Consultation
from backend.app.models.prescription import Prescription
import json

logger = structlog.get_logger(__name__)

class TimelineSyncService:
    """Syncs distinct health records into the unified HealthEvent timeline."""

    def sync_patient_timeline(self, db: Session, patient_id: str):
        """Idempotently syncs existing records into the unified timeline."""
        logger.info("Starting timeline sync", patient_id=patient_id)
        
        # 1. Sync Consultations
        consultations = db.query(Consultation).filter(Consultation.patient_id == patient_id, Consultation.status == 'completed').all()
        for c in consultations:
            existing = db.query(HealthEvent).filter(HealthEvent.metadata_json['source_id'].astext == str(c.id)).first()
            if not existing:
                summary_data = c.summary if c.summary else "{}"
                event = HealthEvent(
                    patient_id=patient_id,
                    event_type=EventType.CONSULTATION,
                    title="Clinical Consultation",
                    summary=f"Consultation completed. Summary data: {summary_data}",
                    event_date=c.created_at,
                    metadata_json={"source_id": str(c.id), "source_type": "consultation"}
                )
                db.add(event)

        # 2. Sync Medical Reports
        reports = db.query(MedicalReport).filter(MedicalReport.patient_id == patient_id, MedicalReport.status == 'completed').all()
        for r in reports:
            existing = db.query(HealthEvent).filter(HealthEvent.metadata_json['source_id'].astext == str(r.id)).first()
            if not existing:
                event = HealthEvent(
                    patient_id=patient_id,
                    event_type=EventType.REPORT,
                    title=f"Medical Report: {r.report_type}",
                    summary=r.summary,
                    event_date=r.created_at,
                    metadata_json={"source_id": str(r.id), "source_type": "medical_report"}
                )
                db.add(event)

        # 3. Sync Prescriptions
        prescriptions = db.query(Prescription).filter(Prescription.patient_id == patient_id, Prescription.status == 'completed').all()
        for p in prescriptions:
            existing = db.query(HealthEvent).filter(HealthEvent.metadata_json['source_id'].astext == str(p.id)).first()
            if not existing:
                event = HealthEvent(
                    patient_id=patient_id,
                    event_type=EventType.PRESCRIPTION,
                    title=f"Prescription from {p.doctor_name or 'Doctor'} at {p.hospital_name or 'Clinic'}",
                    summary=p.summary,
                    event_date=p.created_at,
                    metadata_json={"source_id": str(p.id), "source_type": "prescription"}
                )
                db.add(event)
                
        db.commit()
        logger.info("Timeline sync completed", patient_id=patient_id)

timeline_sync_service = TimelineSyncService()
