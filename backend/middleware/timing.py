import time
from fastapi import Request
from backend.utils.logger import logger

async def timing_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    logger.debug(
        "request_timing",
        extra={"path": request.url.path, "method": request.method, "duration_ms": f"{process_time:.2f}"},
    )
    return response
