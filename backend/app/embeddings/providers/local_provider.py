import threading
import time
import structlog
from typing import List
from backend.app.embeddings.providers.base import EmbeddingProvider
from backend.app.embeddings import config

logger = structlog.get_logger(__name__)

class LocalSentenceTransformerProvider(EmbeddingProvider):
    """
    Sentence Transformers implementation.
    Loads the model once in a thread-safe manner (Singleton pattern).
    """
    _instance = None
    _lock = threading.Lock()
    _model = None

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(LocalSentenceTransformerProvider, cls).__new__(cls)
            return cls._instance

    def _get_model(self):
        if self._model is None:
            with self._lock:
                if self._model is None:
                    try:
                        # Lazy import to avoid slow startup if not using this provider
                        from sentence_transformers import SentenceTransformer
                        import torch
                        
                        # Optional GPU detection if device is cpu but cuda is available
                        device_to_use = config.DEVICE
                        if device_to_use == "auto":
                            device_to_use = "cuda" if torch.cuda.is_available() else "cpu"
                        
                        logger.info("Loading Local HuggingFace model", model=config.EMBEDDING_MODEL, target_device=device_to_use)
                        
                        start_time = time.perf_counter()
                        self._model = SentenceTransformer(config.EMBEDDING_MODEL, device=device_to_use)
                        load_time_ms = int((time.perf_counter() - start_time) * 1000)
                        
                        logger.info("Local HuggingFace model loaded successfully", load_time_ms=load_time_ms)
                    except ImportError as e:
                        logger.error("Failed to load sentence_transformers. Is it installed?", error=str(e))
                        raise
                    except Exception as e:
                        logger.error("Failed to initialize LocalSentenceTransformerProvider", error=str(e))
                        raise
        return self._model

    def embed_query(self, text: str) -> List[float]:
        model = self._get_model()
        return model.encode(text, normalize_embeddings=True).tolist()

    def embed_document(self, text: str) -> List[float]:
        model = self._get_model()
        return model.encode(text, normalize_embeddings=True).tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        model = self._get_model()
        # Utilize batch embedding
        return model.encode(texts, batch_size=config.BATCH_SIZE, normalize_embeddings=True).tolist()
