import json
import logging
import sys
import time
from collections import deque
from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

from fastapi import Request

logger = logging.getLogger("campusmarket.http")

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)

logger.setLevel(logging.INFO)
logger.propagate = False


EC01_PATH = "/publicaciones"
EC01_WINDOW_SIZE = 10
EC01_THRESHOLD_MS = 2000.0
EC01_REQUIRED_WITHIN_THRESHOLD = 9

_ec01_samples = deque(maxlen=EC01_WINDOW_SIZE)
_ec01_lock = Lock()


def _record_ec01_measurement(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
) -> None:
    if method == "GET" and path == EC01_PATH:
        with _ec01_lock:
            _ec01_samples.append(
                {
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                }
            )


def get_ec01_metric() -> dict:
    with _ec01_lock:
        samples = list(_ec01_samples)

    observed_requests = len(samples)

    within_threshold = sum(
        sample["status_code"] == 200
        and sample["duration_ms"] <= EC01_THRESHOLD_MS
        for sample in samples
    )

    evaluation_available = (
        observed_requests == EC01_WINDOW_SIZE
    )

    meets_backend_target = None

    if evaluation_available:
        meets_backend_target = (
            within_threshold
            >= EC01_REQUIRED_WITHIN_THRESHOLD
        )

    return {
        "scenario_id": "EC-01",
        "quality_attribute": "rendimiento",
        "measurement_scope": "backend GET /publicaciones",
        "window_size": EC01_WINDOW_SIZE,
        "threshold_ms": EC01_THRESHOLD_MS,
        "required_within_threshold": (
            EC01_REQUIRED_WITHIN_THRESHOLD
        ),
        "observed_requests": observed_requests,
        "within_threshold": within_threshold,
        "evaluation_available": evaluation_available,
        "meets_backend_target": meets_backend_target,
        "ec01_fully_verified": False,
        "samples": samples,
    }


def reset_ec01_metric() -> None:
    with _ec01_lock:
        _ec01_samples.clear()


async def log_http_request(request: Request, call_next):
    request_id = request.headers.get(
        "X-Request-ID",
        str(uuid4()),
    )

    start_time = time.perf_counter()

    response = await call_next(request)

    duration_ms = round(
        (time.perf_counter() - start_time) * 1000,
        2,
    )

    _record_ec01_measurement(
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms,
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
