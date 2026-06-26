from fastapi import APIRouter
from fastapi import status
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return JSONResponse(content={"status": "healthy", "version": "1.0.0"})

@router.get("/", status_code=status.HTTP_200_OK)
async def root():
    return JSONResponse(content={"application": "MediMind AI", "status": "running"})
