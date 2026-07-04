import uvicorn
import structlog
from fastapi import FastAPI
from backend.config import settings
from backend.api.health import router as health_router
from backend.middleware.cors import cors_middleware
from backend.middleware.request_logging import request_logging_middleware
from backend.middleware.timing import timing_middleware
from backend.app.api.ai_chat import router as ai_chat_router
from backend.app.api.rag import router as rag_router
from backend.app.api.consultation import router as consultation_router
from backend.app.api.reports import router as reports_router
from backend.app.api.prescriptions import router as prescriptions_router
from backend.app.api.timeline import router as timeline_router
from backend.app.api.ai_ops import router as ai_ops_router
from backend.app.api.vector_admin import router as vector_admin_router
from backend.app.api.auth import router as auth_router
from backend.app.embeddings.service import embedding_service
from backend.app.vector_store.service import vector_store_service
from backend.app.database import engine
from sqlalchemy import text
import groq

logger = structlog.get_logger(__name__)


from contextlib import asynccontextmanager
from fastapi import Request
from fastapi.responses import JSONResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up MediMind AI...")
    try:
        logger.info("Verifying Database connection...")
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection verified successfully.")
        
        logger.info("Verifying Pinecone connection...")
        pinecone_health = vector_store_service.health_check()
        if pinecone_health["status"] != "healthy":
            logger.warning("Pinecone vector store is not healthy on startup.", details=pinecone_health)
        else:
            logger.info("Pinecone connection verified successfully.")
            
        logger.info("Verifying Groq connection...")
        client = groq.Groq(api_key=settings.GROQ_API_KEY)
        client.models.list()
        logger.info("Groq API connection verified successfully.")

        # Preload the embedding model into memory on startup
        logger.info("Preloading embedding model...")
        embedding_health = embedding_service.health_check()
        if embedding_health["status"] == "healthy":
            logger.info("Embedding model preloaded successfully.", 
                        provider=embedding_health["provider"], 
                        model=embedding_health["model_name"], 
                        device=embedding_health["device"])
        else:
            logger.error("Embedding model failed to initialize.", details=embedding_health)
    except Exception as e:
        logger.error("Startup verification failed", error=str(e))
        # Failing gracefully as requested
        pass
        
    yield
    
    logger.info("Shutting down MediMind AI gracefully...")
    # Add any cleanup tasks here if needed

def create_app() -> FastAPI:
    app = FastAPI(title="MediMind AI API", version="1.0.0", lifespan=lifespan)
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error("Unhandled global exception", url=str(request.url), error=str(exc))
        return JSONResponse(
            status_code=500,
            content={"message": "An unexpected internal server error occurred. Please try again later."},
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        logger.warning("ValueError encountered", url=str(request.url), error=str(exc))
        return JSONResponse(
            status_code=400,
            content={"message": str(exc)},
        )

    # Middleware
    app.add_middleware(cors_middleware)
    app.middleware("http")(request_logging_middleware)
    app.middleware("http")(timing_middleware)
    # Routers
    app.include_router(health_router)
    app.include_router(auth_router)     # Authentication
    app.include_router(ai_chat_router)  # Phase 3 – AI Chat
    app.include_router(rag_router)      # Phase 4 – RAG Knowledge Base
    app.include_router(consultation_router) # Phase 5 – Consultation
    app.include_router(reports_router)  # Phase 6 - Medical Reports
    app.include_router(prescriptions_router) # Phase 7 - Prescriptions
    app.include_router(timeline_router) # Phase 8 - Health Timeline
    app.include_router(ai_ops_router) # Phase 9 - AI Ops
    app.include_router(vector_admin_router) # Phase 11 - Vector Admin
    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
