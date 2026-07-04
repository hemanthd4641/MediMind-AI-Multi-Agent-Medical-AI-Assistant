import structlog
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.database import get_db
from backend.app.vector_store.service import vector_store_service
from backend.app.embeddings.service import embedding_service
from backend.app.embeddings import config as emb_config

router = APIRouter()
logger = structlog.get_logger(__name__)

@router.get("/health/liveness", status_code=status.HTTP_200_OK)
async def liveness_check():
    """Simple liveness probe for Docker/K8s to know if the container is running."""
    return JSONResponse(content={"status": "alive"})

@router.get("/health", status_code=status.HTTP_200_OK)
@router.get("/health/readiness", status_code=status.HTTP_200_OK)
async def readiness_check(db: Session = Depends(get_db)):
    """Deep readiness probe to ensure all backing services are reachable."""
    health_status = {
        "status": "healthy",
        "version": "1.0.0",
        "components": {}
    }
    
    # Check Database (Supabase)
    try:
        db.execute(text("SELECT 1"))
        health_status["components"]["database"] = "healthy"
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        health_status["components"]["database"] = "unhealthy"
        health_status["status"] = "degraded"
        
    # Check Pinecone
    pinecone_health = vector_store_service.health_check()
    health_status["components"]["pinecone"] = pinecone_health["status"]
    if pinecone_health["status"] == "unhealthy":
        health_status["status"] = "degraded"
        
    # Check Embeddings Model
    # Check Embeddings Model
    embedding_health = embedding_service.health_check()
    health_status["components"]["embeddings"] = embedding_health
    if embedding_health["status"] == "unhealthy":
        health_status["status"] = "degraded"
        
    return JSONResponse(
        content=health_status,
        status_code=status.HTTP_200_OK if health_status["status"] == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE
    )

@router.get("/", status_code=status.HTTP_200_OK)
async def root():
    return JSONResponse(content={"application": "MediMind AI", "status": "running"})
