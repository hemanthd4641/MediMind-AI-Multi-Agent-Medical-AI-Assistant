"""Response Composer Agent – combines all agent outputs into a single professional response."""
from __future__ import annotations

import time
import structlog

from backend.app.ai.services.groq_llm_service import groq_llm_service
from backend.app.ai.prompts.composer_prompt import COMPOSER_SYSTEM_PROMPT, COMPOSER_USER_TEMPLATE
from backend.app.ai.schemas import EmergencyAssessment, IntentClassification, PatientContext, MedicalResponse

logger = structlog.get_logger(__name__)

AGENT_NAME = "Response Composer Agent"


class ResponseComposerAgent:
    """Composes the final healthcare-friendly response from all prior agents."""

    async def run(
        self,
        message: str,
        intent: IntentClassification,
        emergency: EmergencyAssessment | None,
        patient_context: PatientContext | None,
        knowledge_response: str,
        agents_used: list[str],
    ) -> MedicalResponse:
        t0 = time.perf_counter()
        logger.info(f"{AGENT_NAME} started", intent=intent.intent)

        emergency_level = emergency.level if emergency else "N/A"
        patient_ctx_str = ""
        if patient_context:
            parts = []
            if patient_context.symptoms:
                parts.append(f"Symptoms: {', '.join(patient_context.symptoms)}")
            if patient_context.age:
                parts.append(f"Age: {patient_context.age}")
            if patient_context.severity:
                parts.append(f"Severity: {patient_context.severity}")
            patient_ctx_str = "; ".join(parts) if parts else "No specific context provided."

        prompt = COMPOSER_USER_TEMPLATE.format(
            message=message,
            intent=intent.intent,
            emergency_level=emergency_level,
            patient_context=patient_ctx_str,
            knowledge_response=knowledge_response,
        )
        composed = await groq_llm_service.generate(prompt, system_prompt=COMPOSER_SYSTEM_PROMPT)

        elapsed = round((time.perf_counter() - t0) * 1000)
        logger.info(f"{AGENT_NAME} done", elapsed_ms=elapsed)

        return MedicalResponse(
            intent=intent.intent,
            response=composed,
            agents_used=agents_used,
            emergency_level=emergency.level if emergency else None,
        )
