import os
import uuid
import structlog
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
import json
from datetime import datetime

from backend.app.database import get_db
from backend.app.deps import get_current_user
from backend.app.models.prescription import Prescription, PrescriptionMedicine, MedicationHistory, PrescriptionStatus, MedicationStatus
from backend.app.models.patient_profile import PatientProfile
from backend.app.prescriptions.extractor.pipeline import prescription_pipeline

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api/prescriptions", tags=["Prescriptions"])

UPLOAD_DIR = "uploads/prescriptions"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def process_prescription_background(prescription_id: uuid.UUID, file_path: str, mime_type: str, db: Session):
    try:
        prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
        if not prescription:
            return

        prescription.status = PrescriptionStatus.PROCESSING
        db.commit()

        # Get patient profile for allergies/chronic conditions
        profile = db.query(PatientProfile).filter(PatientProfile.user_id == prescription.patient_id).first()
        allergies = profile.allergies.split(',') if profile and profile.allergies else []
        chronic_conditions = profile.chronic_conditions.split(',') if profile and profile.chronic_conditions else []
        
        # Get active medication history
        history = db.query(MedicationHistory).filter(
            MedicationHistory.patient_id == prescription.patient_id, 
            MedicationHistory.status == MedicationStatus.ACTIVE
        ).all()
        history_names = [h.medicine_name for h in history]

        # 1. Pipeline execution (OCR -> CrewAI)
        from backend.app.ai.crews.prescription_crew import PrescriptionCrew
        crew = PrescriptionCrew()
        
        logger.info("Starting pipeline OCR phase")
        from backend.app.prescriptions.ocr.ocr_engine import prescription_ocr_engine
        raw_text = prescription_ocr_engine.extract_text(file_path, mime_type)
        
        ai_result = await crew.run(raw_text, allergies, chronic_conditions, history_names)
        
        # 3. Save to DB
        prescription.doctor_name = ai_result.get("doctor_name", "Unknown")
        prescription.hospital_name = ai_result.get("hospital_name", "Unknown")
        
        # Pack complex structured data into JSON summary
        summary_payload = {
            "summary": ai_result.get("summary", {}),
            "interactions": ai_result.get("interactions", []),
            "allergy_warnings": ai_result.get("allergy_warnings", []),
            "contraindications": ai_result.get("contraindications", []),
            "schedule": ai_result.get("schedule", {})
        }
        prescription.summary = json.dumps(summary_payload)

        # Save Medicines
        for med in ai_result.get("medicines", []):
            db_med = PrescriptionMedicine(
                prescription_id=prescription.id,
                medicine_name=med.get("medicine_name", "Unknown"),
                strength=med.get("strength"),
                unit=med.get("unit"),
                frequency=med.get("frequency"),
                duration=med.get("duration"),
                route=med.get("route"),
                instructions=med.get("instructions"),
                educational_explanation=med.get("educational_explanation")
            )
            db.add(db_med)
            
            # Also add to MedicationHistory
            db_hist = MedicationHistory(
                patient_id=prescription.patient_id,
                medicine_name=med.get("medicine_name", "Unknown"),
                start_date=datetime.utcnow(),
                status=MedicationStatus.ACTIVE,
                source_prescription_id=prescription.id
            )
            db.add(db_hist)
            
        prescription.status = PrescriptionStatus.COMPLETED
        db.commit()
        logger.info("Prescription processing completed", prescription_id=str(prescription.id))

    except Exception as e:
        logger.error("Prescription processing failed", error=str(e), prescription_id=str(prescription_id))
        prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
        if prescription:
            prescription.status = PrescriptionStatus.FAILED
            prescription.summary = json.dumps({"error": f"Error processing prescription: {str(e)}"})
            db.commit()

@router.post("/upload")
async def upload_prescription(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Uploads a prescription and kicks off intelligence processing."""
    user_id = current_user.get("sub", "unknown")
    
    file_ext = file.filename.split('.')[-1] if '.' in file.filename else ''
    safe_filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
        
    prescription = Prescription(
        patient_id=user_id,
        image_path=file_path,
        status=PrescriptionStatus.PENDING
    )
    db.add(prescription)
    db.commit()
    db.refresh(prescription)
    
    background_tasks.add_task(process_prescription_background, prescription.id, file_path, file.content_type, db)
    
    return {"message": "Prescription uploaded successfully. Processing started.", "prescription_id": str(prescription.id)}

@router.get("")
def list_prescriptions(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists all prescriptions for the user."""
    user_id = current_user.get("sub", "unknown")
    prescriptions = db.query(Prescription).filter(Prescription.patient_id == user_id).order_by(Prescription.created_at.desc()).all()
    
    return [{
        "id": str(p.id),
        "doctor_name": p.doctor_name,
        "hospital_name": p.hospital_name,
        "status": p.status.value,
        "created_at": p.created_at
    } for p in prescriptions]

@router.get("/{prescription_id}")
def get_prescription_details(
    prescription_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Gets detailed analysis of a prescription."""
    user_id = current_user.get("sub", "unknown")
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id, Prescription.patient_id == user_id).first()
    
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
        
    medicines = db.query(PrescriptionMedicine).filter(PrescriptionMedicine.prescription_id == prescription.id).all()
    
    summary_data = {}
    if prescription.summary:
        try:
            summary_data = json.loads(prescription.summary)
        except:
            pass
            
    return {
        "id": str(prescription.id),
        "doctor_name": prescription.doctor_name,
        "hospital_name": prescription.hospital_name,
        "status": prescription.status.value,
        "created_at": prescription.created_at,
        "medicines": [{
            "id": str(m.id),
            "medicine_name": m.medicine_name,
            "strength": m.strength,
            "unit": m.unit,
            "frequency": m.frequency,
            "duration": m.duration,
            "route": m.route,
            "instructions": m.instructions,
            "educational_explanation": m.educational_explanation
        } for m in medicines],
        "analysis": summary_data
    }

@router.delete("/{prescription_id}")
def delete_prescription(
    prescription_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletes a prescription and its associated file."""
    user_id = current_user.get("sub", "unknown")
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id, Prescription.patient_id == user_id).first()
    
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
        
    try:
        if os.path.exists(prescription.image_path):
            os.remove(prescription.image_path)
    except Exception as e:
        logger.error("Failed to delete file", path=prescription.image_path, error=str(e))
        
    db.delete(prescription)
    db.commit()
    
    return {"message": "Prescription deleted successfully"}

@router.get("/history/medications")
def get_medication_history(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fetch user's medication history timeline."""
    user_id = current_user.get("sub", "unknown")
    history = db.query(MedicationHistory).filter(MedicationHistory.patient_id == user_id).order_by(MedicationHistory.start_date.desc()).all()
    
    return [{
        "id": str(h.id),
        "medicine_name": h.medicine_name,
        "start_date": h.start_date,
        "end_date": h.end_date,
        "status": h.status.value,
        "source_prescription_id": str(h.source_prescription_id) if h.source_prescription_id else None
    } for h in history]

@router.post("/check-interactions")
async def check_interactions(
    payload: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ad-hoc interaction checker for medicines."""
    user_id = current_user.get("sub", "unknown")
    medicines = payload.get("medicines", [])
    
    if not medicines:
        return {"interactions": []}
        
    profile = db.query(PatientProfile).filter(PatientProfile.user_id == user_id).first()
    chronic_conditions = profile.chronic_conditions.split(',') if profile and profile.chronic_conditions else []
    
    history = db.query(MedicationHistory).filter(
        MedicationHistory.patient_id == user_id, 
        MedicationHistory.status == MedicationStatus.ACTIVE
    ).all()
    history_names = [h.medicine_name for h in history]
    
    from backend.app.ai.agents.drug_interaction_agent import DrugInteractionAgent
    agent = DrugInteractionAgent()
    result = await agent.run(medicines, history_names, chronic_conditions)
    
    return result
