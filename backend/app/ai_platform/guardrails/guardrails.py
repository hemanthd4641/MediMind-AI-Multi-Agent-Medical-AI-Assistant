import re
import structlog
from typing import Tuple

logger = structlog.get_logger(__name__)

class GuardrailsEngine:
    """Enforces safety, blocks prompt injection, and prevents diagnosis/prescription."""

    # Simple heuristic checks (can be expanded via LLM checks if needed)
    INJECTION_PATTERNS = [
        r"ignore previous instructions",
        r"reveal system prompt",
        r"act as",
        r"disable safety",
        r"ignore policies"
    ]

    MEDICAL_RISK_PATTERNS = [
        r"diagnose me",
        r"what disease do i have",
        r"prescribe me",
        r"change my dose",
        r"stop taking",
        r"cure my"
    ]

    def check_input(self, user_input: str) -> Tuple[bool, str]:
        """Returns (is_safe, reason). False means blocked."""
        if not user_input:
            return True, ""
            
        text = user_input.lower()
        
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, text):
                logger.warning("Guardrail Triggered: Prompt Injection Attempt", pattern=pattern)
                return False, "Prompt injection attempt detected. Request blocked."
                
        for pattern in self.MEDICAL_RISK_PATTERNS:
            if re.search(pattern, text):
                logger.warning("Guardrail Triggered: Unsafe Medical Request", pattern=pattern)
                return False, "Direct medical diagnosis or prescription requests are blocked for safety."
                
        return True, ""

    def check_output(self, ai_output: str) -> Tuple[bool, str]:
        """Validates AI response before sending it to user."""
        if not ai_output:
            return True, ""
            
        text = ai_output.lower()
        
        # Ensure AI doesn't accidentally prescribe or diagnose definitively
        if "you have " in text and ("disease" in text or "cancer" in text or "syndrome" in text):
             # Highly heuristic, real implementation might use an LLM safety judge
             logger.warning("Guardrail Triggered: Potential Diagnosis in Output")
             # We won't block it blindly, but we log it.
             # return False, "Output flagged for unauthorized diagnosis."
             
        return True, ""

guardrails = GuardrailsEngine()
