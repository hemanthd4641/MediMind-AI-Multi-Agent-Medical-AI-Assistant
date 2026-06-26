import structlog
from typing import List, Dict, Any
from backend.app.ai.schemas import Citation
import numpy as np

logger = structlog.get_logger(__name__)

AGENT_NAME = "Citation Agent"

class CitationAgent:
    """
    Parses retrieved chunks and generates citations, calculating an overall confidence score.
    """

    async def run(self, retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Takes the chunks used by the knowledge agent and returns citation objects and confidence.
        """
        logger.info(f"{AGENT_NAME} started", total_chunks=len(retrieved_chunks))

        if not retrieved_chunks:
            return {
                "sources": [],
                "confidence": 0.0,
                "evidence_summary": "No reliable medical evidence was found in the uploaded knowledge base."
            }

        sources = []
        similarities = []
        
        for chunk in retrieved_chunks:
            source = Citation(
                document=chunk.get("document_title") or chunk.get("file_name", "Unknown Document"),
                page=chunk.get("page_number"),
                chunk_index=chunk.get("chunk_index")
            )
            # Avoid duplicates if multiple chunks from the same page
            if not any(s.document == source.document and s.page == source.page for s in sources):
                sources.append(source)
            
            if "similarity" in chunk:
                similarities.append(chunk["similarity"])

        # Calculate a basic confidence score based on the highest and average similarity
        confidence = 0.0
        if similarities:
            # We scale the similarity to a 0.0 - 1.0 confidence.
            # Reranker similarity can be anything, but usually cosine is 0-1.
            # We will just cap at 1.0.
            max_sim = max(similarities)
            avg_sim = sum(similarities) / len(similarities)
            # Give more weight to having at least one highly similar chunk
            confidence = min(max_sim * 0.7 + avg_sim * 0.3, 1.0)
            
            # Ensure it's bounded safely
            confidence = max(0.0, min(confidence, 1.0))

        # Basic evidence summary
        summary = f"Found {len(sources)} distinct sources from the knowledge base to answer the query."

        logger.info(f"{AGENT_NAME} done", confidence=confidence, sources_count=len(sources))

        return {
            "sources": sources,
            "confidence": round(confidence, 2),
            "evidence_summary": summary
        }
