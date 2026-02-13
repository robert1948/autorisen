from __future__ import annotations

import os
from typing import Iterable

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

_ALLOWED_METHODS: set[str] = {"GET", "HEAD", "OPTIONS"}
_BLOCKED_METHODS: set[str] = {"POST", "PUT", "PATCH", "DELETE"}

# Paths exempt from read-only restrictions (auth must always work)
_EXEMPT_PATH_PREFIXES: tuple[str, ...] = (
    "/api/auth/",
    "/api/health",
)


def _read_only_enabled() -> bool:
    return os.getenv("READ_ONLY_MODE", "0").strip() == "1"


class ReadOnlyModeMiddleware:
    def __init__(self, app: ASGIApp, *, allowed_methods: Iterable[str] | None = None):
        self.app = app
        self.allowed_methods = {
            method.upper() for method in (allowed_methods or _ALLOWED_METHODS)
        }

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        if not _read_only_enabled():
            await self.app(scope, receive, send)
            return

        # Always allow auth and health endpoints regardless of read-only mode
        path = scope.get("path", "")
        if any(path.startswith(prefix) for prefix in _EXEMPT_PATH_PREFIXES):
            await self.app(scope, receive, send)
            return

        method = (scope.get("method") or "").upper()
        if method in self.allowed_methods:
            await self.app(scope, receive, send)
            return

        if method in _BLOCKED_METHODS:
            response = JSONResponse(
                {"detail": "Read-only mode: write operations are disabled."},
                status_code=403,
            )
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)
