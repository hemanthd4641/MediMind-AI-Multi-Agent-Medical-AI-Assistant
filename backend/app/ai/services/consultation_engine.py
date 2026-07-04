import json
import re
import structlog
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Tuple, Optional

from backend.app.ai.services.groq_llm_service import groq_llm_service

logger = structlog.get_logger(__name__)

class SymptomSlots(BaseModel):
    onset: str = ""
    duration: str = ""
    severity: str = ""
    location: str = ""
    associated_symptoms: List[str] = Field(default_factory=list)
    triggers: List[str] = Field(default_factory=list)
    relieving_factors: List[str] = Field(default_factory=list)

class ConsultationState(BaseModel):
    chief_complaint: str = ""
    symptoms: Dict[str, SymptomSlots] = Field(default_factory=dict)
    medical_history: List[str] = Field(default_factory=list)
    medications: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    lifestyle: Dict[str, str] = Field(default_factory=dict)
    family_history: List[str] = Field(default_factory=list)
    completed_questions: List[str] = Field(default_factory=list)
    pending_questions: List[str] = Field(default_factory=list)
    consultation_stage: str = "chief_complaint"
    red_flags: List[str] = Field(default_factory=list)
    urgency: str = "normal"

class ConsultationStateManager:
    def __init__(self):
        self._states: Dict[str, ConsultationState] = {}

    def get_state(self, user_id: str) -> ConsultationState:
        if user_id not in self._states:
            self._states[user_id] = ConsultationState()
        return self._states[user_id]

    def save_state(self, user_id: str, state: ConsultationState):
        self._states[user_id] = state

state_manager = ConsultationStateManager()

class ConsultationEngine:
    async def process_message(self, user_id: str, message: str) -> Tuple[ConsultationState, Optional[str], str]:
        state = state_manager.get_state(user_id)

        # 1. Intent Detection
        intent = await self._detect_intent(message, state)

        # 2. Update State & Detect Red Flags
        if intent in ["answering", "correcting", "greeting", "asking"]: 
            state = await self._update_state(message, state)
            state_manager.save_state(user_id, state)

        # 3. Emergency Intercept
        if state.urgency == "emergency":
            # Early exit for red flags - Trigger immediate warning
            return state, None, "emergency_warning"

        # 4. End Topic or Summary Request -> Move stage forward
        if intent == "exhausted":
            state = self._advance_stage(state)
            state_manager.save_state(user_id, state)

        if intent == "requesting summary" or self._is_consultation_complete(state):
            return state, None, "summarize"
        
        # 5. Slot Verification & Question Planning
        next_question = await self._plan_next_question(state, message, intent)
        
        if next_question:
            state.completed_questions.append(next_question)
            state_manager.save_state(user_id, state)
            return state, next_question, "ask_question"
        
        # Fallback if no questions generated but not complete
        return state, None, "summarize"

    def _advance_stage(self, state: ConsultationState) -> ConsultationState:
        """Move to the next logical stage if the user indicates they are done with the current one."""
        stages = ["chief_complaint", "symptom_details", "medical_history", "medications", "allergies", "lifestyle", "family_history", "complete"]
        if state.consultation_stage in stages:
            idx = stages.index(state.consultation_stage)
            if idx < len(stages) - 1:
                state.consultation_stage = stages[idx + 1]
        return state

    async def _detect_intent(self, message: str, state: ConsultationState) -> str:
        prompt = f"""
Analyze the user's message in the context of a clinical intake consultation.
Determine the intent of the message. 

Possible Intents:
- answering: Providing information to a previous question.
- asking: Asking a new medical or clarifying question.
- correcting: Correcting previous information.
- greeting: A general greeting.
- requesting summary: Asking to summarize the consultation.
- exhausted: The user indicates they have nothing more to add to the current topic (e.g., "that's all", "nothing else", "no more", "that's it", "I don't know").

User Message: "{message}"

Return ONLY a JSON object with a single key "intent" and string value. Example: {{"intent": "answering"}}
"""
        try:
            res = await groq_llm_service.generate(prompt, system_prompt="You are an intent detector.", agent_name="ConsultationEngine")
            return self._extract_json(res).get("intent", "answering").lower()
        except Exception as e:
            logger.error("Intent detection failed", error=str(e))
            return "answering"

    async def _update_state(self, message: str, state: ConsultationState) -> ConsultationState:
        prompt = f"""
You are a highly accurate clinical data extractor.
Update the following JSON consultation state based on the user's new message.

CRITICAL RULES:
1. NEVER overwrite or delete existing information unless the user explicitly corrects it.
2. For any symptom mentioned, fill in the nested slots (`onset`, `duration`, `severity`, `location`, `associated_symptoms`, `triggers`, `relieving_factors`). If a slot is not mentioned, leave it as an empty string (or empty list).
3. RED FLAG DETECTION: If the user mentions any emergency symptoms (e.g., severe chest pain, difficulty breathing, stroke symptoms, loss of consciousness, severe bleeding, suicidal thoughts), you MUST add them to the `red_flags` list and set `urgency` to "emergency". Otherwise, leave `urgency` as "normal" or whatever it was previously.

Current State:
{state.model_dump_json(indent=2)}

User Message: "{message}"

Return ONLY the updated JSON state matching the exact same schema. Do not include markdown formatting or extra text.
"""
        try:
            res = await groq_llm_service.generate(prompt, system_prompt="You are a clinical state updater.", agent_name="ConsultationEngine")
            new_data = self._extract_json(res)
            
            # Protect strictly managed lists
            new_data["completed_questions"] = state.completed_questions
            new_data["pending_questions"] = state.pending_questions
            
            # Ensure safe fallback for urgency
            if new_data.get("urgency") not in ["normal", "urgent", "emergency"]:
                new_data["urgency"] = state.urgency
                
            return ConsultationState(**new_data)
        except Exception as e:
            logger.error("State update failed", error=str(e))
            return state

    async def _plan_next_question(self, state: ConsultationState, last_message: str, intent: str) -> Optional[str]:
        prompt = f"""
You are a Clinical Question Planner acting as an experienced physician conducting an intake.
Generate ONLY ONE next best unanswered clinical question to ask the patient.

CRITICAL RULES:
1. NEVER ask generic questions like "Tell me more" or "Is there anything else?". You MUST ask exactly ONE clinically relevant question based on missing slots.
2. MAXIMUM FOLLOW-UP LIMIT: Do not ask more than 1 or 2 follow-ups per category if the patient is brief. You MUST review the Completed Questions to ensure you never ask the same or similar question twice.
3. ONE AT A TIME: Never ask compound questions (e.g., "What is the duration and severity?"). Pick exactly one slot.
4. GRACEFUL INTERRUPTION HANDLING: If the patient abruptly changes the topic or asks a question (intent is 'asking' or 'correcting'), answer briefly if appropriate, but gracefully steer them back to the MOST IMPORTANT missing clinical slot from the active stage.

PRIORITIZATION WATERFALL:
The current consultation stage is "{state.consultation_stage}". You MUST ask questions related to this stage.
If the stage is "chief_complaint", ask for the main reason for their visit.
If the stage is "symptom_details", check active `state.symptoms`. Pick one symptom and ask for missing critical slots (`onset`, `duration`, `severity`, `location`, `associated_symptoms`, `triggers`, `relieving_factors`).
If the stage is "medical_history", ask if they have any past medical conditions.
If the stage is "medications", ask if they are taking any medications currently.
If the stage is "allergies", ask if they have any known allergies.
If the stage is "lifestyle", ask briefly about smoking/alcohol or relevant lifestyle factors.
If the stage is "family_history", ask if there are any major medical conditions running in the family.

CRITICAL: Do NOT ask about symptoms if the stage is medical_history. Stay strictly within the current stage.

Completed Questions:
{json.dumps(state.completed_questions)}

Current State:
{state.model_dump_json(indent=2)}

User's Last Intent: "{intent}"

Based on the waterfall and current state, determine the single most important missing slot and ask a natural, empathetic question for it.
Return ONLY a JSON object with a single key "next_question" containing the string question. 
If all essential information is collected, return an empty string "".

Example: {{"next_question": "How long have you been experiencing this headache?"}}
"""
        try:
            res = await groq_llm_service.generate(prompt, system_prompt="You are a clinical question planner.", agent_name="ConsultationEngine")
            return self._extract_json(res).get("next_question", "")
        except Exception as e:
            logger.error("Question planning failed", error=str(e))
            return ""

    def _is_consultation_complete(self, state: ConsultationState) -> bool:
        if state.urgency == "emergency": return True
        if state.consultation_stage == "complete": return True
        
        # If we have basic history and medications, we consider it done
        if state.chief_complaint and state.symptoms:
            if len(state.completed_questions) > 12: 
                return True # Hard limit
        
        return False

    def _extract_json(self, text: str) -> dict:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return {}
