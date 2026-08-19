"""Minimal in-memory per-IP rate limiter.

No external dependency and no persistent storage — state resets on
restart/redeploy, which is acceptable for a single free-tier instance.
Purpose isn't strict fairness, it's protecting the free Groq/Neo4j/Qdrant
quotas from being exhausted by a burst of requests from one source.
"""

import threading
import time
from collections import defaultdict

from fastapi import HTTPException, Request

WINDOW_SECONDS = 60
MAX_REQUESTS_PER_WINDOW = 20

_lock = threading.Lock()
_requests: dict[str, list[float]] = defaultdict(list)


def rate_limit(request: Request) -> None:
    client_ip = request.client.host if request.client else "unknown"
    now = time.monotonic()
    cutoff = now - WINDOW_SECONDS

    with _lock:
        timestamps = _requests[client_ip]
        while timestamps and timestamps[0] < cutoff:
            timestamps.pop(0)
        if len(timestamps) >= MAX_REQUESTS_PER_WINDOW:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded: max {MAX_REQUESTS_PER_WINDOW} requests per {WINDOW_SECONDS}s.",
            )
        timestamps.append(now)
