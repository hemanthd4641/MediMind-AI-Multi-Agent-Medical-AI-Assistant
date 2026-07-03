import time
import structlog
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
from backend.app.vector_store.base import VectorStore
from backend.app.vector_store import config

logger = structlog.get_logger(__name__)

class PineconeVectorStore(VectorStore):
    """Implementation of VectorStore using Pinecone Cloud."""

    def __init__(self):
        self.api_key = config.PINECONE_API_KEY
        self.index_name = config.PINECONE_INDEX
        self.environment = config.PINECONE_ENVIRONMENT
        
        if not self.api_key:
            logger.warning("PINECONE_API_KEY is not set. Vector store operations will fail.")
            self.pc = None
            self.index = None
            return
            
        try:
            self.pc = Pinecone(api_key=self.api_key)
            # Try to get the index. If it doesn't exist, we'll create it later if create_index is called
            if self.index_name in self.pc.list_indexes().names():
                self.index = self.pc.Index(self.index_name)
            else:
                self.index = None
                logger.info(f"Pinecone index '{self.index_name}' not found. It will need to be created.")
        except Exception as e:
            logger.error("Failed to initialize Pinecone client", error=str(e))
            self.pc = None
            self.index = None

    def create_index(self, dimension: int = None):
        if not self.pc:
            raise ValueError("Pinecone client not initialized.")
            
        if dimension is None:
            # Dynamically detect dimension by embedding a dummy string
            from backend.app.embeddings.service import embedding_service
            dummy_emb = embedding_service.embed_query("test")
            dimension = len(dummy_emb)
            logger.info("Dynamically detected embedding dimension", dimension=dimension)
            
        if self.index_name not in self.pc.list_indexes().names():
            logger.info("Creating Pinecone index...", index_name=self.index_name, dimension=dimension)
            self.pc.create_index(
                name=self.index_name,
                dimension=dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region=self.environment
                )
            )
            # Wait for index to be ready
            while not self.pc.describe_index(self.index_name).status['ready']:
                time.sleep(1)
            
            logger.info("Pinecone index created successfully.")
            
        if not self.index:
            self.index = self.pc.Index(self.index_name)

    def delete_index(self):
        if self.pc and self.index_name in self.pc.list_indexes().names():
            self.pc.delete_index(self.index_name)
            self.index = None
            logger.info("Pinecone index deleted.", index_name=self.index_name)

    def upsert(self, chunk_id: str, embedding: List[float], metadata: Dict[str, Any], namespace: str):
        self._check_index()
        self.index.upsert(
            vectors=[{"id": chunk_id, "values": embedding, "metadata": metadata}],
            namespace=namespace
        )

    def upsert_batch(self, vectors: List[Dict[str, Any]], namespace: str):
        self._check_index()
        # Ensure we don't exceed Pinecone's payload limit by batching in smaller chunks if needed.
        # Pinecone handles up to 1000 vectors per request usually.
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            # Retry logic can be added here if needed, but Pinecone client has built-in retries
            self.index.upsert(vectors=batch, namespace=namespace)
            logger.info("Upserted batch to Pinecone", count=len(batch), namespace=namespace)

    def query(self, query_embedding: List[float], top_k: int, namespace: str, filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        self._check_index()
        kwargs = {
            "vector": query_embedding,
            "top_k": top_k,
            "namespace": namespace,
            "include_metadata": True,
            "include_values": False
        }
        if filter:
            kwargs["filter"] = filter
            
        t0 = time.perf_counter()
        response = self.index.query(**kwargs)
        query_time_ms = int((time.perf_counter() - t0) * 1000)
        
        logger.info("Pinecone query executed", matches=len(response.matches), latency_ms=query_time_ms, namespace=namespace)
        
        results = []
        for match in response.matches:
            results.append({
                "id": match.id,
                "score": match.score,
                "metadata": match.metadata
            })
        return results

    def delete(self, ids: List[str], namespace: str):
        self._check_index()
        self.index.delete(ids=ids, namespace=namespace)

    def fetch(self, ids: List[str], namespace: str) -> Dict[str, Any]:
        self._check_index()
        return self.index.fetch(ids=ids, namespace=namespace)

    def list_namespaces(self) -> List[str]:
        self._check_index()
        stats = self.index.describe_index_stats()
        namespaces = stats.get("namespaces", {})
        return list(namespaces.keys())

    def health_check(self) -> Dict[str, Any]:
        if not self.pc:
            return {"status": "unhealthy", "reason": "Pinecone client not initialized (check API key)"}
        
        try:
            t0 = time.perf_counter()
            indexes = self.pc.list_indexes().names()
            latency = int((time.perf_counter() - t0) * 1000)
            
            if self.index_name not in indexes:
                return {"status": "warning", "reason": f"Index '{self.index_name}' not found", "latency_ms": latency}
            
            if self.index:
                stats = self.index.describe_index_stats()
                return {
                    "status": "healthy",
                    "latency_ms": latency,
                    "index_name": self.index_name,
                    "dimension": stats.get("dimension"),
                    "total_vector_count": stats.get("total_vector_count"),
                    "namespaces": stats.get("namespaces", {})
                }
            return {"status": "warning", "reason": "Index object not instantiated", "latency_ms": latency}
        except Exception as e:
            return {"status": "unhealthy", "reason": str(e)}

    def _check_index(self):
        if not self.index:
            # If we don't have the index, try to create it automatically just-in-time
            try:
                self.create_index()
            except Exception as e:
                raise RuntimeError(f"Pinecone index is not initialized and failed auto-creation: {str(e)}")
