"""
Groq LLM Service – singleton wrapper used by all CrewAI agents.
"""
from __future__ import annotations

import asyncio
import time
import structlog
from groq import Groq, RateLimitError, APITimeoutError, APIConnectionError

from backend.app.config import settings

logger = structlog.get_logger(__name__)


class GroqLLMService:
    """Singleton Groq client with async `generate`, retries, and structured logging."""

    _instance: GroqLLMService | None = None

    def __new__(cls) -> GroqLLMService:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.DEFAULT_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self._initialized = True
        logger.info("GroqLLMService initialized", model=self.model)

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_retries: int = 3,
    ) -> str:
        """Call Groq asynchronously with retry/back-off.

        Args:
            prompt: User-facing prompt.
            system_prompt: Optional system-level context.
            max_retries: How many times to retry on transient errors.

        Returns:
            The generated text content.

        Raises:
            RuntimeError: After all retries are exhausted.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        for attempt in range(1, max_retries + 1):
            try:
                t0 = time.perf_counter()
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=self.temperature,
                        max_tokens=2048,
                    ),
                )
                latency_ms = round((time.perf_counter() - t0) * 1000)
                logger.info(
                    "Groq response received",
                    attempt=attempt,
                    latency_ms=latency_ms,
                    model=self.model,
                )
                return response.choices[0].message.content.strip()

            except RateLimitError as exc:
                logger.warning("Groq rate limit hit", attempt=attempt, error=str(exc))
                if attempt >= max_retries:
                    raise RuntimeError("Groq rate limit – please retry later.") from exc
                await asyncio.sleep(2 ** attempt)

            except APITimeoutError as exc:
                logger.warning("Groq timeout", attempt=attempt, error=str(exc))
                if attempt >= max_retries:
                    raise RuntimeError("Groq request timed out.") from exc
                await asyncio.sleep(2 ** attempt)

            except APIConnectionError as exc:
                logger.error("Groq connection error", attempt=attempt, error=str(exc))
                if attempt >= max_retries:
                    raise RuntimeError("Groq is unavailable – connection error.") from exc
                await asyncio.sleep(2 ** attempt)

            except Exception as exc:
                logger.error("Groq unexpected error", attempt=attempt, error=str(exc))
                raise RuntimeError(f"Groq error: {exc}") from exc

        raise RuntimeError("Groq generate exhausted all retries.")


# Module-level singleton
groq_llm_service = GroqLLMService()
