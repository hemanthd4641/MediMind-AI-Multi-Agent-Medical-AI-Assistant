import uvicorn
from fastapi import FastAPI
from backend.config import settings
from backend.api.health import router as health_router
from backend.middleware.cors import cors_middleware
from backend.middleware.request_logging import request_logging_middleware
from backend.middleware.timing import timing_middleware


def create_app() -> FastAPI:
    app = FastAPI(title="MediMind AI API", version="1.0.0")
    # Middleware
    app.add_middleware(cors_middleware)
    app.middleware("http")(request_logging_middleware)
    app.middleware("http")(timing_middleware)
    # Routers
    app.include_router(health_router)
    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)
