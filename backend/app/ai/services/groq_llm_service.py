"""
Groq LLM Service – singleton wrapper used by all CrewAI agents.
"""
from __future__ import annotations

import asyncio
import time
import os
import structlog
from groq import Groq, AsyncGroq, RateLimitError, APITimeoutError, APIConnectionError

from backend.app.config import settings
from backend.app.ai_platform.guardrails.guardrails import guardrails
from backend.app.ai_platform.evaluation.evaluation_engine import evaluation_engine
from backend.app.models.ai_platform import LLMExecution, ExecutionStatus

logger = structlog.get_logger(__name__)


class GroqLLMService:
    """Singleton Groq client with async `generate`, retries, structured logging, and MLOps tracking."""

    _instance: GroqLLMService | None = None

    def __new__(cls) -> GroqLLMService:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        
        # Determine API key from settings or env
        api_key = settings.GROQ_API_KEY if hasattr(settings, 'GROQ_API_KEY') else os.getenv("GROQ_API_KEY", "placeholder")
        self.client = AsyncGroq(api_key=api_key)
        
        self.model = getattr(settings, 'DEFAULT_MODEL', "llama3-70b-8192")
        self.temperature = getattr(settings, 'LLM_TEMPERATURE', 0.0)
        self._initialized = True
        logger.info("GroqLLMService initialized", model=self.model)

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful medical AI assistant.",
        max_retries: int = 3,
        agent_name: str = "Unknown",
        db_session = None,
        conversation_id: str = None
    ) -> str:
        """Call Groq asynchronously with retry/back-off and MLOps tracking.

        Args:
            prompt: User-facing prompt.
            system_prompt: Optional system-level context.
            max_retries: How many times to retry on transient errors.
            agent_name: Logical name of the agent calling this for tracking.
            db_session: Optional DB session to log the LLMExecution to.
            conversation_id: Optional UUID to group executions under one chat turn.

        Returns:
            The generated text content.

        Raises:
            RuntimeError: After all retries are exhausted.
        """
        
        # 1. Input Guardrails
        is_safe, reason = guardrails.check_input(prompt)
        if not is_safe:
            if db_session:
                exec_log = LLMExecution(
                    conversation_id=conversation_id,
                    agent_name=agent_name,
                    model=self.model,
                    status=ExecutionStatus.GUARDRAIL_BLOCKED,
                    error_message=reason
                )
                db_session.add(exec_log)
                db_session.commit()
            return f"Blocked: {reason}"
            
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        for attempt in range(1, max_retries + 1):
            try:
                t0 = time.perf_counter()
                
                logger.info(f"[{agent_name}] Calling Groq LLM API...", attempt=attempt)
                chat_completion = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=4000,
                )
                
                result = chat_completion.choices[0].message.content.strip()
                latency_ms = int((time.perf_counter() - t0) * 1000)
                
                # Token extraction from Groq response
                usage = chat_completion.usage
                in_tokens = usage.prompt_tokens if usage else 0
                out_tokens = usage.completion_tokens if usage else 0
                
                # 2. Output Guardrails
                is_out_safe, out_reason = guardrails.check_output(result)
                if not is_out_safe:
                    logger.warning("Output Guardrail Triggered", reason=out_reason)
                    result = f"Blocked by Output Guardrail: {out_reason}"
                
                # 3. Log Execution and Evaluate
                if db_session:
                    exec_log = LLMExecution(
                        conversation_id=conversation_id,
                        agent_name=agent_name,
                        model=self.model,
                        input_tokens=in_tokens,
                        output_tokens=out_tokens,
                        latency_ms=latency_ms,
                        status=ExecutionStatus.SUCCESS if is_out_safe else ExecutionStatus.GUARDRAIL_BLOCKED
                    )
                    db_session.add(exec_log)
                    db_session.commit()
                    db_session.refresh(exec_log)
                    
                    # Run Evaluation
                    eval_result = evaluation_engine.evaluate(str(exec_log.id), prompt, result)
                    db_session.add(eval_result)
                    db_session.commit()
                
                return result

            except RateLimitError as exc:
                logger.warning("Groq rate limit hit", attempt=attempt, error=str(exc))
                if attempt >= max_retries:
                    self._log_failure(db_session, conversation_id, agent_name, "Groq rate limit hit", exc)
                    raise RuntimeError("Groq rate limit – please retry later.") from exc
                await asyncio.sleep(2 ** attempt)

            except APITimeoutError as exc:
                logger.warning("Groq timeout", attempt=attempt, error=str(exc))
                if attempt >= max_retries:
                    self._log_failure(db_session, conversation_id, agent_name, "Groq timeout", exc)
                    raise RuntimeError("Groq request timed out.") from exc
                await asyncio.sleep(2 ** attempt)

            except APIConnectionError as exc:
                logger.error("Groq connection error", attempt=attempt, error=str(exc))
                if attempt >= max_retries:
                    self._log_failure(db_session, conversation_id, agent_name, "Groq connection error", exc)
                    raise RuntimeError("Groq is unavailable – connection error.") from exc
                await asyncio.sleep(2 ** attempt)

            except Exception as exc:
                logger.error("Groq unexpected error", attempt=attempt, error=str(exc))
                self._log_failure(db_session, conversation_id, agent_name, "Groq unexpected error", exc)
                raise RuntimeError(f"Groq error: {exc}") from exc

        raise RuntimeError("Groq generate exhausted all retries.")

    def _log_failure(self, db_session, conversation_id, agent_name, error_msg, exc):
        if db_session:
            exec_log = LLMExecution(
                conversation_id=conversation_id,
                agent_name=agent_name,
                model=self.model,
                status=ExecutionStatus.FAILED,
                error_message=f"{error_msg}: {str(exc)}"
            )
            db_session.add(exec_log)
            db_session.commit()

# Module-level singleton
groq_llm_service = GroqLLMService()
