"""In-memory LLM response cache with TTL eviction.

Caches LLM responses keyed by a hash of (model, system_prompt, user_prompt).
This avoids paying for identical queries within the TTL window while keeping
memory bounded by ``max_size``.

Usage::

    from backend.src.modules.usage.llm_cache import llm_cache

    key = llm_cache.make_key(model, system_prompt, user_prompt)
    cached = llm_cache.get(key)
    if cached is not None:
        return cached  # (text, usage_meta) tuple — zero cost

    # … call LLM …

    llm_cache.put(key, (text, usage_meta))

Thread-safe via a simple lock; suitable for async FastAPI workers because
the critical section is a microsecond dict lookup — no I/O under the lock.
"""

from __future__ import annotations

import hashlib
import logging
import os
import threading
import time
from typing import Any, Optional

log = logging.getLogger(__name__)

# Default: 5 minutes.  Override via environment variable.
_DEFAULT_TTL_SECONDS = int(os.getenv("LLM_CACHE_TTL_SECONDS", "300"))
_DEFAULT_MAX_SIZE = int(os.getenv("LLM_CACHE_MAX_SIZE", "512"))


class _CacheEntry:
    __slots__ = ("value", "expires_at")

    def __init__(self, value: Any, ttl: int) -> None:
        self.value = value
        self.expires_at = time.monotonic() + ttl


class LLMCache:
    """Bounded, TTL-evicting LLM response cache."""

    def __init__(
        self,
        ttl_seconds: int = _DEFAULT_TTL_SECONDS,
        max_size: int = _DEFAULT_MAX_SIZE,
    ) -> None:
        self._ttl = ttl_seconds
        self._max_size = max_size
        self._store: dict[str, _CacheEntry] = {}
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @staticmethod
    def make_key(model: str, system_prompt: str, user_prompt: str) -> str:
        """Deterministic cache key from the LLM call parameters."""
        raw = f"{model}||{system_prompt}||{user_prompt}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """Return cached value or ``None`` on miss/expiry."""
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            if time.monotonic() > entry.expires_at:
                del self._store[key]
                return None
            return entry.value

    def put(self, key: str, value: Any) -> None:
        """Insert or overwrite an entry.  Evicts oldest on overflow."""
        with self._lock:
            # Evict expired entries first
            now = time.monotonic()
            expired = [k for k, v in self._store.items() if now > v.expires_at]
            for k in expired:
                del self._store[k]

            # Evict oldest if still over budget
            while len(self._store) >= self._max_size:
                oldest_key = min(self._store, key=lambda k: self._store[k].expires_at)
                del self._store[oldest_key]

            self._store[key] = _CacheEntry(value, self._ttl)

    def invalidate(self, key: str) -> None:
        """Remove a specific entry."""
        with self._lock:
            self._store.pop(key, None)

    def clear(self) -> None:
        """Drop all cached entries."""
        with self._lock:
            self._store.clear()

    @property
    def size(self) -> int:
        """Current number of entries (including potentially expired)."""
        return len(self._store)


# Module-level singleton
llm_cache = LLMCache()
