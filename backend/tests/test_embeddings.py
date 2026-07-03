import pytest
import os
from unittest.mock import patch, MagicMock

# Set environment variables for testing before importing modules
os.environ["EMBEDDING_PROVIDER"] = "huggingface_api"
os.environ["EMBEDDING_MODEL"] = "BAAI/bge-small-en-v1.5" # Use small model for faster tests
os.environ["DEVICE"] = "cpu"
os.environ["HF_TOKEN"] = "test_token"

from backend.app.embeddings.providers.api_provider import HuggingFaceInferenceProvider
from backend.app.embeddings.providers.local_provider import LocalSentenceTransformerProvider
from backend.app.embeddings.service import EmbeddingService
from backend.app.embeddings.factory import ProviderFactory

class MockArray(list):
    def tolist(self):
        return self

@pytest.fixture
def mock_requests_post():
    with patch("requests.Session.post") as mock_post:
        # Create a mock response
        mock_response = MagicMock()
        # Mock the json method to return a dummy embedding of size 768
        mock_response.status_code = 200
        mock_response.json.return_value = [[0.1] * 768]
        mock_post.return_value = mock_response
        yield mock_post

@pytest.fixture
def mock_local_provider():
    with patch("backend.app.embeddings.factory.LocalSentenceTransformerProvider") as mock_lp:
        mock_instance = MagicMock()
        mock_instance.embed_query.return_value = [0.1] * 768
        mock_lp.return_value = mock_instance
        yield mock_lp

@patch("backend.app.embeddings.config.EMBEDDING_PROVIDER", "huggingface_api")
def test_provider_factory_api():
    """Test that the factory returns the correct provider (API)."""
    provider = ProviderFactory.get_provider()
    assert isinstance(provider, HuggingFaceInferenceProvider)

@patch("backend.app.embeddings.config.EMBEDDING_PROVIDER", "local")
def test_provider_factory_local(mock_local_provider):
    """Test that the factory returns the correct provider (Local)."""
    provider = ProviderFactory.get_provider()
    # Since we mocked it in the factory, the returned object is a MagicMock
    assert isinstance(provider, MagicMock)

@patch("backend.app.embeddings.config.EMBEDDING_PROVIDER", "local")
def test_provider_factory_fallback(mock_local_provider):
    """Test that the factory falls back to API if Local fails to initialize."""
    mock_local_provider.side_effect = Exception("Failed to load local model")
    provider = ProviderFactory.get_provider()
    assert isinstance(provider, HuggingFaceInferenceProvider)

def test_api_provider_singleton(mock_requests_post):
    """Test that the API provider is a singleton."""
    provider1 = HuggingFaceInferenceProvider()
    provider2 = HuggingFaceInferenceProvider()
    assert provider1 is provider2

def test_embed_query_api(mock_requests_post):
    """Test embedding a single query using API."""
    provider = HuggingFaceInferenceProvider()
    provider._session = None 
    
    embedding = provider.embed_query("test query")
    assert isinstance(embedding, list)
    assert len(embedding) == 768
    
    mock_requests_post.assert_called_once()
    args, kwargs = mock_requests_post.call_args
    assert kwargs["json"] == {"inputs": "test query"}

def test_batch_embedding_api(mock_requests_post):
    """Test embedding multiple documents using API."""
    provider = HuggingFaceInferenceProvider()
    provider._session = None
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [[0.1] * 768, [0.2] * 768, [0.3] * 768]
    mock_requests_post.return_value = mock_response
    
    texts = ["doc1", "doc2", "doc3"]
    embeddings = provider.embed_documents(texts)
    
    assert isinstance(embeddings, list)
    assert len(embeddings) == 3
    assert len(embeddings[0]) == 768
    
    args, kwargs = mock_requests_post.call_args
    assert kwargs["json"] == {"inputs": texts}

@patch("backend.app.embeddings.config.EMBEDDING_PROVIDER", "huggingface_api")
def test_embedding_service_api(mock_requests_post):
    """Test the embedding service facade with API provider."""
    # Temporarily set the provider directly to avoid dealing with factory side-effects
    service = EmbeddingService()
    service.provider = HuggingFaceInferenceProvider()
    service._provider_name = "huggingface_api"
    service.provider._session = None
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [[0.5] * 768]
    mock_requests_post.return_value = mock_response
    
    query_emb = service.embed_query("test query")
    assert len(query_emb) == 768
    
    mock_response.json.return_value = [[0.5] * 768, [0.6] * 768]
    batch_emb = service.batch_embed(["doc1", "doc2"])
    assert len(batch_emb) == 2

def test_normalize_embeddings():
    """Test the normalization utility."""
    service = EmbeddingService()
    embeddings = [[1.0, 1.0, 1.0], [2.0, 0.0, 0.0]]
    
    normalized = service.normalize_embeddings(embeddings)
    
    import math
    mag1 = math.sqrt(sum(x*x for x in normalized[0]))
    mag2 = math.sqrt(sum(x*x for x in normalized[1]))
    
    assert math.isclose(mag1, 1.0, rel_tol=1e-5)
    assert math.isclose(mag2, 1.0, rel_tol=1e-5)
