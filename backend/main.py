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

logger = structlog.get_logger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(title="MediMind AI API", version="1.0.0")
    # Middleware
    app.add_middleware(cors_middleware)
    app.middleware("http")(request_logging_middleware)
    app.middleware("http")(timing_middleware)
    # Routers
    app.include_router(health_router)
    app.include_router(ai_chat_router)  # Phase 3 – AI Chat
    app.include_router(rag_router)      # Phase 4 – RAG Knowledge Base
    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
