"""Pydantic output models for Phase 3 AI orchestration."""
from __future__ import annotations
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


# ── Intent ──────────────────────────────────────────────────────────────────

class IntentType(str, Enum):
    GREETING = "greeting"
    GENERAL_MEDICAL_KNOWLEDGE = "general_medical_knowledge"
    SYMPTOM_CONSULTATION = "symptom_consultation"
    MEDICAL_REPORT_ANALYSIS = "medical_report_analysis"
    PRESCRIPTION_ANALYSIS = "prescription_analysis"
    PATIENT_HISTORY = "patient_history"
    MEDICATION_QUESTION = "medication_question"
    IDENTITY_DOCUMENT_QUERY = "identity_document_query"
    EMERGENCY = "emergency"
    SMALL_TALK = "small_talk"


class IntentClassification(BaseModel):
    intent: IntentType = Field(..., description="Detected user intent")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0–1")
    reason: str = Field(..., description="Short explanation for the classification")


class DocumentClassification(BaseModel):
    document_type: str = Field(..., description="The type of the document")
    namespace: str = Field(..., description="The Pinecone namespace for the document")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")


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
