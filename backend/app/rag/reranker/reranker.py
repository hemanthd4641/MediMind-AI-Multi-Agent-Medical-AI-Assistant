import numpy as np
from typing import List, Dict, Any
from sklearn.metrics.pairwise import cosine_similarity
from backend.app.embeddings.service import embedding_service
import structlog
import re

logger = structlog.get_logger(__name__)

class Reranker:
    """
    Reranks retrieved chunks using a combination of similarity, keyword overlap, and medical relevance.
    """

    MEDICAL_TERMS = {
        "treatment", "symptom", "diagnosis", "patient", "disease", "syndrome", "therapy",
        "medication", "drug", "dose", "clinical", "trial", "hospital", "doctor", "blood",
        "pressure", "heart", "pain", "infection", "cancer", "diabetes", "guideline", "protocol"
    }

    @classmethod
    def score_keyword_overlap(cls, query: str, text: str) -> float:
        query_words = set(re.findall(r'\w+', query.lower()))
        if not query_words:
            return 0.0
        text_words = set(re.findall(r'\w+', text.lower()))
        overlap = query_words.intersection(text_words)
        return len(overlap) / len(query_words)

    @classmethod
    def score_medical_relevance(cls, text: str) -> float:
        text_words = set(re.findall(r'\w+', text.lower()))
        overlap = cls.MEDICAL_TERMS.intersection(text_words)
        # Cap at 1.0 (if they hit at least 3 terms, they get full points)
        return min(len(overlap) / 3.0, 1.0)

    @classmethod
    def rerank(cls, query: str, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not chunks:
            return []
            
        logger.info("Reranking chunks", count=len(chunks))
        
        for chunk in chunks:
            # chunk["similarity"] already contains the Pinecone cosine similarity score
            sim_score = chunk.get("similarity", 0.0)
            kw_score = cls.score_keyword_overlap(query, chunk["content"])
            med_score = cls.score_medical_relevance(chunk["content"])
            
            # Weighted combination (Similarity is most important)
            final_score = (sim_score * 0.7) + (kw_score * 0.2) + (med_score * 0.1)
            chunk["similarity"] = round(final_score, 4)

        # Sort descending by similarity
        chunks.sort(key=lambda x: x["similarity"], reverse=True)
        return chunks
