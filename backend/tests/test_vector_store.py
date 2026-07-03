import pytest
from unittest.mock import patch, MagicMock

import backend.app.vector_store.config as vs_config
vs_config.PINECONE_API_KEY = "fake-key"
vs_config.PINECONE_INDEX = "medimind-ai"
vs_config.PINECONE_ENVIRONMENT = "us-east-1"

from backend.app.vector_store.pinecone_store import PineconeVectorStore
from backend.app.vector_store.service import VectorStoreService

@pytest.fixture
def mock_pinecone():
    with patch("backend.app.vector_store.pinecone_store.Pinecone") as mock_pc:
        mock_instance = MagicMock()
        mock_pc.return_value = mock_instance
        
        # Mock list indexes
        mock_instance.list_indexes.return_value.names.return_value = ["medimind-ai"]
        
        # Mock Index operations
        mock_index = MagicMock()
        mock_instance.Index.return_value = mock_index
        
        yield mock_instance, mock_index

def test_health_check(mock_pinecone):
    """Test health check returns expected format when healthy."""
    mock_pc, mock_index = mock_pinecone
    
    # Mock index stats
    mock_index.describe_index_stats.return_value = {
        "dimension": 768,
        "total_vector_count": 100,
        "namespaces": {"medical-knowledge": {"vector_count": 100}}
    }
    
    store = PineconeVectorStore()
    store.api_key = "test-key"  # Bypass init check
    
    health = store.health_check()
    assert health["status"] == "healthy"
    assert health["total_vector_count"] == 100
    assert "medical-knowledge" in health["namespaces"]

def test_upsert_batch(mock_pinecone):
    """Test batch upsert passes correct arguments to pinecone SDK."""
    mock_pc, mock_index = mock_pinecone
    
    store = PineconeVectorStore()
    vectors = [
        {"id": "1", "values": [0.1]*768, "metadata": {"chunk": 1}},
        {"id": "2", "values": [0.2]*768, "metadata": {"chunk": 2}}
    ]
    
    store.upsert_batch(vectors, "test-namespace")
    
    # Verify index upsert was called with the batch and namespace
    mock_index.upsert.assert_called_once_with(
        vectors=vectors,
        namespace="test-namespace"
    )

def test_query_filtering(mock_pinecone):
    """Test query correctly handles metadata filters."""
    mock_pc, mock_index = mock_pinecone
    
    # Mock query response
    mock_response = MagicMock()
    mock_match = MagicMock()
    mock_match.id = "doc1"
    mock_match.score = 0.95
    mock_match.metadata = {"document_title": "Test Doc"}
    mock_response.matches = [mock_match]
    
    mock_index.query.return_value = mock_response
    
    store = PineconeVectorStore()
    
    # Perform query with filter
    filter_dict = {"document_title": {"$eq": "Test Doc"}}
    results = store.query([0.1]*768, top_k=1, namespace="test-namespace", filter=filter_dict)
    
    assert len(results) == 1
    assert results[0]["id"] == "doc1"
    
    # Verify filter was passed to Pinecone
    mock_index.query.assert_called_once_with(
        vector=[0.1]*768,
        top_k=1,
        namespace="test-namespace",
        include_metadata=True,
        include_values=False,
        filter=filter_dict
    )
