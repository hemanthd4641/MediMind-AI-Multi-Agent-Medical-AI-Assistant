import time
import structlog
import numpy as np
from typing import List
from backend.app.embeddings.factory import ProviderFactory
from backend.app.embeddings import config
from backend.app.embeddings.providers.local_provider import LocalSentenceTransformerProvider
from backend.app.embeddings.providers.api_provider import HuggingFaceInferenceProvider

logger = structlog.get_logger(__name__)

class EmbeddingService:
    """
    Facade service for embedding operations.
    Hides the provider implementation from the rest of the application.
    """

    def __init__(self):
        self.provider = ProviderFactory.get_provider()
        self._provider_name = "local" if isinstance(self.provider, LocalSentenceTransformerProvider) else "huggingface_api"

    def embed_query(self, text: str) -> List[float]:
        t0 = time.perf_counter()
        embedding = self.provider.embed_query(text)
        latency = int((time.perf_counter() - t0) * 1000)
        logger.info("Embedding generated", type="query", latency_ms=latency, provider=self._provider_name, model=config.EMBEDDING_MODEL)
        return embedding

    def embed_document(self, text: str) -> List[float]:
        t0 = time.perf_counter()
        embedding = self.provider.embed_document(text)
        latency = int((time.perf_counter() - t0) * 1000)
        logger.info("Embedding generated", type="document", latency_ms=latency, provider=self._provider_name, model=config.EMBEDDING_MODEL)
        return embedding

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        t0 = time.perf_counter()
        embeddings = self.provider.embed_documents(texts)
        latency = int((time.perf_counter() - t0) * 1000)
        logger.info("Batch embedding generated", count=len(texts), latency_ms=latency, batch_size=config.BATCH_SIZE, provider=self._provider_name, model=config.EMBEDDING_MODEL)
        return embeddings
        
    def batch_embed(self, texts: List[str]) -> List[List[float]]:
        """Alias for embed_documents"""
        return self.embed_documents(texts)

    def normalize_embeddings(self, embeddings: List[List[float]]) -> List[List[float]]:
        """Utility to normalize embeddings if a provider doesn't do it natively."""
        emb_arr = np.array(embeddings)
        norms = np.linalg.norm(emb_arr, axis=1, keepdims=True)
        # Avoid division by zero
        norms[norms == 0] = 1e-10
        normalized = emb_arr / norms
        return normalized.tolist()
        
    def health_check(self) -> dict:
        status = "healthy"
        api_reachability = "N/A"
        try:
            # perform a basic operation to verify the provider is alive
            self.provider.embed_query("health")
            if self._provider_name == "huggingface_api":
                api_reachability = "reachable"
        except Exception as e:
            status = "unhealthy"
            logger.error("Embedding provider health check failed", error=str(e), provider=self._provider_name)
            if self._provider_name == "huggingface_api":
                api_reachability = "unreachable"
            
        return {
            "status": status,
            "provider": self._provider_name,
            "model_name": config.EMBEDDING_MODEL,
            "device": config.DEVICE,
            "api_reachability": api_reachability
        }

# Singleton instance for easy importing (backward compatibility)
embedding_service = EmbeddingService()
