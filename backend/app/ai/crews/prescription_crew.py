import time
import structlog
from typing import Dict, Any, List

from backend.app.ai.agents.prescription_extraction_agent import PrescriptionExtractionAgent
from backend.app.ai.agents.medicine_explanation_agent import MedicineExplanationAgent
from backend.app.ai.agents.drug_interaction_agent import DrugInteractionAgent
from backend.app.ai.agents.allergy_agent import AllergyAgent
from backend.app.ai.agents.contraindication_agent import ContraindicationAgent
from backend.app.ai.agents.medication_schedule_agent import MedicationScheduleAgent
from backend.app.ai.agents.medication_summary_agent import MedicationSummaryAgent

logger = structlog.get_logger(__name__)

class PrescriptionCrew:
    """Orchestrates the AI Prescription Intelligence pipeline."""

    def __init__(self):
        self.extractor = PrescriptionExtractionAgent()
        self.explainer = MedicineExplanationAgent()
        self.interactor = DrugInteractionAgent()
        self.allergist = AllergyAgent()
        self.contra = ContraindicationAgent()
        self.scheduler = MedicationScheduleAgent()
        self.summarizer = MedicationSummaryAgent()

    async def run(self, raw_text: str, patient_allergies: List[str] = None, patient_chronic: List[str] = None, patient_history: List[str] = None) -> Dict[str, Any]:
        t0 = time.perf_counter()
        logger.info("PrescriptionCrew started")
        
        patient_allergies = patient_allergies or []
        patient_chronic = patient_chronic or []
        patient_history = patient_history or []

        # 1. Extraction
        extracted = await self.extractor.run(raw_text)
        medicines = extracted.get("medicines", [])
        medicine_names = [m.get("medicine_name") for m in medicines if m.get("medicine_name")]
        
        # 2. Parallel-ish Tasks (We run sequentially here for safety, but they are independent)
        # 2a. Explanations
        explanations = await self.explainer.run(medicine_names)
        # Attach explanations back to the medicines
        for m in medicines:
            m["educational_explanation"] = explanations.get(m.get("medicine_name"), "")
            
        # 2b. Interactions
        interactions = await self.interactor.run(medicine_names, patient_history, patient_chronic)
        
        # 2c. Allergies
        allergies = await self.allergist.run(medicine_names, patient_allergies)
        
        # 2d. Contraindications
        contraindications = await self.contra.run(medicine_names, patient_chronic)
        
        # 2e. Scheduling
        schedule = await self.scheduler.run(medicines)
        
        # 3. Final Summary
        summary = await self.summarizer.run(extracted, interactions, allergies, contraindications)
        
        elapsed = round((time.perf_counter() - t0) * 1000)
        logger.info("PrescriptionCrew completed", elapsed_ms=elapsed)
        
        return {
            "doctor_name": extracted.get("doctor_name"),
            "hospital_name": extracted.get("hospital_name"),
            "medicines": medicines,
            "interactions": interactions.get("interactions", []),
            "allergy_warnings": allergies.get("allergy_warnings", []),
            "contraindications": contraindications.get("contraindications", []),
            "schedule": schedule.get("schedule", {}),
            "summary": summary
        }
