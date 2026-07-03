from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class VectorStore(ABC):
    """Abstract base class for all Vector Store providers (e.g. Pinecone, Weaviate, pgvector)."""

    @abstractmethod
    def create_index(self, dimension: int):
        """Create the index if it does not exist."""
        pass

    @abstractmethod
    def delete_index(self):
        """Delete the entire index."""
        pass

    @abstractmethod
    def upsert(self, chunk_id: str, embedding: List[float], metadata: Dict[str, Any], namespace: str):
        """Upsert a single vector with metadata."""
        pass

    @abstractmethod
    def upsert_batch(self, vectors: List[Dict[str, Any]], namespace: str):
        """
        Upsert a batch of vectors.
        Expected format for each vector dict:
        { "id": str, "values": List[float], "metadata": Dict[str, Any] }
        """
        pass

    @abstractmethod
    def query(self, query_embedding: List[float], top_k: int, namespace: str, filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Query vectors by similarity.
        Returns a list of dicts with keys: 'id', 'score', 'metadata'
        """
        pass

    @abstractmethod
    def delete(self, ids: List[str], namespace: str):
        """Delete vectors by ID."""
        pass

    @abstractmethod
    def fetch(self, ids: List[str], namespace: str) -> Dict[str, Any]:
        """Fetch vectors by ID."""
        pass

    @abstractmethod
    def list_namespaces(self) -> List[str]:
        """List all namespaces in the index."""
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Return the health status of the vector store connection."""
        pass
