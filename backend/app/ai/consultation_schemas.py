from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum

class UrgencyLevel(str, Enum):
    ROUTINE = "Routine"
    SOON = "Soon"
    URGENT = "Urgent"
    EMERGENCY = "Emergency"

class ConsultationStage(str, Enum):
    CHIEF_COMPLAINT = "Chief Complaint"
    SYMPTOM_DETAILS = "Symptom Details"
    MEDICAL_HISTORY = "Medical History"
    CURRENT_MEDICATION = "Current Medication"
    ALLERGIES = "Allergies"
    LIFESTYLE_FACTORS = "Lifestyle Factors"
    SUMMARY = "Summary"

class SymptomDetails(BaseModel):
    symptom: str = Field(description="The primary symptom reported")
    body_location: Optional[str] = Field(None, description="Where the symptom is located on the body")
    severity: Optional[str] = Field(None, description="How severe the symptom is (e.g., mild, moderate, severe, 8/10)")
    duration: Optional[str] = Field(None, description="How long the symptom has been present")
    triggers: Optional[List[str]] = Field(default_factory=list, description="Things that make the symptom worse or trigger it")
    associated_symptoms: Optional[List[str]] = Field(default_factory=list, description="Other symptoms occurring at the same time")
    frequency: Optional[str] = Field(None, description="How often the symptom occurs")

class ConsultationState(BaseModel):
    current_stage: ConsultationStage = Field(description="The current stage of the consultation")
    progress_percentage: int = Field(description="Percentage completion of the consultation (0-100)")
    missing_information: List[str] = Field(description="Information still needed for the current or upcoming stages")
    is_complete: bool = Field(default=False, description="Whether the consultation is ready for summary")

class FollowUpQuestion(BaseModel):
    question: str = Field(description="The next logical clinical question to ask")
    reason: str = Field(description="Why this question is being asked based on current missing information")

class UrgencyAssessment(BaseModel):
    level: UrgencyLevel = Field(description="The assessed urgency level")
    explanation: str = Field(description="Explanation for the assigned urgency level based on symptoms")

class ConsultationSummary(BaseModel):
    chief_complaint: str = Field(description="The primary reason for the consultation")
    symptoms: List[SymptomDetails] = Field(description="All structured symptoms collected")
    timeline: str = Field(description="Overall timeline of the illness/symptoms")
    relevant_medical_history: str = Field(description="Patient's past medical history")
    current_medications: str = Field(description="Medications the patient is currently taking")
    allergies: str = Field(description="Patient's allergies")
    lifestyle_factors: str = Field(description="Relevant lifestyle factors (smoking, alcohol, etc.)")
    risk_factors: List[str] = Field(description="Identified risk factors")
    urgency_level: UrgencyLevel = Field(description="Final urgency assessment")
    differential_diagnoses: List[str] = Field(description="AI-generated differential diagnoses, clearly labeled as possibilities.")
    recommended_specialty: str = Field(description="Recommended medical specialty for the patient to consult (e.g., Cardiology, General Practice).")
    suggested_diagnostic_tests: List[str] = Field(description="Suggested diagnostic tests that a doctor might order.")
    recommended_next_steps: List[str] = Field(description="Recommended next steps for the patient")
    medical_disclaimer: str = Field(default="This is an AI-generated summary for informational purposes only and does not constitute medical advice or a diagnosis. Please consult a qualified healthcare professional.", description="Standard medical disclaimer")
