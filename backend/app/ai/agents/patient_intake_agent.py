"""Patient Intake Agent – extracts structured patient info from user message."""
from __future__ import annotations

import json
import re
import time
import structlog

from backend.app.ai.services.groq_llm_service import groq_llm_service
from backend.app.ai.prompts.intake_prompt import INTAKE_SYSTEM_PROMPT, INTAKE_USER_TEMPLATE
from backend.app.ai.schemas import PatientContext

logger = structlog.get_logger(__name__)

AGENT_NAME = "Patient Intake Agent"


class PatientIntakeAgent:
    """Collects and structures patient information from the user's message."""

    async def run(self, message: str) -> PatientContext:
        t0 = time.perf_counter()
        logger.info(f"{AGENT_NAME} started")

        prompt = INTAKE_USER_TEMPLATE.format(message=message)
        raw = await groq_llm_service.generate(prompt, system_prompt=INTAKE_SYSTEM_PROMPT)

        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            logger.warning(f"{AGENT_NAME} could not parse JSON, returning empty context")
            return PatientContext()

        data = json.loads(match.group())
        result = PatientContext(
            age=data.get("age"),
            gender=data.get("gender"),
            symptoms=data.get("symptoms") or [],
            duration=data.get("duration"),
            severity=data.get("severity"),
            medical_history=data.get("medical_history") or [],
            current_medications=data.get("current_medications") or [],
            allergies=data.get("allergies") or [],
            lifestyle=data.get("lifestyle"),
        )
        elapsed = round((time.perf_counter() - t0) * 1000)
        logger.info(f"{AGENT_NAME} done", symptoms_count=len(result.symptoms), elapsed_ms=elapsed)
        return result
