import structlog
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.deps import get_current_user
from backend.app.models.ai_platform import PromptTemplate, LLMExecution, EvaluationResult
from backend.app.ai_platform.prompt_manager.prompt_manager import prompt_manager
from backend.app.ai_platform.metrics.metrics_service import metrics_service
from backend.app.ai_platform.testing.test_framework import test_framework

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api/ai", tags=["AI Ops"])

# ---- DTOs ----
class PromptCreate(BaseModel):
    agent_name: str
    title: str
    prompt: str

class PromptRollback(BaseModel):
    version: int

# ---- Metrics & Dashboard ----
@router.get("/metrics")
def get_metrics(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Fetch high-level metrics for dashboard."""
    return metrics_service.get_dashboard_metrics(db)

@router.get("/executions")
def get_executions(limit: int = 50, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Fetch recent LLM Executions."""
    execs = db.query(LLMExecution).order_by(LLMExecution.created_at.desc()).limit(limit).all()
    return [{
        "id": str(e.id),
        "agent_name": e.agent_name,
        "model": e.model,
        "input_tokens": e.input_tokens,
        "output_tokens": e.output_tokens,
        "latency_ms": e.latency_ms,
        "status": e.status.value,
        "error_message": e.error_message,
        "created_at": e.created_at.isoformat()
    } for e in execs]

@router.get("/evaluations")
def get_evaluations(limit: int = 50, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Fetch recent evaluations."""
    evals = db.query(EvaluationResult).order_by(EvaluationResult.created_at.desc()).limit(limit).all()
    return [{
        "id": str(e.id),
        "execution_id": str(e.execution_id),
        "hallucination_score": e.hallucination_score,
        "groundedness": e.groundedness,
        "safety_score": e.safety_score,
        "overall_score": e.overall_score,
        "created_at": e.created_at.isoformat()
    } for e in evals]

# ---- Prompt Management ----
@router.get("/prompts")
def get_prompts(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """List all prompts."""
    prompts = prompt_manager.get_all_prompts(db)
    return [{
        "id": str(p.id),
        "agent_name": p.agent_name,
        "version": p.version,
        "title": p.title,
        "prompt": p.prompt,
        "is_active": p.is_active,
        "created_at": p.created_at.isoformat()
    } for p in prompts]

@router.post("/prompts")
def create_prompt(payload: PromptCreate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new prompt version."""
    new_p = prompt_manager.create_new_version(db, payload.agent_name, payload.title, payload.prompt)
    return {"message": "Created successfully", "version": new_p.version}

@router.put("/prompts/{agent_name}/rollback")
def rollback_prompt(agent_name: str, payload: PromptRollback, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Rollback to a specific version."""
    success = prompt_manager.rollback_version(db, agent_name, payload.version)
    if not success:
        raise HTTPException(status_code=404, detail="Version not found.")
    return {"message": f"Rolled back to version {payload.version}"}

# ---- Testing Framework ----
@router.post("/test-suite")
async def run_test_suite(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Trigger the automated AI test suite."""
    results = await test_framework.run_test_suite(db)
    return results
