import threading
from typing import List

class EmbeddingService:
    """
    Singleton service for generating embeddings using sentence-transformers.
    Loads the model lazily to avoid heavy memory usage at startup if not needed.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EmbeddingService, cls).__new__(cls)
                cls._instance._model = None
            return cls._instance

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            # Using a lightweight, performant model suitable for semantic search
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
        return self._model

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        model = self._get_model()
        return model.encode(text).tolist()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        if not texts:
            return []
        model = self._get_model()
        return model.encode(texts).tolist()

embedding_service = EmbeddingService()
