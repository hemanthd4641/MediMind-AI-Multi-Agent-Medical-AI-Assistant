import threading
import structlog
from typing import List
import requests
import time
from backend.app.embeddings.providers.base import EmbeddingProvider
from backend.app.embeddings import config
from backend.app.config import settings

logger = structlog.get_logger(__name__)

class HuggingFaceInferenceProvider(EmbeddingProvider):
    """
    Hugging Face Inference API implementation.
    Uses remote API calls to avoid loading large ML models locally.
    """
    _instance = None
    _lock = threading.Lock()
    _session = None

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(HuggingFaceInferenceProvider, cls).__new__(cls)
            return cls._instance

    def _get_session(self):
        if self._session is None:
            with self._lock:
                if self._session is None:
                    self._session = requests.Session()
                    self._session.headers.update({"Authorization": f"Bearer {settings.HF_TOKEN}"})
                    logger.info("Initialized Hugging Face API session", model=config.EMBEDDING_MODEL)
        return self._session

    def _call_api(self, payload):
        session = self._get_session()
        api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{config.EMBEDDING_MODEL}"
        
        # Exponential backoff retry logic for 503 (Model loading)
        max_retries = config.HF_MAX_RETRIES
        timeout = config.HF_API_TIMEOUT
        
        for attempt in range(max_retries):
            try:
                response = session.post(api_url, json=payload, timeout=timeout)
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 503:
                    # Model is loading
                    wait_time = 2 ** attempt
                    logger.warning("Hugging Face model is loading, retrying...", attempt=attempt+1, wait_time=wait_time)
                    time.sleep(wait_time)
                else:
                    logger.error("Hugging Face API error", status_code=response.status_code, text=response.text)
                    response.raise_for_status()
            except requests.exceptions.RequestException as e:
                logger.error("Hugging Face API request failed", error=str(e))
                if attempt == max_retries - 1:
                    raise Exception(f"Failed to reach Hugging Face API after {max_retries} retries: {str(e)}")
                wait_time = 2 ** attempt
                time.sleep(wait_time)
                
        raise Exception(f"Failed to get embeddings from Hugging Face API after {max_retries} retries.")

    def embed_query(self, text: str) -> List[float]:
        # The API returns a list of lists of floats when sending a list of strings
        # or list of floats when sending a single string for some models. 
        # Feature extraction usually returns nested lists.
        result = self._call_api({"inputs": text})
        # If it's nested (e.g. [[...]]), extract the first item
        if isinstance(result, list) and len(result) > 0 and isinstance(result[0], list):
            return result[0]
        return result

    def embed_document(self, text: str) -> List[float]:
        return self.embed_query(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # Process in batches
        all_embeddings = []
        for i in range(0, len(texts), config.BATCH_SIZE):
            batch = texts[i:i + config.BATCH_SIZE]
            result = self._call_api({"inputs": batch})
            # Ensure it's a list of lists
            if result and isinstance(result[0], float):
                # If the API incorrectly returned a flat list for a batch, wrap it
                all_embeddings.append(result)
            else:
                all_embeddings.extend(result)
        return all_embeddings
