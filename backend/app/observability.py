import json
import logging
import sys
import time
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import Request


logger = logging.getLogger("campusmarket.http")

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)

logger.setLevel(logging.INFO)
logger.propagate = False


async def log_http_request(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    start_time = time.perf_counter()

    response = await call_next(request)

    duration_ms = round(
        (time.perf_counter() - start_time) * 1000,
        2,
    )

    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": "INFO",
        "event": "http_request",
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": duration_ms,
    }

    logger.info(
        json.dumps(
            log_entry,
            ensure_ascii=False,
            separators=(",", ":"),
        )
    )

    response.headers["X-Request-ID"] = request_id

    return response