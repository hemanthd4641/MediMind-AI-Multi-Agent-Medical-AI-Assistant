import structlog
import json
from typing import Dict, Any
from backend.app.ai.services.groq_llm_service import groq_llm_service

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are an expert Clinical Summary Agent.
Your job is to generate a plain-language summary of a medical report based on the extracted and evaluated findings.
Highlight important discussion points for healthcare professionals.
Do NOT provide medical advice or diagnose any condition.

You must return a valid JSON object matching this structure:
{
  "summary": "Plain-language summary of the report...",
  "discussion_points": ["Point 1", "Point 2"],
  "confidence_score": 0.95 // A float between 0.0 and 1.0 representing how confident you are in this summary based on the data
}

DO NOT output any markdown blocks (like ```json), just output the raw JSON object.
"""

class ReportClinicalSummaryAgent:
    """Generates the final plain-language report summary."""

    async def run(self, report_type: str, abnormal_data: Dict[str, Any], raw_items: list) -> Dict[str, Any]:
        logger.info("ReportClinicalSummaryAgent started")
        
        items_json = json.dumps(raw_items, indent=2)
        abnormal_json = json.dumps(abnormal_data, indent=2)
        
        prompt = f"""Report Type: {report_type}

Evaluated Parameters:
---
{items_json}
---

Abnormal Findings detected:
---
{abnormal_json}
---

Generate the summary. Remember: ONLY output a valid JSON object.
"""
        try:
            result = await groq_llm_service.generate(prompt, system_prompt=SYSTEM_PROMPT)
            
            result = result.strip()
            if result.startswith("```json"):
                result = result[7:]
            if result.startswith("```"):
                result = result[3:]
            if result.endswith("```"):
                result = result[:-3]
            result = result.strip()
            
            data = json.loads(result)
            return data
            
        except json.JSONDecodeError as e:
            logger.error("ReportClinicalSummaryAgent JSON parse error", error=str(e), response=result)
            return {
                "summary": "Failed to generate summary.",
                "discussion_points": [],
                "confidence_score": 0.0
            }
        except Exception as e:
            logger.error("ReportClinicalSummaryAgent error", error=str(e))
            return {
                "summary": "Error generating summary.",
                "discussion_points": [],
                "confidence_score": 0.0
            }
