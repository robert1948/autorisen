"""Simple rate limiter helpers for authentication endpoints."""

from __future__ import annotations

import os
import time
from collections import defaultdict, deque
from typing import Deque, Dict, Tuple

try:
    import redis  # type: ignore
except ImportError:  # pragma: no cover
    redis = None

_RATE_LIMIT = int(os.getenv("AUTH_RATE_LIMIT", "5"))  # legacy default
_WINDOW_SECONDS = int(os.getenv("AUTH_RATE_LIMIT_WINDOW", "60"))

_LOGIN_IP_LIMIT = int(os.getenv("AUTH_LOGIN_IP_PER_MIN", "5"))
_LOGIN_IP_WINDOW = int(os.getenv("AUTH_LOGIN_IP_WINDOW_SECONDS", "60"))
_LOGIN_ACCOUNT_LIMIT = int(os.getenv("AUTH_LOGIN_ACCOUNT_PER_HOUR", "20"))
_LOGIN_ACCOUNT_WINDOW = int(os.getenv("AUTH_LOGIN_ACCOUNT_WINDOW_SECONDS", str(60 * 60)))

_REDIS_URL = os.getenv("REDIS_URL")
_redis_client = None
if _REDIS_URL and redis is not None:
    _redis_client = redis.Redis.from_url(_REDIS_URL)

# fallback in-memory store (per-process)
_memory_buckets: Dict[str, Deque[float]] = defaultdict(deque)


def _build_key(identifier: str) -> str:
    return f"auth:rate:{identifier}"


def _check(identifier: str, limit: int, window: int) -> bool:
    """Return True if request is allowed for the configured window."""
    if limit <= 0:
        return True
    now = time.time()

    if _redis_client:
        key = _build_key(identifier)
        pipeline = _redis_client.pipeline()
        pipeline.zremrangebyscore(key, 0, now - window)
        pipeline.zadd(key, {f"{now}:{os.getpid()}": now})
        pipeline.expire(key, window)
        pipeline.zcard(key)
        _, _, _, count = pipeline.execute()
        return int(count) <= limit

    bucket = _memory_buckets[identifier]
    while bucket and now - bucket[0] > window:
        bucket.popleft()
    if len(bucket) >= limit:
        return False
    bucket.append(now)
    return True


def check(identifier: str) -> bool:
    """Legacy single-window rate limiter (kept for backwards compatibility)."""
    return _check(identifier, _RATE_LIMIT, _WINDOW_SECONDS)


def reset(identifier: str) -> None:
    if _redis_client:
        _redis_client.delete(_build_key(identifier))
    else:
        _memory_buckets.pop(identifier, None)


def allow_login(ip_address: str | None, account_identifier: str) -> Tuple[bool, str | None]:
    """
    Enforce combined login rate limits.

    Returns (allowed, reason) where reason is ``"ip"`` or ``"account"`` when blocked.
    """

    if ip_address:
        if not _check(f"login:ip:{ip_address}", _LOGIN_IP_LIMIT, _LOGIN_IP_WINDOW):
            return False, "ip"
    normalized_account = account_identifier.strip().lower()
    if normalized_account:
        if not _check(
            f"login:acct:{normalized_account}", _LOGIN_ACCOUNT_LIMIT, _LOGIN_ACCOUNT_WINDOW
        ):
            return False, "account"
    return True, None


def reset_login(ip_address: str | None, account_identifier: str) -> None:
    """Clear login counters after a successful authentication."""

    if ip_address:
        reset(f"login:ip:{ip_address}")
    normalized_account = account_identifier.strip().lower()
    if normalized_account:
        reset(f"login:acct:{normalized_account}")
