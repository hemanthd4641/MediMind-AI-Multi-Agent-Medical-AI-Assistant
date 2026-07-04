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
    def search(
        db: Session, 
        query: str, 
        top_k: int = 5, 
        namespace: str = vs_config.PINECONE_NAMESPACE_MEDICAL_KNOWLEDGE,
        metadata_filter: dict = None
    ) -> List[Dict[str, Any]]:
        """
        Embeds the query and performs a nearest-neighbor search via Pinecone.
        Returns a list of dicts representing the top-k chunks.
        """
        import time
        t0 = time.perf_counter()
        
        logger.info("Generating query embedding", query=query, namespace=namespace)
        query_embedding = embedding_service.embed_query(query)
        
        logger.info("Querying Pinecone vector store", top_k=top_k, namespace=namespace, filter=metadata_filter)
        # Query Pinecone
        pinecone_results = vector_store_service.query(
            query_embedding=query_embedding,
            top_k=top_k,
            namespace=namespace,
            filter=metadata_filter
        )
        
        retrieved = []
        for match in pinecone_results:
            metadata = match.get("metadata", {})
            
            # Validation: Ensure it actually belongs to the requested namespace
            doc_namespace = metadata.get("namespace")
            if doc_namespace and doc_namespace != namespace:
                logger.warning("Namespace mismatch in retrieval - ignoring document", 
                               expected=namespace, got=doc_namespace, chunk_id=match.get("id"))
                continue
                
            # Validation: Enforce a minimum similarity threshold to prevent hallucination
            score = match.get("score", 0.0)
            if score < 0.65:
                logger.info("Chunk dropped due to low similarity score", score=score, threshold=0.65, chunk_id=match.get("id"))
                continue
                
            retrieved.append({
                "chunk_id": match.get("id"),
                "document_title": metadata.get("document_name", metadata.get("document_title", "")),
                "document_source": metadata.get("document_source", ""),
                "file_name": metadata.get("file_name", ""),
                "page_number": int(metadata.get("page_number", 1)),
                "content": metadata.get("content", ""),
                "similarity": match.get("score", 0.0),
                "metadata": metadata
            })
            
        elapsed_ms = round((time.perf_counter() - t0) * 1000)
        logger.info("Vector search complete", 
                    namespace=namespace,
                    chunks_found=len(retrieved),
                    response_time_ms=elapsed_ms)
                    
        return retrieved
