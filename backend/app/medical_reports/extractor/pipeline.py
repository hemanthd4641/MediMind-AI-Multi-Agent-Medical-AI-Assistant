import structlog
from typing import List, Dict, Any, Tuple
from backend.app.medical_reports.ocr.engine import ocr_engine
from backend.app.medical_reports.reference_ranges.engine import reference_range_engine

logger = structlog.get_logger(__name__)

class ExtractionPipeline:
    """End-to-End pipeline for extracting medical report data."""
    
    async def process_report(self, file_path: str, mime_type: str) -> Tuple[str, List[Dict[str, Any]], str]:
        """
        Runs OCR, structured extraction (via Agent), and reference range evaluation.
        Returns (Raw Text, Evaluated Items, Report Type)
        """
        # 1. OCR Extraction
        logger.info("Starting pipeline OCR phase")
        raw_text = ocr_engine.extract_text(file_path, mime_type)
        
        # 2. Structured Extraction (CrewAI Agent)
        # We import here to avoid circular dependencies if agents import models etc.
        from backend.app.ai.agents.report_extraction_agent import ReportExtractionAgent
        extractor = ReportExtractionAgent()
        
        logger.info("Starting pipeline AI Extraction phase")
        report_data = await extractor.run(raw_text)
        
        # report_data should be a dictionary: {"report_type": "Blood Test", "items": [...]}
        items = report_data.get("items", [])
        report_type = report_data.get("report_type", "General Lab Report")
        
        # 3. Reference Range Evaluation
        logger.info("Evaluating extracted parameters against reference ranges")
        evaluated_items = reference_range_engine.process_items(items)
        
        return raw_text, evaluated_items, report_type

extraction_pipeline = ExtractionPipeline()
