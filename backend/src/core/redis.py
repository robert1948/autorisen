"""Redis helper utilities with in-memory fallback."""

from __future__ import annotations

import time
from functools import lru_cache
from typing import Any, Dict, Optional

try:  # pragma: no cover - optional dependency may be absent in tests
    import redis
except Exception:  # pragma: no cover
    redis = None  # type: ignore

from backend.src.core.config import settings


class _MemoryStore:
    """Very small in-memory store that mimics ``setex``/``get``/``delete``."""

    def __init__(self) -> None:
        self._store: Dict[str, tuple[Any, float]] = {}

    def setex(self, key: str, ttl: int, value: Any) -> None:
        expires = time.time() + max(ttl, 0)
        self._store[key] = (value, expires)

    def get(self, key: str) -> Optional[Any]:
        item = self._store.get(key)
        if not item:
            return None
        value, expires = item
        if expires and expires < time.time():
            self._store.pop(key, None)
            return None
        return value

    def delete(self, key: str) -> None:
        self._store.pop(key, None)


@lru_cache
def _get_store():
    url = settings.redis_url
    if redis is None or not url:
        return _MemoryStore()
    try:
        client = redis.Redis.from_url(url, decode_responses=True)  # type: ignore[attr-defined]
        client.ping()
        return client
    except Exception:
        return _MemoryStore()


def _key_for_jti(jti: str) -> str:
    return f"auth:deny:jti:{jti}"


def _key_for_user_version(user_id: str | int) -> str:
    return f"auth:revoke:user:{user_id}:version"


def denylist_jti(jti: str, exp_ts: int) -> None:
    ttl = max(int(exp_ts - time.time()), 0)
    ttl = max(ttl, 1)
    store = _get_store()
    store.setex(_key_for_jti(jti), ttl, "1")


def is_jti_denied(jti: str) -> bool:
    store = _get_store()
    return bool(store.get(_key_for_jti(jti)))


def cache_user_token_version(
    user_id: str | int, version: int, ttl_seconds: int = 3600
) -> None:
    store = _get_store()
    store.setex(_key_for_user_version(user_id), ttl_seconds, str(int(version)))


def get_cached_user_token_version(user_id: str | int) -> Optional[int]:
    store = _get_store()
    value = store.get(_key_for_user_version(user_id))
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def clear_user_token_version_cache(user_id: str | int) -> None:
    store = _get_store()
    store.delete(_key_for_user_version(user_id))
