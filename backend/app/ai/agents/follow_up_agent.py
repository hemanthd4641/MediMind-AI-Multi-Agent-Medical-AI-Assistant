import structlog
from typing import List, Dict, Any
from backend.app.ai.services.groq_llm_service import groq_llm_service
from backend.app.ai.consultation_schemas import FollowUpQuestion, ConsultationState, SymptomDetails
import json

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are an expert Clinical Follow-up Question Agent.
Based on the current consultation state, missing information, and extracted symptoms, generate the next single best clinical question.

Rules:
1. Ask exactly ONE question.
2. The question should be empathetic but direct and concise.
3. Use simple language.
4. If missing information is listed, ask about it (e.g. location, duration, severity, radiating pain).
5. Do NOT ask questions that have already been answered.

You must return a valid JSON object matching this structure:
{
  "question": "The question string",
  "reason": "Why this question is necessary"
}

DO NOT output any markdown blocks (like ```json), just output the raw JSON object.
"""

class FollowUpAgent:
    """Generates the next logical clinical question."""

    async def run(self, chat_history: List[Dict[str, str]], state: ConsultationState, symptoms: List[SymptomDetails]) -> FollowUpQuestion:
        logger.info("FollowUpAgent started", stage=state.current_stage)
        
        history_text = ""
        for msg in chat_history[-10:]:
            role = "Patient" if msg["sender"] == "user" else "AI"
            history_text += f"{role}: {msg['content']}\n"
            
        symptoms_text = "\n".join([s.model_dump_json() for s in symptoms])
        
        prompt = f"""Conversation History:
---
{history_text}
---

Current Stage: {state.current_stage}
Missing Information: {', '.join(state.missing_information)}

Extracted Symptoms:
---
{symptoms_text}
---

Generate the next best question. Remember: ONLY output a valid JSON object.
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
            return FollowUpQuestion(**data)
            
        except json.JSONDecodeError as e:
            logger.error("FollowUpAgent JSON parse error", error=str(e), response=result)
            # Safe fallback
            return FollowUpQuestion(
                question="Can you tell me a bit more about that?",
                reason="Fallback question due to parsing error."
            )
        except Exception as e:
            logger.error("FollowUpAgent error", error=str(e))
            return FollowUpQuestion(
                question="Can you tell me a bit more about that?",
                reason="Fallback question due to unexpected error."
            )
