import json
import re
import structlog
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Tuple, Optional

from backend.app.ai.services.groq_llm_service import groq_llm_service

logger = structlog.get_logger(__name__)

class ConsultationState(BaseModel):
    chief_complaint: str = ""
    symptoms: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    medical_history: List[str] = Field(default_factory=list)
    medications: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    lifestyle: Dict[str, str] = Field(default_factory=dict)
    completed_questions: List[str] = Field(default_factory=list)
    pending_questions: List[str] = Field(default_factory=list)
    consultation_stage: str = "initial"
    urgency: str = "unknown"

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

        # 2. Update State
        if intent in ["answering", "correcting", "greeting", "asking"]: 
            state = await self._update_state(message, state)
            state_manager.save_state(user_id, state)

        # 3. Slot Verification & Question Planning
        if intent == "requesting summary" or self._is_consultation_complete(state):
            return state, None, "summarize"
        
        next_question = await self._plan_next_question(state, message, intent)
        
        if next_question:
            state.completed_questions.append(next_question)
            state_manager.save_state(user_id, state)
            return state, next_question, "ask_question"
        
        return state, None, "summarize"

    async def _detect_intent(self, message: str, state: ConsultationState) -> str:
        prompt = f"""
Analyze the user's message in the context of a medical consultation.
Determine the intent of the message. 

Possible Intents:
- answering: Providing information to a previous question.
- asking: Asking a new medical or clarifying question.
- correcting: Correcting previous information.
- greeting: A general greeting.
- requesting summary: Asking to summarize the consultation.
- exhausted: The user indicates they have nothing more to add (e.g., "that's all", "nothing else", "no more", "that's it", "I don't know").

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
You are a structured clinical data extractor.
Update the following JSON consultation state based on the user's new message.
Extract the new information and merge it into the existing state.
NEVER overwrite existing information unless the user explicitly corrects it.

For symptoms, each symptom in the dictionary should ideally have these slots filled:
- duration
- severity
- location
- associated symptoms
- frequency
- triggers

If the user mentions a symptom but omits details, just leave those slots empty for that symptom.

Current State:
{state.model_dump_json(indent=2)}

User Message: "{message}"

Return ONLY the updated JSON state matching the exact same schema. Do not include markdown formatting or extra text.
"""
        try:
            res = await groq_llm_service.generate(prompt, system_prompt="You are a JSON state updater.", agent_name="ConsultationEngine")
            new_data = self._extract_json(res)
            
            # Keep completed/pending questions intact to avoid LLM hallucinating them away
            new_data["completed_questions"] = state.completed_questions
            new_data["pending_questions"] = state.pending_questions
            
            return ConsultationState(**new_data)
        except Exception as e:
            logger.error("State update failed", error=str(e))
            return state

    async def _plan_next_question(self, state: ConsultationState, last_message: str, intent: str) -> Optional[str]:
        prompt = f"""
You are a Clinical Question Planner. Generate ONLY ONE next best unanswered clinical question.

CRITICAL RULES:
1. NEVER ask generic questions like "Can you tell me more about that?" or "Is there anything else?". Instead, ask specific clinical questions that fill predefined slots (duration, severity, location, etc.).
2. MAXIMUM FOLLOW-UP LIMIT: Each symptom should have at most 3 follow-up questions. Review the Completed Questions. If a symptom has already been asked about 3 times, DO NOT ask about it again. Move to the next missing slot or category.
3. EXHAUSTED DETECTED: The user's last intent was "{intent}". If the intent is "exhausted" (e.g. they said "that's all" or "nothing else"), you MUST STOP asking about the current symptom and move to the next consultation stage (like Medical History or Medications).
4. If no meaningful follow-up exists for any category, output an empty string "". NEVER enter an infinite loop.

Prioritize filling missing information in this exact order:
1. Chief Complaint (if empty)
2. Symptom Details (if a symptom is missing duration, severity, location, associated symptoms, frequency, or triggers)
3. Medical History (if empty)
4. Medications (if empty)
5. Allergies (if empty)
6. Lifestyle (if empty)

Before generating a question, verify it is NOT in the list of completed questions. Never ask the same question twice.

Completed Questions:
{json.dumps(state.completed_questions)}

Current State:
{state.model_dump_json(indent=2)}

User's Last Message: "{last_message}"
User's Last Intent: "{intent}"

Return ONLY a JSON object with a single key "next_question" containing the string question (or empty string if none). Example: {{"next_question": "How long have you had this headache?"}}
"""
        try:
            res = await groq_llm_service.generate(prompt, system_prompt="You are a clinical question planner.", agent_name="ConsultationEngine")
            return self._extract_json(res).get("next_question", "")
        except Exception as e:
            logger.error("Question planning failed", error=str(e))
            return ""

    def _is_consultation_complete(self, state: ConsultationState) -> bool:
        if not state.chief_complaint: return False
        if not state.symptoms: return False
        
        # Check if basic slots for at least one symptom are somewhat filled
        for symptom, slots in state.symptoms.items():
            if not slots.get("duration") or not slots.get("severity"):
                return False
        return False

    def _extract_json(self, text: str) -> dict:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return {}
