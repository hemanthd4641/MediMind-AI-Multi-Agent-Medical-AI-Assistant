import os
import uuid
import structlog
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.deps import get_current_user
from backend.app.models.medical_report import MedicalReport, MedicalReportItem, ReportStatus
from backend.app.medical_reports.extractor.pipeline import extraction_pipeline
from backend.app.ai.crews.report_analysis_crew import ReportAnalysisCrew
import json

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api/reports", tags=["Medical Reports"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def process_report_background(report_id: uuid.UUID, file_path: str, mime_type: str, db: Session):
    """Background task to run the heavy OCR and AI Pipeline."""
    try:
        report = db.query(MedicalReport).filter(MedicalReport.id == report_id).first()
        if not report:
            return

        report.status = ReportStatus.PROCESSING
        db.commit()

        # 1. OCR & Structured Extraction
        raw_text, evaluated_items, report_type = await extraction_pipeline.process_report(file_path, mime_type)
        
        # 2. CrewAI Analysis
        crew = ReportAnalysisCrew()
        ai_result = await crew.run(report_type, evaluated_items)
        
        # 3. Save to DB
        report.report_type = report_type
        report.summary = ai_result.get("summary")
        report.confidence = ai_result.get("confidence_score")
        
        # Store educational notes or citations in a JSON string (could be a separate column/table in production)
        report.educational_notes = json.dumps({
            "discussion_points": ai_result.get("discussion_points", []),
            "citations": ai_result.get("citations", [])
        })

        # Save Items
        for item in ai_result.get("evaluated_items", []):
            db_item = MedicalReportItem(
                report_id=report.id,
                parameter_name=item.get("parameter_name", "Unknown"),
                observed_value=item.get("observed_value", "0"),
                unit=item.get("unit"),
                reference_min=item.get("reference_min"),
                reference_max=item.get("reference_max"),
                status=item.get("status", "NORMAL"),
                explanation=item.get("explanation")
            )
            db.add(db_item)
            
        report.status = ReportStatus.COMPLETED
        db.commit()
        logger.info("Report processing completed successfully", report_id=str(report.id))

    except Exception as e:
        logger.error("Report processing failed", error=str(e), report_id=str(report_id))
        report = db.query(MedicalReport).filter(MedicalReport.id == report_id).first()
        if report:
            report.status = ReportStatus.FAILED
            report.summary = f"Error processing report: {str(e)}"
            db.commit()

@router.post("/upload")
async def upload_report(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Uploads a medical report and kicks off processing."""
    user_id = current_user.get("sub", "unknown")
    logger.info("Uploading report", filename=file.filename, user_id=user_id)
    
    file_ext = file.filename.split('.')[-1] if '.' in file.filename else ''
    safe_filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
        
    report = MedicalReport(
        patient_id=user_id,
        title=file.filename,
        report_type="Pending...",
        status=ReportStatus.PENDING,
        file_path=file_path
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    
    background_tasks.add_task(process_report_background, report.id, file_path, file.content_type, db)
    
    return {"message": "Report uploaded successfully. Processing started.", "report_id": str(report.id)}

@router.get("")
def list_reports(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists all medical reports for the user."""
    user_id = current_user.get("sub", "unknown")
    reports = db.query(MedicalReport).filter(MedicalReport.patient_id == user_id).order_by(MedicalReport.created_at.desc()).all()
    
    return [{
        "id": str(r.id),
        "title": r.title,
        "report_type": r.report_type,
        "status": r.status.value,
        "upload_date": r.upload_date,
        "confidence": r.confidence
    } for r in reports]

@router.get("/{report_id}")
def get_report_details(
    report_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Gets detailed analysis of a medical report."""
    user_id = current_user.get("sub", "unknown")
    report = db.query(MedicalReport).filter(MedicalReport.id == report_id, MedicalReport.patient_id == user_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    items = db.query(MedicalReportItem).filter(MedicalReportItem.report_id == report.id).all()
    
    notes = {}
    if report.educational_notes:
        try:
            notes = json.loads(report.educational_notes)
        except:
            pass
            
    return {
        "id": str(report.id),
        "title": report.title,
        "report_type": report.report_type,
        "status": report.status.value,
        "upload_date": report.upload_date,
        "summary": report.summary,
        "confidence": report.confidence,
        "discussion_points": notes.get("discussion_points", []),
        "citations": notes.get("citations", []),
        "items": [{
            "id": str(i.id),
            "parameter_name": i.parameter_name,
            "observed_value": i.observed_value,
            "unit": i.unit,
            "reference_min": i.reference_min,
            "reference_max": i.reference_max,
            "status": i.status.value,
            "explanation": i.explanation
        } for i in items]
    }

@router.delete("/{report_id}")
def delete_report(
    report_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletes a report and its associated file."""
    user_id = current_user.get("sub", "unknown")
    report = db.query(MedicalReport).filter(MedicalReport.id == report_id, MedicalReport.patient_id == user_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    try:
        if os.path.exists(report.file_path):
            os.remove(report.file_path)
    except Exception as e:
        logger.error("Failed to delete file", path=report.file_path, error=str(e))
        
    db.delete(report)
    db.commit()
    
    return {"message": "Report deleted successfully"}
