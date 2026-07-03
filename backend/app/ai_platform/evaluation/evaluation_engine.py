import structlog
from typing import Dict, Any
from backend.app.models.ai_platform import EvaluationResult

logger = structlog.get_logger(__name__)

class EvaluationEngine:
    """Evaluates an AI response for groundedness, hallucinations, and safety."""

    def evaluate(self, execution_id: str, prompt: str, output: str, context: str = "") -> EvaluationResult:
        """
        Runs heuristics (and potentially an LLM judge) to score the output.
        For production, this would call a smaller fast model like LLaMA-3-8B to grade it.
        Here we use heuristic mocks for the architectural scaffolding.
        """
        logger.info("Evaluating AI execution", execution_id=execution_id)
        
        # 1. Groundedness check
        # If context is provided, check overlap
        groundedness = 1.0
        hallucination = 0.0
        
        if context:
            # Naive overlap score
            out_words = set(output.lower().split())
            ctx_words = set(context.lower().split())
            if len(out_words) > 0:
                overlap = len(out_words.intersection(ctx_words)) / len(out_words)
                groundedness = min(overlap * 2, 1.0) # Boosted for common words
                hallucination = max(1.0 - groundedness, 0.0) * 100

        # 2. Safety check
        safety_score = 1.0
        if "prescribe" in output.lower() or "diagnose" in output.lower():
            safety_score = 0.5 # Decreased if words appear, requires review
            
        # 3. Relevance & Faithfulness (Mocked for structural completeness)
        relevance = 0.95
        faithfulness = groundedness
        
        overall = (groundedness + relevance + faithfulness + safety_score) / 4.0
        
        result = EvaluationResult(
            execution_id=execution_id,
            groundedness=round(groundedness, 2),
            relevance=round(relevance, 2),
            hallucination_score=round(hallucination, 2),
            faithfulness=round(faithfulness, 2),
            safety_score=round(safety_score, 2),
            overall_score=round(overall, 2)
        )
        
        return result

evaluation_engine = EvaluationEngine()
