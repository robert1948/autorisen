"""Simple rate limiter helpers for authentication endpoints."""

from __future__ import annotations

import os
import time
from collections import defaultdict, deque
from typing import Deque, Dict

try:
    import redis  # type: ignore
except ImportError:  # pragma: no cover
    redis = None

_RATE_LIMIT = int(os.getenv("AUTH_RATE_LIMIT", "5"))  # requests
_WINDOW_SECONDS = int(os.getenv("AUTH_RATE_LIMIT_WINDOW", "60"))

_REDIS_URL = os.getenv("REDIS_URL")
_redis_client = None
if _REDIS_URL and redis is not None:
    _redis_client = redis.Redis.from_url(_REDIS_URL)

# fallback in-memory store (per-process)
_memory_buckets: Dict[str, Deque[float]] = defaultdict(deque)


def _build_key(identifier: str) -> str:
    return f"auth:rate:{identifier}"


def check(identifier: str) -> bool:
    """Return True if request is allowed, False if rate limited."""

    now = time.time()

    if _redis_client:
        key = _build_key(identifier)
        pipeline = _redis_client.pipeline()
        pipeline.zremrangebyscore(key, 0, now - _WINDOW_SECONDS)
        pipeline.zcard(key)
        pipeline.execute()
        current = _redis_client.zcard(key)
        if current >= _RATE_LIMIT:
            return False
        _redis_client.zadd(key, {str(now): now})
        _redis_client.expire(key, _WINDOW_SECONDS)
        return True

    bucket = _memory_buckets[identifier]
    while bucket and now - bucket[0] > _WINDOW_SECONDS:
        bucket.popleft()
    if len(bucket) >= _RATE_LIMIT:
        return False
    bucket.append(now)
    return True


def reset(identifier: str) -> None:
    if _redis_client:
        _redis_client.delete(_build_key(identifier))
    else:
        _memory_buckets.pop(identifier, None)
