import structlog
import json
from typing import Dict, Any, List
from backend.app.ai.services.groq_llm_service import groq_llm_service

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are an expert Health Timeline Agent.
Your job is to read a list of raw chronological health events and generate a clean, unified patient timeline narrative.
Group the narrative logically (e.g. "Recent Activity", "Past 6 Months").

Return ONLY a valid JSON object:
{
  "timeline_narrative": "A unified story of the patient's health journey...",
  "key_events_highlighted": ["List", "of", "important", "milestones"]
}
DO NOT output any markdown blocks (like ```json).
"""

class TimelineAgent:
    """Generates a narrative from raw timeline events."""

    async def run(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        logger.info("TimelineAgent started")
        
        if not events:
            return {"timeline_narrative": "No health history recorded yet.", "key_events_highlighted": []}
            
        events_json = json.dumps(events, indent=2)
        prompt = f"Raw Events:\n{events_json}\nGenerate the timeline narrative. ONLY valid JSON."
        
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
            
            return json.loads(result)
        except Exception as e:
            logger.error("TimelineAgent error", error=str(e))
            return {"timeline_narrative": "Failed to generate narrative.", "key_events_highlighted": []}
