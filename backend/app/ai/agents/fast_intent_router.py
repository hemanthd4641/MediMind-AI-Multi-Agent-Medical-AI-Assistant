import json
import re
import structlog
from typing import Dict, Any

from backend.app.ai.services.groq_llm_service import groq_llm_service
from backend.app.ai.schemas import IntentClassification, IntentType

logger = structlog.get_logger(__name__)

FAST_ROUTER_PROMPT = """
You are a highly efficient medical AI intent classifier.
Analyze the user's message and determine the correct intent from the following exact list:

- greeting
- general_medical_knowledge
- symptom_consultation
- medical_report_analysis
- prescription_analysis
- patient_history
- medication_question
- identity_document_query
- emergency
- small_talk

Rules for Classification:
1. "greeting": Simple greetings (e.g., "Hello", "Hi").
2. "general_medical_knowledge": Questions about diseases, general medical facts, biology, or conditions (e.g., "What is HIV?", "Symptoms of diabetes", "What causes dengue?"). 
3. "symptom_consultation": The user is describing their own current symptoms and wants medical advice or a consultation (e.g., "I have a headache and fever").
4. "medical_report_analysis": The user is asking to analyze a lab report, blood test, scan, or uploaded document, OR asking for their own specific medical metrics (e.g., "What does my lipid profile mean?", "What is my total cholesterol?", "What is my blood sugar?").
5. "prescription_analysis": The user wants you to read a prescription.
6. "patient_history": The user is asking about their past medical history.
7. "medication_question": The user is asking about specific drugs, their uses, side effects, or drug interactions.
8. "identity_document_query": The user is asking about their identity documents (e.g., "What is my Aadhaar number?", "My insurance details").
9. "emergency": The user is describing a critical, life-threatening situation (e.g., "chest pain", "can't breathe", "heavy bleeding").
10. "small_talk": Casual non-medical chat.

Return ONLY a JSON object with the following schema:
{{
    "intent": "<one of the 10 intents above>",
    "confidence": <float between 0.0 and 1.0>,
    "reason": "<short explanation>"
}}

User Message: "{message}"
"""

class FastIntentRouter:
    """A lightweight router that runs before CrewAI to quickly classify intent."""

    async def run(self, message: str) -> IntentClassification:
        prompt = FAST_ROUTER_PROMPT.format(message=message)
        system_prompt = "You are a fast intent classifier. Output ONLY valid JSON."
        
        try:
            res = await groq_llm_service.generate(prompt, system_prompt=system_prompt, agent_name="FastIntentRouter")
            
            # Extract JSON
            match = re.search(r"\{.*\}", res, re.DOTALL)
            if match:
                data = json.loads(match.group())
            else:
                data = json.loads(res)
                
            intent_str = data.get("intent", "small_talk").lower()
            confidence = float(data.get("confidence", 0.5))
            reason = str(data.get("reason", "Fallback parsed intent."))
            
            # Ensure it maps to the enum
            try:
                intent_enum = IntentType(intent_str)
            except ValueError:
                intent_enum = IntentType.SMALL_TALK
                
            return IntentClassification(
                intent=intent_enum,
                confidence=confidence,
                reason=reason
            )
        except Exception as e:
            logger.error("FastIntentRouter failed, falling back to small_talk", error=str(e))
            return IntentClassification(
                intent=IntentType.SMALL_TALK,
                confidence=0.1,
                reason="Error in parsing LLM response."
            )
