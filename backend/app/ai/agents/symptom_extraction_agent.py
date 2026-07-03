import structlog
from typing import List, Dict, Any
from backend.app.ai.services.groq_llm_service import groq_llm_service
from backend.app.ai.consultation_schemas import SymptomDetails
import json
import re

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are an expert Clinical Symptom Extraction Agent.
Your job is to analyze the conversation between a patient and an AI medical assistant and extract structured symptom information.

You must return a valid JSON array of objects, where each object matches this structure:
{
  "symptom": "string (the primary symptom)",
  "body_location": "string or null",
  "severity": "string or null",
  "duration": "string or null",
  "triggers": ["string", "string"],
  "associated_symptoms": ["string", "string"],
  "frequency": "string or null"
}

If no symptoms are present, return an empty array [].
DO NOT output any markdown blocks (like ```json), just output the raw JSON array.
"""

class SymptomExtractionAgent:
    """Extracts structured symptoms from a consultation."""

    async def run(self, chat_history: List[Dict[str, str]], latest_message: str) -> List[SymptomDetails]:
        logger.info("SymptomExtractionAgent started")
        
        history_text = ""
        for msg in chat_history[-10:]:  # Consider last 10 messages for context
            role = "Patient" if msg["sender"] == "user" else "AI"
            history_text += f"{role}: {msg['content']}\n"
        
        history_text += f"Patient (Latest): {latest_message}\n"
        
        prompt = f"""Extract symptoms from the following conversation history:
---
{history_text}
---
Remember: ONLY output a valid JSON array.
"""
        try:
            result = await groq_llm_service.generate(prompt, system_prompt=SYSTEM_PROMPT)
            
            # Clean up response in case of markdown formatting
            result = result.strip()
            if result.startswith("```json"):
                result = result[7:]
            if result.startswith("```"):
                result = result[3:]
            if result.endswith("```"):
                result = result[:-3]
            result = result.strip()
            
            data = json.loads(result)
            if not isinstance(data, list):
                logger.error("SymptomExtractionAgent returned non-list JSON")
                return []
                
            symptoms = []
            for item in data:
                symptoms.append(SymptomDetails(**item))
            
            return symptoms
            
        except json.JSONDecodeError as e:
            logger.error("SymptomExtractionAgent JSON parse error", error=str(e), response=result)
            return []
        except Exception as e:
            logger.error("SymptomExtractionAgent error", error=str(e))
            return []
