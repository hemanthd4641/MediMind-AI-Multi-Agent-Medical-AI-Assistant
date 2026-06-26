"""Pydantic output models for Phase 3 AI orchestration."""
from __future__ import annotations
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


# ── Intent ──────────────────────────────────────────────────────────────────

class IntentType(str, Enum):
    SYMPTOM_CHECK = "symptom_check"
    GENERAL_MEDICAL_QUESTION = "general_medical_question"
    REPORT_ANALYSIS = "report_analysis"
    PRESCRIPTION_ANALYSIS = "prescription_analysis"
    DRUG_INTERACTION = "drug_interaction"
    NUTRITION = "nutrition"
    APPOINTMENT = "appointment"
    EMERGENCY = "emergency"
    CHAT = "chat"
    MEDICAL_HISTORY = "medical_history"


class IntentClassification(BaseModel):
    intent: IntentType = Field(..., description="Detected user intent")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0–1")
    reason: str = Field(..., description="Short explanation for the classification")


# ── Emergency ────────────────────────────────────────────────────────────────

class EmergencyLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EmergencyAssessment(BaseModel):
    level: EmergencyLevel = Field(..., description="Urgency level")
    reason: str = Field(..., description="Why this level was chosen")
    recommended_action: str = Field(..., description="What the user should do")


# ── Patient Context ──────────────────────────────────────────────────────────

class PatientContext(BaseModel):
    age: Optional[str] = None
    gender: Optional[str] = None
    symptoms: List[str] = Field(default_factory=list)
    duration: Optional[str] = None
    severity: Optional[str] = None
    medical_history: List[str] = Field(default_factory=list)
    current_medications: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    lifestyle: Optional[str] = None


# ── Final Response ───────────────────────────────────────────────────────────

class Citation(BaseModel):
    document: str = Field(..., description="Document source or file name")
    page: Optional[int] = Field(None, description="Page number of the citation")
    chunk_index: Optional[int] = Field(None, description="Internal chunk index")

class MedicalResponse(BaseModel):
    intent: str = Field(..., description="Classified intent")
    response: str = Field(..., description="AI-generated healthcare response")
    agents_used: List[str] = Field(default_factory=list, description="Agents that participated")
    emergency_level: Optional[str] = Field(None, description="Emergency level if assessed")
    
    # RAG Citations
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence in the response based on retrieved evidence")
    sources: List[Citation] = Field(default_factory=list, description="Citations from the knowledge base used for this response")
    evidence_summary: Optional[str] = Field(None, description="Brief summary of the evidence used")

    disclaimer: str = Field(
        default=(
            "⚠️ This information is for educational purposes only and does not constitute "
            "medical advice. Always consult a qualified healthcare professional for diagnosis "
            "and treatment."
        )
    )


# ── API Request ──────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User's message to the AI system")
