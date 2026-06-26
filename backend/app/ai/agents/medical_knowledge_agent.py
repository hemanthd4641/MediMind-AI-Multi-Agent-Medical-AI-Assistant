"""Medical Knowledge Agent – answers general educational medical questions via Groq."""
from __future__ import annotations

import time
import structlog

from backend.app.ai.services.groq_llm_service import groq_llm_service
from backend.app.ai.prompts.knowledge_prompt import KNOWLEDGE_SYSTEM_PROMPT, KNOWLEDGE_USER_TEMPLATE
from backend.app.ai.schemas import PatientContext

logger = structlog.get_logger(__name__)

AGENT_NAME = "Medical Knowledge Agent"


class MedicalKnowledgeAgent:
    """
    Answers general medical questions using Groq only.
    Phase 3 does NOT use RAG – that comes in a later phase.
    """

    async def run(self, message: str, patient_context: PatientContext | None = None) -> str:
        t0 = time.perf_counter()
        logger.info(f"{AGENT_NAME} started")

        context_str = ""
        if patient_context and patient_context.symptoms:
            context_str = (
                f"Patient symptoms: {', '.join(patient_context.symptoms)}. "
                f"Duration: {patient_context.duration or 'unknown'}. "
                f"Severity: {patient_context.severity or 'unknown'}."
            )

        prompt = KNOWLEDGE_USER_TEMPLATE.format(message=message, patient_context=context_str)
        result = await groq_llm_service.generate(prompt, system_prompt=KNOWLEDGE_SYSTEM_PROMPT)

        elapsed = round((time.perf_counter() - t0) * 1000)
        logger.info(f"{AGENT_NAME} done", elapsed_ms=elapsed)
        return result
