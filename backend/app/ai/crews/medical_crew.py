"""
Medical Crew – orchestrates AI agents with dynamic routing.

Workflow:
  User Request -> FastIntentRouter (external) -> MedicalCrew
    → Patient Intake Agent  (runs for symptom/history/emergency intents)
    → Emergency Agent       (runs for symptom/emergency intents)
    → Medical Knowledge     (runs for RAG dependent intents)
    → Citation Agent        (runs if knowledge agent retrieves chunks)
    → Response Composer     (always runs, combines all outputs)
"""
from __future__ import annotations

import time
import structlog
from sqlalchemy.orm import Session

from backend.app.ai.agents.patient_intake_agent import PatientIntakeAgent
from backend.app.ai.agents.emergency_detection_agent import EmergencyDetectionAgent
from backend.app.ai.agents.medical_knowledge_agent import MedicalKnowledgeAgent
from backend.app.ai.agents.citation_agent import CitationAgent
from backend.app.ai.agents.response_composer_agent import ResponseComposerAgent
from backend.app.ai.schemas import (
    EmergencyAssessment, EmergencyLevel,
    IntentClassification, IntentType,
    PatientContext, MedicalResponse, Citation
)
from backend.app.vector_store import config as vs_config

logger = structlog.get_logger(__name__)

# Intents that trigger Patient Intake
INTAKE_INTENTS = {
    IntentType.SYMPTOM_CONSULTATION,
    IntentType.EMERGENCY,
    IntentType.PATIENT_HISTORY,
    IntentType.MEDICATION_QUESTION,
    IntentType.PRESCRIPTION_ANALYSIS,
}

# Intents that trigger Emergency Detection
EMERGENCY_INTENTS = {
    IntentType.SYMPTOM_CONSULTATION,
    IntentType.EMERGENCY,
}

# Intents that trigger Medical Knowledge (CrewAI-bound RAG)
KNOWLEDGE_INTENTS = {
    IntentType.SYMPTOM_CONSULTATION,
    IntentType.MEDICATION_QUESTION,
    IntentType.MEDICAL_REPORT_ANALYSIS,
    IntentType.PRESCRIPTION_ANALYSIS,
    IntentType.EMERGENCY,
    IntentType.PATIENT_HISTORY,
    IntentType.IDENTITY_DOCUMENT_QUERY,
}


class MedicalCrew:
    """Orchestrates the MediMind AI multi-agent pipeline."""

    def __init__(self) -> None:
        self.intake = PatientIntakeAgent()
        self.emergency = EmergencyDetectionAgent()
        self.knowledge = MedicalKnowledgeAgent()
        self.citation = CitationAgent()
        self.composer = ResponseComposerAgent()

    async def run(
        self, 
        message: str, 
        intent: IntentClassification, 
        db: Session | None = None,
        user_id: str | None = None
    ) -> MedicalResponse:
        t0 = time.perf_counter()
        agents_used: list[str] = []

        logger.info("MedicalCrew execution started", intent=intent.intent, confidence=intent.confidence)

        # ── Step 2: Patient Intake (conditional) ─────────────────────────────
        patient_context: PatientContext | None = None
        if intent.intent in INTAKE_INTENTS:
            agents_used.append("Patient Intake Agent")
            patient_context = await self.intake.run(message)

        # ── Step 3: Emergency Detection (conditional) ────────────────────────
        emergency: EmergencyAssessment | None = None
        if intent.intent in EMERGENCY_INTENTS:
            agents_used.append("Emergency Detection Agent")
            emergency = await self.emergency.run(message)
            logger.info("Emergency assessment", level=emergency.level)

        # ── Step 4: Medical Knowledge & Citations (conditional) ───────────────
        knowledge_response = ""
        citation_data = {
            "sources": [],
            "confidence": 0.0,
            "evidence_summary": None
        }
        
        if intent.intent in KNOWLEDGE_INTENTS:
            agents_used.append("Medical Knowledge Agent")
            
            # Determine namespace based on intent
            namespaces = ["patient_reports"]
            if intent.intent in [IntentType.MEDICATION_QUESTION, IntentType.PRESCRIPTION_ANALYSIS]:
                namespaces = ["prescriptions"]
            elif intent.intent == IntentType.IDENTITY_DOCUMENT_QUERY:
                namespaces = ["identity_documents"]
            
            # Add patient_id to metadata_filter if querying patient-specific data
            metadata_filter = None
            if user_id:
                metadata_filter = {"patient_id": user_id}
                
            k_res = await self.knowledge.run(
                message=message, 
                patient_context=patient_context, 
                db=db,
                namespaces=namespaces,
                metadata_filter=metadata_filter
            )
            knowledge_response = k_res["response"]
            
            chunks = k_res.get("chunks", [])
            if chunks:
                agents_used.append("Citation Agent")
                citation_data = await self.citation.run(chunks)

        # ── Step 5: Response Composer (always) ───────────────────────────────
        agents_used.append("Response Composer Agent")
        final_response = await self.composer.run(
            message=message,
            intent=intent,
            emergency=emergency,
            patient_context=patient_context,
            knowledge_response=knowledge_response,
            agents_used=agents_used,
        )
        
        # Attach citations to the final MedicalResponse
        final_response.sources = citation_data.get("sources", [])
        final_response.confidence = citation_data.get("confidence", 0.0)
        final_response.evidence_summary = citation_data.get("evidence_summary")

        elapsed = round((time.perf_counter() - t0) * 1000)
        logger.info(
            "MedicalCrew completed",
            intent=intent.intent,
            agents_used=agents_used,
            emergency_level=emergency.level if emergency else None,
            elapsed_ms=elapsed,
        )
        return final_response

