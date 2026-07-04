"""Medical Knowledge Agent – retrieves evidence from Pinecone and answers grounded medical questions via Groq."""
from __future__ import annotations

import time
import structlog
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from backend.app.ai.services.groq_llm_service import groq_llm_service
from backend.app.ai.prompts.knowledge_prompt import KNOWLEDGE_SYSTEM_PROMPT, KNOWLEDGE_USER_TEMPLATE
from backend.app.ai.schemas import PatientContext
from backend.app.rag.retriever.vector_search import VectorSearch
from backend.app.rag.reranker.reranker import Reranker

logger = structlog.get_logger(__name__)

AGENT_NAME = "Medical Knowledge Agent"


class MedicalKnowledgeAgent:
    """
    Answers general medical questions by first retrieving context from the vector database.
    """

    async def run(
        self, 
        message: str, 
        patient_context: PatientContext | None = None, 
        db: Session | None = None,
        namespaces: List[str] = None,
        metadata_filter: dict = None
    ) -> Dict[str, Any]:
        """
        Returns a dict containing the "response" (str) and "chunks" (List[Dict]).
        """
        # Set default namespace if None
        from backend.app.vector_store import config as vs_config
        if not namespaces:
            namespaces = [vs_config.PINECONE_NAMESPACE_MEDICAL_KNOWLEDGE]

        t0 = time.perf_counter()
        logger.info(f"{AGENT_NAME} started", namespaces=namespaces)

        retrieved_chunks = []
        if db:
            # 1. Retrieve raw chunks
            raw_chunks = []
            for ns in namespaces:
                ns_chunks = VectorSearch.search(
                    db=db, 
                    query=message, 
                    top_k=5, 
                    namespace=ns, 
                    metadata_filter=metadata_filter
                )
                raw_chunks.extend(ns_chunks)
            
            # 2. Rerank
            retrieved_chunks = Reranker.rerank(message, raw_chunks) if raw_chunks else []
            
            # 3. Take top 5 after reranking
            retrieved_chunks = retrieved_chunks[:5]

        # 4. Formulate the Context String for the LLM
        evidence_str = ""
        if retrieved_chunks:
            evidence_parts = []
            for i, chunk in enumerate(retrieved_chunks):
                doc_name = chunk.get("document_title") or chunk.get("file_name", "Unknown")
                page = chunk.get("page_number", "?")
                evidence_parts.append(f"[Source {i+1}: {doc_name}, Page {page}]\n{chunk['content']}\n")
            evidence_str = "\n".join(evidence_parts)
        else:
            evidence_str = "No reliable medical evidence was found in the uploaded knowledge base."

        # Patient Context
        context_str = ""
        if patient_context and patient_context.symptoms:
            context_str = (
                f"Patient symptoms: {', '.join(patient_context.symptoms)}. "
                f"Duration: {patient_context.duration or 'unknown'}. "
                f"Severity: {patient_context.severity or 'unknown'}."
            )

        # Update the Prompt to include RAG evidence
        rag_prompt = (
            f"Here is the retrieved medical evidence from our knowledge base:\n"
            f"---\n{evidence_str}\n---\n\n"
            f"If the evidence says 'No reliable medical evidence was found', you MUST state this "
            f"clearly in your answer, but you may proceed to give general medical information while "
            f"indicating it is not grounded in the uploaded documents.\n\n"
            f"Otherwise, answer the user's question based strictly on the provided evidence. "
            f"Do not hallucinate.\n\n"
        )
        
        prompt = rag_prompt + KNOWLEDGE_USER_TEMPLATE.format(message=message, patient_context=context_str)
        
        result_text = await groq_llm_service.generate(prompt, system_prompt=KNOWLEDGE_SYSTEM_PROMPT)

        elapsed = round((time.perf_counter() - t0) * 1000)
        logger.info(f"{AGENT_NAME} done", elapsed_ms=elapsed, chunks_used=len(retrieved_chunks))
        
        return {
            "response": result_text,
            "chunks": retrieved_chunks
        }

