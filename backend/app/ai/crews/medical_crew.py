"""
Medical Crew – orchestrates all AI agents with dynamic routing.

Workflow:
  User Request
    → Router Agent          (always runs)
    → Patient Intake Agent  (runs for symptom/emergency/history intents)
    → Emergency Agent       (runs for symptom/emergency intents)
    → Medical Knowledge     (runs for medical question/symptom/drug/nutrition intents)
    → Response Composer     (always runs, combines all outputs)
"""
from __future__ import annotations

import time
import structlog

from backend.app.ai.agents.router_agent import RouterAgent
from backend.app.ai.agents.patient_intake_agent import PatientIntakeAgent
from backend.app.ai.agents.emergency_detection_agent import EmergencyDetectionAgent
from backend.app.ai.agents.medical_knowledge_agent import MedicalKnowledgeAgent
from backend.app.ai.agents.response_composer_agent import ResponseComposerAgent
from backend.app.ai.schemas import (
    EmergencyAssessment, EmergencyLevel,
    IntentClassification, IntentType,
    PatientContext, MedicalResponse,
)

logger = structlog.get_logger(__name__)

# Intents that trigger Patient Intake
INTAKE_INTENTS = {
    IntentType.SYMPTOM_CHECK,
    IntentType.EMERGENCY,
    IntentType.MEDICAL_HISTORY,
    IntentType.DRUG_INTERACTION,
    IntentType.PRESCRIPTION_ANALYSIS,
}

# Intents that trigger Emergency Detection
EMERGENCY_INTENTS = {
    IntentType.SYMPTOM_CHECK,
    IntentType.EMERGENCY,
}

# Intents that trigger Medical Knowledge
KNOWLEDGE_INTENTS = {
    IntentType.SYMPTOM_CHECK,
    IntentType.GENERAL_MEDICAL_QUESTION,
    IntentType.DRUG_INTERACTION,
    IntentType.NUTRITION,
    IntentType.REPORT_ANALYSIS,
    IntentType.PRESCRIPTION_ANALYSIS,
    IntentType.EMERGENCY,
}


class MedicalCrew:
    """Orchestrates the MediMind AI multi-agent pipeline."""

    def __init__(self) -> None:
        self.router = RouterAgent()
        self.intake = PatientIntakeAgent()
        self.emergency = EmergencyDetectionAgent()
        self.knowledge = MedicalKnowledgeAgent()
        self.composer = ResponseComposerAgent()

    async def run(self, message: str) -> MedicalResponse:
        t0 = time.perf_counter()
        agents_used: list[str] = []

        # ── Step 1: Router (always) ──────────────────────────────────────────
        agents_used.append("Router Agent")
        intent: IntentClassification = await self.router.run(message)
        logger.info("MedicalCrew routing decision", intent=intent.intent, confidence=intent.confidence)

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

        # ── Step 4: Medical Knowledge (conditional) ──────────────────────────
        knowledge_response = ""
        if intent.intent in KNOWLEDGE_INTENTS:
            agents_used.append("Medical Knowledge Agent")
            knowledge_response = await self.knowledge.run(message, patient_context)

        # ── Step 5: Response Composer (always) ───────────────────────────────
        agents_used.append("Response Composer Agent")
        response = await self.composer.run(
            message=message,
            intent=intent,
            emergency=emergency,
            patient_context=patient_context,
            knowledge_response=knowledge_response,
            agents_used=agents_used,
        )

        elapsed = round((time.perf_counter() - t0) * 1000)
        logger.info(
            "MedicalCrew completed",
            intent=intent.intent,
            agents_used=agents_used,
            emergency_level=emergency.level if emergency else None,
            elapsed_ms=elapsed,
        )
        return response
