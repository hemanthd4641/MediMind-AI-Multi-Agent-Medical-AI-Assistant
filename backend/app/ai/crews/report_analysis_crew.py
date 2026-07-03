import time
import structlog
from typing import Dict, Any

from backend.app.ai.agents.abnormal_value_detection_agent import AbnormalValueDetectionAgent
from backend.app.ai.agents.medical_explanation_agent import MedicalExplanationAgent
from backend.app.ai.agents.report_clinical_summary_agent import ReportClinicalSummaryAgent
from backend.app.ai.agents.report_citation_agent import ReportCitationAgent

logger = structlog.get_logger(__name__)

class ReportAnalysisCrew:
    """Orchestrates the AI medical report analysis pipeline."""

    def __init__(self):
        self.abnormal_agent = AbnormalValueDetectionAgent()
        self.explanation_agent = MedicalExplanationAgent()
        self.summary_agent = ReportClinicalSummaryAgent()
        self.citation_agent = ReportCitationAgent()

    async def run(self, report_type: str, evaluated_items: list) -> Dict[str, Any]:
        """Runs the AI agents on the extracted/evaluated report parameters."""
        t0 = time.perf_counter()
        logger.info("ReportAnalysisCrew started")

        # 1. Abnormal Value Detection
        abnormal_data = await self.abnormal_agent.run(evaluated_items)
        
        # 2. Medical Explanations
        parameter_names = [item.get("parameter_name") for item in evaluated_items if item.get("parameter_name")]
        explanations = await self.explanation_agent.run(parameter_names)
        
        # Merge explanations back into items
        for item in evaluated_items:
            name = item.get("parameter_name")
            if name and name in explanations:
                item["explanation"] = explanations[name]
        
        # 3. Clinical Summary
        summary_data = await self.summary_agent.run(report_type, abnormal_data, evaluated_items)
        
        # 4. Citations
        citation_data = await self.citation_agent.run(parameter_names)
        
        elapsed = round((time.perf_counter() - t0) * 1000)
        logger.info("ReportAnalysisCrew completed", elapsed_ms=elapsed)
        
        return {
            "abnormal_findings": abnormal_data.get("abnormal_findings", []),
            "has_critical_values": abnormal_data.get("has_critical_values", False),
            "summary": summary_data.get("summary", ""),
            "discussion_points": summary_data.get("discussion_points", []),
            "confidence_score": summary_data.get("confidence_score", 0.0),
            "citations": citation_data.get("citations", []),
            "evaluated_items": evaluated_items
        }
