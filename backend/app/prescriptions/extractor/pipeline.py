import structlog
from typing import List, Dict, Any, Tuple
from backend.app.prescriptions.ocr.ocr_engine import prescription_ocr_engine

logger = structlog.get_logger(__name__)

class PrescriptionExtractionPipeline:
    """End-to-End pipeline for extracting prescription data."""
    
    async def process_prescription(self, file_path: str, mime_type: str) -> Tuple[str, Dict[str, Any]]:
        """
        Runs OCR, structured extraction (via Agent), and further analysis.
        Returns (Raw Text, Final CrewAI Result)
        """
        # 1. OCR Extraction
        logger.info("Starting prescription pipeline OCR phase")
        raw_text = prescription_ocr_engine.extract_text(file_path, mime_type)
        
        # 2. Crew AI Orchestration
        logger.info("Starting Prescription CrewAI analysis")
        from backend.app.ai.crews.prescription_crew import PrescriptionCrew
        
        crew = PrescriptionCrew()
        result = await crew.run(raw_text)
        
        return raw_text, result

prescription_pipeline = PrescriptionExtractionPipeline()
