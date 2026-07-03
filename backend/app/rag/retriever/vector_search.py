from sqlalchemy.orm import Session
from typing import List, Dict, Any
from backend.app.embeddings.service import embedding_service
from backend.app.vector_store.service import vector_store_service
from backend.app.vector_store import config as vs_config
import structlog

logger = structlog.get_logger(__name__)

class VectorSearch:
    """
    Performs similarity search against Pinecone Cloud.
    Maintains the identical return signature as the old pgvector implementation.
    """
    
    @staticmethod
    def search(db: Session, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Embeds the query and performs a nearest-neighbor search via Pinecone.
        Returns a list of dicts representing the top-k chunks.
        """
        logger.info("Generating query embedding", query=query)
        query_embedding = embedding_service.embed_query(query)
        
        logger.info("Querying Pinecone vector store", top_k=top_k)
        # Query Pinecone
        pinecone_results = vector_store_service.query(
            query_embedding=query_embedding,
            top_k=top_k,
            namespace=vs_config.PINECONE_NAMESPACE_MEDICAL_KNOWLEDGE
        )
        
        retrieved = []
        for match in pinecone_results:
            metadata = match["metadata"]
            retrieved.append({
                "chunk_id": match["id"],
                "document_title": metadata.get("document_title", ""),
                "document_source": metadata.get("document_source", ""),
                "file_name": metadata.get("file_name", ""),
                "page_number": int(metadata.get("page_number", 1)),
                "content": metadata.get("content", ""),
                "similarity": match.get("score", 0.0),
                "metadata": metadata
            })
            
        logger.info("Vector search complete", chunks_found=len(retrieved))
        return retrieved
