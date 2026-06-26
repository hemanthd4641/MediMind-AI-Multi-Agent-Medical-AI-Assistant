import numpy as np
from typing import List, Dict, Any
from sklearn.metrics.pairwise import cosine_similarity
from backend.app.rag.embedder.embedding_service import embedding_service
import re

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

        # Re-compute cosine similarity to get exact scores
        query_emb = np.array(embedding_service.embed_text(query)).reshape(1, -1)
        chunk_texts = [c["content"] for c in chunks]
        chunk_embs = np.array(embedding_service.embed_texts(chunk_texts))
        
        similarities = cosine_similarity(query_emb, chunk_embs)[0]

        for i, chunk in enumerate(chunks):
            sim_score = float(similarities[i])
            kw_score = cls.score_keyword_overlap(query, chunk["content"])
            med_score = cls.score_medical_relevance(chunk["content"])
            
            # Weighted combination (Similarity is most important)
            final_score = (sim_score * 0.7) + (kw_score * 0.2) + (med_score * 0.1)
            chunk["similarity"] = round(final_score, 4)

        # Sort descending by similarity
        chunks.sort(key=lambda x: x["similarity"], reverse=True)
        return chunks
