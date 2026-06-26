"""Emergency Detection Agent – determines urgency level (never diagnoses)."""
from __future__ import annotations

import json
import re
import time
import structlog

from backend.app.ai.services.groq_llm_service import groq_llm_service
from backend.app.ai.prompts.emergency_prompt import EMERGENCY_SYSTEM_PROMPT, EMERGENCY_USER_TEMPLATE
from backend.app.ai.schemas import EmergencyAssessment, EmergencyLevel

logger = structlog.get_logger(__name__)

AGENT_NAME = "Emergency Detection Agent"


class EmergencyDetectionAgent:
    """
    Determines whether the user needs urgent medical care.
    NEVER claims a diagnosis – only assesses urgency level.
    """

    async def run(self, message: str) -> EmergencyAssessment:
        t0 = time.perf_counter()
        logger.info(f"{AGENT_NAME} started")

        prompt = EMERGENCY_USER_TEMPLATE.format(message=message)
        raw = await groq_llm_service.generate(prompt, system_prompt=EMERGENCY_SYSTEM_PROMPT)

        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            logger.warning(f"{AGENT_NAME} could not parse JSON, defaulting to LOW")
            return EmergencyAssessment(
                level=EmergencyLevel.LOW,
                reason="Unable to assess – defaulted to LOW",
                recommended_action="Please consult a healthcare professional if you have concerns.",
            )

        data = json.loads(match.group())
        level_str = data.get("level", "LOW").upper()
        try:
            level = EmergencyLevel(level_str)
        except ValueError:
            level = EmergencyLevel.LOW

        result = EmergencyAssessment(
            level=level,
            reason=data.get("reason", ""),
            recommended_action=data.get("recommended_action", ""),
        )
        elapsed = round((time.perf_counter() - t0) * 1000)
        logger.info(f"{AGENT_NAME} done", level=result.level, elapsed_ms=elapsed)
        return result
