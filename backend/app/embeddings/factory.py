from backend.app.embeddings import config
from backend.app.embeddings.providers.base import EmbeddingProvider
from backend.app.embeddings.providers.api_provider import HuggingFaceInferenceProvider
from backend.app.embeddings.providers.local_provider import LocalSentenceTransformerProvider
import structlog

logger = structlog.get_logger(__name__)

class ProviderFactory:
    """Factory to instantiate the appropriate EmbeddingProvider."""

    @staticmethod
    def get_provider() -> EmbeddingProvider:
        provider_name = config.EMBEDDING_PROVIDER.lower()
        
        if provider_name == "local":
            try:
                # Try to initialize the local provider by testing the import
                import sentence_transformers
                return LocalSentenceTransformerProvider()
            except Exception as e:
                # Automatic fallback
                logger.warning("Failed to initialize LocalSentenceTransformerProvider (missing dependencies), falling back to Hugging Face API", error=str(e), fallback="huggingface_api")
                return HuggingFaceInferenceProvider()
                
        elif provider_name == "huggingface_api":
            return HuggingFaceInferenceProvider()
        
        # Future providers can be added here
        # elif provider_name == "openai":
        #     return OpenAIEmbeddingProvider()
        
        raise ValueError(f"Unknown embedding provider: {provider_name}")
