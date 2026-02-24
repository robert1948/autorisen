"""Monitoring middleware — lightweight request metrics collection.

Collects per-path request counts, latency percentiles, status code
distribution, and error rates. Exposes metrics via an in-memory store
that the ``/api/metrics`` endpoint (or external scrapers) can read.

Design: pure ASGI middleware (no BaseHTTPMiddleware) matching the
project pattern set by ``cache_headers.py`` and ``read_only.py``.
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from threading import Lock
from typing import Any, Dict, List, Optional

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# In-memory metrics store (thread-safe)
# ---------------------------------------------------------------------------

@dataclass
class PathMetrics:
    """Accumulated metrics for a single path prefix."""

    request_count: int = 0
    error_count: int = 0  # 5xx responses
    client_error_count: int = 0  # 4xx responses
    total_latency_ms: float = 0.0
    min_latency_ms: float = float("inf")
    max_latency_ms: float = 0.0
    status_codes: Dict[int, int] = field(default_factory=lambda: defaultdict(int))
    latencies: List[float] = field(default_factory=list)

    # Keep last N latencies for percentile calculation
    MAX_LATENCY_SAMPLES = 1000

    def record(self, status_code: int, latency_ms: float) -> None:
        self.request_count += 1
        self.total_latency_ms += latency_ms
        self.min_latency_ms = min(self.min_latency_ms, latency_ms)
        self.max_latency_ms = max(self.max_latency_ms, latency_ms)
        self.status_codes[status_code] += 1

        if status_code >= 500:
            self.error_count += 1
        elif status_code >= 400:
            self.client_error_count += 1

        self.latencies.append(latency_ms)
        if len(self.latencies) > self.MAX_LATENCY_SAMPLES:
            self.latencies = self.latencies[-self.MAX_LATENCY_SAMPLES:]

    def percentile(self, p: float) -> float:
        """Return the p-th percentile latency (0-100)."""
        if not self.latencies:
            return 0.0
        sorted_lat = sorted(self.latencies)
        idx = int(len(sorted_lat) * p / 100.0)
        idx = min(idx, len(sorted_lat) - 1)
        return round(sorted_lat[idx], 2)

    def to_dict(self) -> Dict[str, Any]:
        avg = (
            round(self.total_latency_ms / self.request_count, 2)
            if self.request_count
            else 0.0
        )
        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "client_error_count": self.client_error_count,
            "avg_latency_ms": avg,
            "min_latency_ms": round(self.min_latency_ms, 2) if self.request_count else 0.0,
            "max_latency_ms": round(self.max_latency_ms, 2),
            "p50_latency_ms": self.percentile(50),
            "p95_latency_ms": self.percentile(95),
            "p99_latency_ms": self.percentile(99),
            "status_codes": dict(self.status_codes),
        }


class MetricsStore:
    """Thread-safe in-memory metrics registry."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._paths: Dict[str, PathMetrics] = defaultdict(PathMetrics)
        self._global = PathMetrics()
        self._start_time = time.time()

    def record(self, path: str, status_code: int, latency_ms: float) -> None:
        bucket = self._bucket(path)
        with self._lock:
            self._paths[bucket].record(status_code, latency_ms)
            self._global.record(status_code, latency_ms)

    def snapshot(self) -> Dict[str, Any]:
        """Return a JSON-serialisable metrics snapshot."""
        with self._lock:
            uptime_s = round(time.time() - self._start_time, 1)
            return {
                "uptime_seconds": uptime_s,
                "global": self._global.to_dict(),
                "paths": {
                    k: v.to_dict()
                    for k, v in sorted(self._paths.items())
                },
            }

    def reset(self) -> None:
        """Clear all collected metrics."""
        with self._lock:
            self._paths.clear()
            self._global = PathMetrics()
            self._start_time = time.time()

    @staticmethod
    def _bucket(path: str) -> str:
        """Normalise path into a metrics bucket.

        Groups dynamic segments: ``/api/rag/documents/abc`` → ``/api/rag/documents/:id``
        """
        parts = path.rstrip("/").split("/")
        normalised = []
        for i, part in enumerate(parts):
            # Heuristic: UUID-like or purely numeric segments → :id
            if len(part) >= 20 or (part and part.replace("-", "").isalnum() and not part.isalpha()):
                normalised.append(":id")
            else:
                normalised.append(part)
        return "/".join(normalised) or "/"


# Singleton shared across the app
metrics_store = MetricsStore()


# ---------------------------------------------------------------------------
# ASGI Middleware
# ---------------------------------------------------------------------------

class MonitoringMiddleware:
    """Pure ASGI middleware that records request metrics.

    Follows the same ``__init__(app) + __call__(scope, receive, send)``
    pattern as the project's other middleware.
    """

    # Paths to skip (health checks, static assets)
    SKIP_PREFIXES = (
        "/health",
        "/api/health",
        "/assets/",
        "/favicon",
        "/manifest",
        "/robots.txt",
        "/sitemap",
    )

    def __init__(self, app: Any) -> None:
        self.app = app

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path: str = scope.get("path", "/")

        # Skip noisy endpoints
        if any(path.startswith(p) for p in self.SKIP_PREFIXES):
            await self.app(scope, receive, send)
            return

        t0 = time.time()
        status_code = 500  # default if something goes wrong before response

        async def _send_wrapper(message: Any) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status", 500)
            await send(message)

        try:
            await self.app(scope, receive, _send_wrapper)
        finally:
            latency_ms = (time.time() - t0) * 1000.0
            metrics_store.record(path, status_code, latency_ms)
