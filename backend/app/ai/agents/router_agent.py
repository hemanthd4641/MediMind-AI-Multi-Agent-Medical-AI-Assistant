"""Router Agent – classifies user intent."""
from __future__ import annotations

import json
import re
import time
import structlog

from backend.app.ai.services.groq_llm_service import groq_llm_service
from backend.app.ai.prompts.router_prompt import ROUTER_SYSTEM_PROMPT, ROUTER_USER_TEMPLATE
from backend.app.ai.schemas import IntentClassification, IntentType

logger = structlog.get_logger(__name__)

AGENT_NAME = "Router Agent"


class RouterAgent:
    """Determines the intent of the user's message."""

    async def run(self, message: str) -> IntentClassification:
        t0 = time.perf_counter()
        logger.info(f"{AGENT_NAME} started", message_preview=message[:80])

        prompt = ROUTER_USER_TEMPLATE.format(message=message)
        raw = await groq_llm_service.generate(prompt, system_prompt=ROUTER_SYSTEM_PROMPT)

        # Extract JSON from response
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            logger.warning(f"{AGENT_NAME} could not parse JSON, defaulting to 'chat'")
            return IntentClassification(intent=IntentType.CHAT, confidence=0.5, reason="Parse error – defaulted to chat")

        data = json.loads(match.group())
        result = IntentClassification(
            intent=IntentType(data.get("intent", "chat")),
            confidence=float(data.get("confidence", 0.5)),
            reason=data.get("reason", ""),
        )
        elapsed = round((time.perf_counter() - t0) * 1000)
        logger.info(f"{AGENT_NAME} done", intent=result.intent, confidence=result.confidence, elapsed_ms=elapsed)
        return result
