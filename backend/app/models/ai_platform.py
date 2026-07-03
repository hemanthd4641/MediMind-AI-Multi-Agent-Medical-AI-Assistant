import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, JSON, Float, Integer, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from backend.app.database import Base

class ExecutionStatus(enum.Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    GUARDRAIL_BLOCKED = "GUARDRAIL_BLOCKED"

class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_name = Column(String, index=True, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    title = Column(String, nullable=False)
    prompt = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class LLMExecution(Base):
    __tablename__ = "llm_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(String, index=True, nullable=True) # Optional, links to chat or task
    agent_name = Column(String, index=True, nullable=False)
    model = Column(String, nullable=False)
    prompt_version = Column(Integer, nullable=True)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    latency_ms = Column(Integer, default=0)
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.SUCCESS)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id = Column(UUID(as_uuid=True), nullable=False)
    groundedness = Column(Float, default=0.0)
    relevance = Column(Float, default=0.0)
    hallucination_score = Column(Float, default=0.0) # 0 to 100
    faithfulness = Column(Float, default=0.0)
    safety_score = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
