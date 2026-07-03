import time
import structlog
from typing import List, Dict, Any, Tuple
from backend.app.ai.agents.symptom_extraction_agent import SymptomExtractionAgent
from backend.app.ai.agents.conversation_state_agent import ConversationStateAgent
from backend.app.ai.agents.follow_up_agent import FollowUpAgent
from backend.app.ai.agents.urgency_assessment_agent import UrgencyAssessmentAgent
from backend.app.ai.agents.consultation_summary_agent import ConsultationSummaryAgent
from backend.app.ai.consultation_schemas import ConsultationState, ConsultationStage, ConsultationSummary

logger = structlog.get_logger(__name__)

class ConsultationCrew:
    """Orchestrates the AI clinical interview workflow."""

    def __init__(self):
        self.symptom_extractor = SymptomExtractionAgent()
        self.state_agent = ConversationStateAgent()
        self.follow_up_agent = FollowUpAgent()
        self.urgency_agent = UrgencyAssessmentAgent()
        self.summary_agent = ConsultationSummaryAgent()

    async def run(self, chat_history: List[Dict[str, str]], latest_message: str) -> Dict[str, Any]:
        """Runs the pipeline for a single turn in the consultation."""
        t0 = time.perf_counter()
        logger.info("ConsultationCrew started")

        # Step 1: Extract Symptoms
        symptoms = await self.symptom_extractor.run(chat_history, latest_message)
        
        # Step 2: Determine Conversation State
        # (Pass the updated history including the latest user message)
        full_history = chat_history.copy()
        full_history.append({"sender": "user", "content": latest_message})
        
        state = await self.state_agent.run(full_history, symptoms)
        
        # Step 3: Assess Urgency
        urgency = await self.urgency_agent.run(symptoms)
        
        # Step 4: Determine Next Action (Follow-up vs Summary)
        response_text = ""
        summary_data = None
        
        if state.is_complete or state.current_stage == ConsultationStage.SUMMARY:
            # Generate final summary
            summary_data = await self.summary_agent.run(full_history, symptoms, urgency)
            response_text = "Thank you for providing all this information. I have compiled a summary of your consultation which you can view or download. Is there anything else you'd like to add or discuss?"
        else:
            # Generate follow-up question
            follow_up = await self.follow_up_agent.run(full_history, state, symptoms)
            response_text = follow_up.question
            
        elapsed = round((time.perf_counter() - t0) * 1000)
        logger.info("ConsultationCrew completed", elapsed_ms=elapsed, stage=state.current_stage)
        
        return {
            "response": response_text,
            "stage": state.current_stage,
            "progress": state.progress_percentage,
            "urgency": urgency.level,
            "symptoms": [s.model_dump() for s in symptoms],
            "summary": summary_data.model_dump() if summary_data else None,
            "is_complete": state.is_complete or state.current_stage == ConsultationStage.SUMMARY
        }
