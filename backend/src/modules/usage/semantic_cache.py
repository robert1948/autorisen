"""Semantic LLM cache — embedding-based similarity lookup for near-duplicate queries.

Complements the exact-match ``LLMCache`` by catching semantically similar
prompts ("What's my cash flow?" vs "Show me cash flow analysis") that would
miss a hash-based cache.

Uses the same OpenAI text-embedding-3-small model already deployed for RAG
(no new infrastructure).  Entries are stored in-memory with TTL eviction
and a configurable similarity threshold.

Usage::

    from backend.src.modules.usage.semantic_cache import semantic_cache

    hit = await semantic_cache.get(user_prompt)
    if hit is not None:
        return hit  # (response_text, usage_meta) — zero LLM cost

    # … call LLM …

    await semantic_cache.put(user_prompt, (text, usage_meta))
"""

from __future__ import annotations

import logging
import math
import os
import threading
import time
from typing import Any, Optional

log = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────────────────────

_DEFAULT_TTL = int(os.getenv("SEMANTIC_CACHE_TTL", "600"))  # 10 min
_DEFAULT_MAX_SIZE = int(os.getenv("SEMANTIC_CACHE_MAX_SIZE", "256"))
_DEFAULT_THRESHOLD = float(os.getenv("SEMANTIC_CACHE_THRESHOLD", "0.92"))


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Fast cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class SemanticCache:
    """In-memory embedding-based cache for LLM responses.

    Each entry stores: (embedding, value, timestamp).
    On lookup, the query embedding is compared against all stored entries;
    if cosine similarity >= threshold, the cached value is returned.
    """

    def __init__(
        self,
        *,
        ttl_seconds: int = _DEFAULT_TTL,
        max_size: int = _DEFAULT_MAX_SIZE,
        similarity_threshold: float = _DEFAULT_THRESHOLD,
    ) -> None:
        self._ttl = ttl_seconds
        self._max_size = max_size
        self._threshold = similarity_threshold
        self._lock = threading.Lock()
        # list of (embedding, value, insert_time)
        self._entries: list[tuple[list[float], Any, float]] = []
        self._hits = 0
        self._misses = 0

    # ── Embedding helper ──────────────────────────────────────────────────

    @staticmethod
    async def _embed(text: str) -> Optional[list[float]]:
        """Generate an embedding for a text using the RAG embedding pipeline.

        Falls back to None if no API key is configured (dev/test).
        """
        try:
            from backend.src.modules.rag.embeddings import generate_embeddings
            from backend.src.core.config import get_settings

            api_key = get_settings().openai_api_key
            if not api_key:
                return None

            vectors = await generate_embeddings([text], api_key=api_key)
            return vectors[0] if vectors else None
        except Exception:
            log.debug("Semantic cache embedding failed", exc_info=True)
            return None

    # ── Public API ────────────────────────────────────────────────────────

    async def get(self, query: str) -> Optional[Any]:
        """Look up a semantically similar cached entry.

        Returns the cached value if found, else None.
        """
        vec = await self._embed(query)
        if vec is None:
            self._misses += 1
            return None

        now = time.monotonic()
        best_val = None
        best_score = 0.0

        with self._lock:
            # Evict expired while scanning
            alive: list[tuple[list[float], Any, float]] = []
            for emb, val, ts in self._entries:
                if (now - ts) > self._ttl:
                    continue
                alive.append((emb, val, ts))
                score = _cosine_similarity(vec, emb)
                if score >= self._threshold and score > best_score:
                    best_score = score
                    best_val = val
            self._entries = alive

        if best_val is not None:
            self._hits += 1
            log.debug("Semantic cache HIT (score=%.3f)", best_score)
        else:
            self._misses += 1

        return best_val

    async def put(self, query: str, value: Any) -> None:
        """Store a query/response pair in the cache."""
        vec = await self._embed(query)
        if vec is None:
            return

        now = time.monotonic()
        with self._lock:
            self._entries.append((vec, value, now))
            # Evict oldest if over size
            if len(self._entries) > self._max_size:
                self._entries = self._entries[-self._max_size:]

    def clear(self) -> None:
        """Flush all entries."""
        with self._lock:
            self._entries.clear()
            self._hits = 0
            self._misses = 0

    @property
    def stats(self) -> dict[str, Any]:
        """Return cache statistics for monitoring."""
        with self._lock:
            return {
                "entries": len(self._entries),
                "max_size": self._max_size,
                "ttl_seconds": self._ttl,
                "similarity_threshold": self._threshold,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": (
                    round(self._hits / (self._hits + self._misses), 3)
                    if (self._hits + self._misses) > 0
                    else 0.0
                ),
            }


# Module-level singleton
semantic_cache = SemanticCache()
