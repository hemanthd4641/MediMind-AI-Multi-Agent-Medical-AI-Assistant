import structlog
from typing import List, Dict, Any
from backend.app.rag.retriever.vector_search import VectorSearch

logger = structlog.get_logger(__name__)

class CompatibilityVectorStore:
    """Compatibility wrapper that adapts the search calls from agents to the new Pinecone retriever."""
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        logger.info("CompatibilityVectorStore searching via Pinecone", query=query, top_k=top_k)
        # Pass None for db since VectorSearch.search does not use the db parameter in the Pinecone implementation.
        return VectorSearch.search(db=None, query=query, top_k=top_k)

vector_store = CompatibilityVectorStore()
