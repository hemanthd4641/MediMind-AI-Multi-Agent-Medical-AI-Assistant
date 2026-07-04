"""
MedicalAIService – the only entry point for FastAPI routes to the AI layer.
FastAPI routes must NEVER interact with CrewAI directly.
"""
from __future__ import annotations

import time
import structlog
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.ai.crews.medical_crew import MedicalCrew
from backend.app.ai.schemas import MedicalResponse, IntentType, Citation
from backend.app.ai.services.consultation_engine import ConsultationEngine
from backend.app.ai.agents.fast_intent_router import FastIntentRouter
from backend.app.ai.services.groq_llm_service import groq_llm_service

logger = structlog.get_logger(__name__)

# Module-level instances (reused across requests)
_crew = MedicalCrew()
_engine = ConsultationEngine()
_fast_router = FastIntentRouter()


class MedicalAIService:
    """Facade over the MedicalCrew and Fast Routing – the only public AI interface."""

    async def process_request(self, message: str, user_id: str, db: Session | None = None) -> MedicalResponse:
        """Process a user message through the full AI pipeline."""
        logger.info("MedicalAIService.process_request", user_id=user_id, message_preview=message[:80])
        t0 = time.perf_counter()

        try:
            # 1. Fast Intent Routing
            intent = await _fast_router.run(message)
            logger.info("Query Routing Decision", detected_intent=intent.intent, confidence=intent.confidence)

            # 2. Path A: Simple Queries (Bypass CrewAI & RAG)
            if intent.intent in [IntentType.GREETING, IntentType.SMALL_TALK]:
                prompt = f"The user said: '{message}'. Respond as a helpful medical AI assistant briefly and kindly."
                response_text = await groq_llm_service.generate(prompt, system_prompt="You are a friendly medical AI assistant.")
                
                elapsed = round((time.perf_counter() - t0) * 1000)
                logger.info("Query Routing Execution", selected_agents=["FastIntentRouter"], namespace=None, response_time_ms=elapsed)
                
                return MedicalResponse(
                    intent=intent.intent,
                    response=response_text,
                    agents_used=["FastIntentRouter"],
                )

            # 3. Path B: General Medical Knowledge (Bypass CrewAI, use multiple knowledge namespaces)
            if intent.intent == IntentType.GENERAL_MEDICAL_KNOWLEDGE:
                from backend.app.ai.agents.medical_knowledge_agent import MedicalKnowledgeAgent
                k_agent = MedicalKnowledgeAgent()
                
                k_res = await k_agent.run(
                    message=message, 
                    patient_context=None, 
                    db=db,
                    namespaces=["medical_knowledge", "clinical_guidelines", "drug_database"]
                )
                response_text = k_res["response"]
                chunks = k_res.get("chunks", [])
                
                sources = []
                for i, chunk in enumerate(chunks):
                    doc_name = chunk.get("document_title") or chunk.get("file_name", "Unknown")
                    sources.append(Citation(document=doc_name, page=chunk.get("page_number"), chunk_index=i))
                    
                elapsed = round((time.perf_counter() - t0) * 1000)
                logger.info(
                    "Query Routing Execution", 
                    selected_agents=["FastIntentRouter", "MedicalKnowledgeAgent"], 
                    namespaces=["medical_knowledge", "clinical_guidelines", "drug_database"], 
                    retrieved_documents=len(chunks),
                    response_time_ms=elapsed
                )
                
                return MedicalResponse(
                    intent=intent.intent,
                    response=response_text,
                    agents_used=["FastIntentRouter", "MedicalKnowledgeAgent"],
                    sources=sources,
                    confidence=1.0 if chunks else 0.0,
                )

            # 4. Path C: Identity Document Query (Bypass CrewAI & ConsultationEngine, direct RAG)
            if intent.intent == IntentType.IDENTITY_DOCUMENT_QUERY:
                from backend.app.rag.retriever.vector_search import VectorSearch
                raw_chunks = VectorSearch.search(
                    db=db,
                    query=message,
                    top_k=3,
                    namespace="identity_documents",
                    metadata_filter={"patient_id": user_id} if user_id else None
                )
                
                evidence_str = ""
                sources = []
                if raw_chunks:
                    for i, chunk in enumerate(raw_chunks):
                        doc_name = chunk.get("document_title") or chunk.get("file_name", "Unknown")
                        evidence_str += f"[Source {i+1}: {doc_name}]\n{chunk['content']}\n\n"
                        sources.append(Citation(document=doc_name, page=chunk.get("page_number"), chunk_index=i))
                        
                prompt = (
                    f"User question: {message}\n\n"
                    f"Retrieved Identity Documents:\n{evidence_str}\n\n"
                    f"Answer the user's question clearly based ONLY on the documents. If no documents match, say so."
                )
                
                response_text = await groq_llm_service.generate(prompt, system_prompt="You are an AI assistant that reads identity documents.")
                elapsed = round((time.perf_counter() - t0) * 1000)
                
                logger.info(
                    "Query Routing Execution", 
                    selected_agents=["FastIntentRouter", "IdentityAgent"], 
                    namespace="identity_documents", 
                    response_time_ms=elapsed
                )
                
                return MedicalResponse(
                    intent=intent.intent,
                    response=response_text,
                    agents_used=["FastIntentRouter", "IdentityAgent"],
                    sources=sources,
                    confidence=1.0 if sources else 0.0,
                )

            # 5. Path D: Patient-Specific Routing (Use Consultation Engine & CrewAI)
            state, next_question, action = await _engine.process_message(user_id, message)
            
            enhanced_message = (
                f"--- STRUCTURED CONSULTATION STATE ---\n"
                f"{state.model_dump_json(indent=2)}\n"
                f"-------------------------------------\n\n"
                f"USER MESSAGE: {message}\n\n"
            )
            
            if action == "summarize":
                enhanced_message += "SYSTEM INSTRUCTION: All required clinical slots are completed. Generate a comprehensive clinical consultation summary based on the structured state."
            else:
                enhanced_message += f"SYSTEM INSTRUCTION: You must ask the following next question to the patient. Do not ask anything else. Be empathetic.\nNEXT QUESTION TO ASK: {next_question}"

            response = await _crew.run(message=enhanced_message, intent=intent, db=db, user_id=user_id)
            
            # Prepend FastIntentRouter to agents used
            response.agents_used = ["FastIntentRouter"] + response.agents_used
            
            elapsed = round((time.perf_counter() - t0) * 1000)
            logger.info("Query Routing Execution", selected_agents=response.agents_used, namespace="patient_reports_or_medications", response_time_ms=elapsed)
            
            return response
            
        except RuntimeError as exc:
            logger.error("AI pipeline error", user_id=user_id, error=str(exc))
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"AI service temporarily unavailable: {exc}",
            ) from exc
        except Exception as exc:
            logger.error("Unexpected AI error", user_id=user_id, error=str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred in the AI pipeline.",
            ) from exc


# Module-level singleton
medical_ai_service = MedicalAIService()

