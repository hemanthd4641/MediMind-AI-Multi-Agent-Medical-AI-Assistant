import structlog
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.models.ai_platform import LLMExecution

logger = structlog.get_logger(__name__)

class MetricsService:
    """Aggregates LLM usage, latency, and cost estimates."""

    # Rough cost estimates per 1M tokens (e.g. Groq LLaMA3-70B)
    PRICE_PER_1M_INPUT = 0.59
    PRICE_PER_1M_OUTPUT = 0.79

    def get_dashboard_metrics(self, db: Session) -> dict:
        """Returns aggregate metrics for the dashboard."""
        
        total_executions = db.query(func.count(LLMExecution.id)).scalar() or 0
        total_input = db.query(func.sum(LLMExecution.input_tokens)).scalar() or 0
        total_output = db.query(func.sum(LLMExecution.output_tokens)).scalar() or 0
        avg_latency = db.query(func.avg(LLMExecution.latency_ms)).scalar() or 0
        
        # Calculate Cost
        cost = (total_input / 1_000_000 * self.PRICE_PER_1M_INPUT) + \
               (total_output / 1_000_000 * self.PRICE_PER_1M_OUTPUT)
               
        return {
            "total_executions": total_executions,
            "total_tokens": total_input + total_output,
            "input_tokens": total_input,
            "output_tokens": total_output,
            "average_latency_ms": round(avg_latency, 2),
            "estimated_cost_usd": round(cost, 4)
        }

metrics_service = MetricsService()
