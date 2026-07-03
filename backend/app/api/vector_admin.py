from fastapi import APIRouter, Depends
from backend.app.deps import get_current_user
from backend.app.vector_store.service import vector_store_service
from backend.app.embeddings import config as embed_config
from backend.app.vector_store import config as vs_config
import structlog

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api/vector", tags=["Vector Store"])

@router.get("/health")
def get_health(current_user: dict = Depends(get_current_user)):
    """Check health and status of the Vector Store."""
    health_data = vector_store_service.health_check()
    return health_data

@router.get("/stats")
def get_stats(current_user: dict = Depends(get_current_user)):
    """Get metadata about the current vector store configuration."""
    return {
        "embedding_model": embed_config.EMBEDDING_MODEL,
        "embedding_dimension": vs_config.EMBEDDING_DIMENSION,
        "environment": vs_config.PINECONE_ENVIRONMENT,
        "index_name": vs_config.PINECONE_INDEX,
        "active_namespaces": [
            vs_config.PINECONE_NAMESPACE_MEDICAL_KNOWLEDGE,
            vs_config.PINECONE_NAMESPACE_PATIENT_REPORTS
        ]
    }
