import structlog
from typing import List, Dict, Any, Optional
from backend.app.vector_store.factory import VectorStoreFactory

logger = structlog.get_logger(__name__)

class VectorStoreService:
    """
    Facade service for vector database operations.
    Hides the underlying implementation (e.g. Pinecone) from the business logic.
    """

    def __init__(self):
        self.store = VectorStoreFactory.get_store()

    def upsert_chunk(self, chunk_id: str, text: str, embedding: List[float], metadata: Dict[str, Any], namespace: str):
        """Helper to upsert a single chunk."""
        # Embed the text into metadata so we can retrieve it
        metadata_copy = metadata.copy()
        metadata_copy["content"] = text
        self.store.upsert(chunk_id, embedding, metadata_copy, namespace)

    def upsert_batch(self, vectors: List[Dict[str, Any]], namespace: str):
        """
        Upsert a batch of vectors.
        Expected format for each vector dict:
        { "id": str, "values": List[float], "metadata": Dict[str, Any] }
        """
        self.store.upsert_batch(vectors, namespace)

    def query(self, query_embedding: List[float], top_k: int, namespace: str, filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Query vectors by similarity.
        Returns a list of dicts with keys: 'id', 'score', 'metadata'
        """
        return self.store.query(query_embedding, top_k, namespace, filter)

    def health_check(self) -> Dict[str, Any]:
        """Return the health status of the vector store connection."""
        return self.store.health_check()
        
    def list_namespaces(self) -> List[str]:
        return self.store.list_namespaces()

vector_store_service = VectorStoreService()
