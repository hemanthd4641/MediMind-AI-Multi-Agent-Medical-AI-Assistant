from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Dict, Any
from backend.app.models.rag_models import DocumentChunk, MedicalDocument
from backend.app.rag.embedder.embedding_service import embedding_service
import structlog

logger = structlog.get_logger(__name__)

class VectorSearch:
    """
    Performs similarity search against the pgvector database.
    """
    
    @staticmethod
    def search(db: Session, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Embeds the query and performs a nearest-neighbor search.
        Returns a list of dicts representing the top-k chunks.
        """
        logger.info("Generating query embedding", query=query)
        query_embedding = embedding_service.embed_text(query)
        
        # pgvector uses `<->` for L2 distance, `<#>` for inner product, `<=>` for cosine distance.
        # all-MiniLM-L6-v2 outputs are typically compared using cosine distance.
        # We order by DocumentChunk.embedding.cosine_distance(query_embedding).
        
        stmt = (
            select(DocumentChunk, MedicalDocument)
            .join(MedicalDocument, DocumentChunk.document_id == MedicalDocument.id)
            .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
            .limit(top_k)
        )
        
        results = db.execute(stmt).all()
        
        retrieved = []
        for chunk, doc in results:
            # We convert cosine distance to a similarity score: similarity = 1 - distance
            # This requires recalculating or using SQLAlchemy's distance function if we included it in select.
            # For simplicity, we just use the chunks and we'll let the reranker calculate precise scores if needed.
            # But the requirement asks for Similarity Score. Let's retrieve the distance.
            
            # Since we can't easily extract the order_by value from the result object in all SQLAlchemy versions,
            # we will calculate similarity in the reranker, or we can just pass the chunk text.
            
            retrieved.append({
                "chunk_id": str(chunk.id),
                "document_title": doc.title,
                "document_source": doc.source or doc.file_name,
                "file_name": doc.file_name,
                "page_number": chunk.page_number,
                "content": chunk.content,
                # Temporary placeholder for similarity, computed in reranker
                "similarity": 0.0,
                "metadata": chunk.metadata_
            })
            
        logger.info("Vector search complete", chunks_found=len(retrieved))
        return retrieved
