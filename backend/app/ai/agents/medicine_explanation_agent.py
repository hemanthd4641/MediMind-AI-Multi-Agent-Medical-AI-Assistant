import structlog
import json
from typing import List, Dict, Any
from backend.app.ai.services.groq_llm_service import groq_llm_service
from backend.app.ai.services.vector_store import vector_store

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are an expert Medicine Explanation Agent.
Your job is to provide comprehensive educational explanations for a list of medicines.

Explain in patient-friendly terms but provide a dual-explanation (medical vs patient-friendly).
Do NOT prescribe, recommend dosage changes, or diagnose.
Always include a brief medical disclaimer.

You must return a valid JSON object matching this structure, where keys are medicine names:
{
  "Medicine_Name": {
    "purpose": "string",
    "food_interactions": "string",
    "alcohol_interactions": "string",
    "common_side_effects": "string",
    "serious_side_effects": "string",
    "missed_dose_guidance": "string",
    "storage_recommendations": "string",
    "safety_warnings": "string",
    "medical_explanation": "string (Technical explanation of mechanism)",
    "patient_friendly_explanation": "string (Simple explanation)",
    "confidence": "high or low (low if you do not recognize the medicine name)"
  }
}

DO NOT output any markdown blocks (like ```json), just output the raw JSON object.
"""

class MedicineExplanationAgent:
    """Provides educational explanations for medicines using RAG contexts."""

    async def run(self, medicines: List[str]) -> Dict[str, Dict[str, str]]:
        logger.info("MedicineExplanationAgent started")
        
        if not medicines:
            return {}
            
        # Retrieve RAG context for each medicine
        contexts = []
        for med in medicines:
            try:
                results = vector_store.search(f"What is {med}? Purpose, side effects, precautions.", top_k=2)
                for r in results:
                    contexts.append(f"Source for {med}: {r.get('content', '')}")
            except Exception as e:
                logger.warning(f"Failed to fetch RAG context for {med}", error=str(e))
                
        rag_context_str = "\n---\n".join(contexts)
        params_text = "\n".join([f"- {m}" for m in medicines])
        
        prompt = f"""Provide explanations for the following medicines:
{params_text}

Use this retrieved medical context if helpful (but prioritize general medical knowledge if context is lacking):
---
{rag_context_str}
---

Remember: ONLY output a valid JSON object.
"""
        try:
            result = await groq_llm_service.generate(prompt, system_prompt=SYSTEM_PROMPT)
            
            result = result.strip()
            if result.startswith("```json"):
                result = result[7:]
            if result.startswith("```"):
                result = result[3:]
            if result.endswith("```"):
                result = result[:-3]
            result = result.strip()
            
            data = json.loads(result)
            return data
            
        except json.JSONDecodeError as e:
            logger.error("MedicineExplanationAgent JSON parse error", error=str(e), response=result)
            return {}
        except Exception as e:
            logger.error("MedicineExplanationAgent error", error=str(e))
            return {}
