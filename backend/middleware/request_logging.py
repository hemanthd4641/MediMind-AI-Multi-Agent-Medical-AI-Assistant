import time
import json
from fastapi import Request
from backend.utils.logger import logger

async def request_logging_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    logger.info(
        "request",
        extra={
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "duration_ms": f"{process_time:.2f}",
        },
    )
    return response
