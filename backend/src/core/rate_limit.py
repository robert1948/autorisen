# backend/src/core/rate_limit.py
"""
Centralized rate limiting for the API.

Features
- Works whether `slowapi` is installed or not (no-op fallback).
- Dual-use decorators: `@auth_rate_limit` or `@auth_rate_limit()`.
- Env flags to tweak/disable:
    * DISABLE_RATE_LIMIT=1           -> disables rate limiting entirely
    * RATE_LIMIT_DEFAULT="200/minute"
    * RATE_LIMIT_AUTH="5/minute"
- Idempotent `configure_rate_limit(app)` wiring.
- Consistent JSON for 429 responses.
"""

from __future__ import annotations

import os
from typing import Any, Callable, Optional

# ---------- Configuration ----------
DISABLE = os.getenv("DISABLE_RATE_LIMIT", "").strip() in {"1", "true", "yes"}
DEFAULT_LIMIT = os.getenv("RATE_LIMIT_DEFAULT", "200/minute")
AUTH_LIMIT = os.getenv("RATE_LIMIT_AUTH", "5/minute")


def _dual_use_limit_decorator(
    limiter_obj: Any, limit: str, arg: Optional[Callable] = None
):
    """
    Turn a slowapi limiter.limit(limit) into a decorator that works as:
      - @decorator
      - @decorator()
    """
    if callable(arg):  # used as @decorator
        return limiter_obj.limit(limit)(arg)

    def _decorator(func: Callable):
        return limiter_obj.limit(limit)(func)

    return _decorator


try:
    if DISABLE:
        raise ImportError("Rate limiting disabled via DISABLE_RATE_LIMIT=1")

    from fastapi.responses import JSONResponse  # type: ignore
    from slowapi import Limiter  # type: ignore
    from slowapi.errors import RateLimitExceeded  # type: ignore
    from slowapi.middleware import SlowAPIMiddleware  # type: ignore
    from slowapi.util import get_remote_address  # type: ignore

    limiter = Limiter(key_func=get_remote_address, default_limits=[DEFAULT_LIMIT])

    def rate_limit(limit: str) -> Callable[[Callable], Callable]:
        """Usage: @rate_limit("10/minute")"""

        def _decorator(func: Callable):
            return limiter.limit(limit)(func)

        return _decorator

    def auth_rate_limit(arg: Optional[Callable] = None, *, limit: Optional[str] = None):
        """Usage: @auth_rate_limit  OR  @auth_rate_limit()  OR  @auth_rate_limit(limit="10/minute")"""
        return _dual_use_limit_decorator(limiter, limit or AUTH_LIMIT, arg)

    def configure_rate_limit(app) -> None:
        """
        Wire middleware + 429 handler exactly once.
        Safe to call multiple times (idempotent).
        """
        # Already configured?
        if getattr(app.state, "rate_limit_configured", False):
            return

        # Attach limiter for access in routes if needed
        app.state.limiter = limiter

        # Middleware
        # Avoid double-adding if user code also adds it
        if not any(
            type(m).__name__ == "SlowAPIMiddleware"
            for m in getattr(app, "user_middleware", [])
        ):
            app.add_middleware(SlowAPIMiddleware)

        # JSON handler for 429
        def _429_handler(request, exc):
            return JSONResponse(
                status_code=429, content={"detail": "rate limit exceeded"}
            )

        # Avoid replacing if already present
        existing = app.exception_handlers.get(RateLimitExceeded)
        if existing is None:
            app.add_exception_handler(RateLimitExceeded, _429_handler)

        app.state.rate_limit_configured = True

except Exception:
    # -------- No-op fallback (no slowapi or disabled) --------
    class _NoopLimiter:
        def limit(self, *_a, **_k):
            def _wrap(f):
                return f

            return _wrap

    limiter = _NoopLimiter()

    def rate_limit(_limit: str):
        def _decorator(func: Callable):
            return func

        return _decorator

    def auth_rate_limit(arg: Optional[Callable] = None, *, limit: Optional[str] = None):
        if callable(arg):  # used as @auth_rate_limit
            return arg

        def _decorator(func: Callable):
            return func

        return _decorator

    def configure_rate_limit(app) -> None:  # noqa: ARG001
        # Nothing to wire in no-op mode
        setattr(getattr(app, "state", app), "rate_limit_configured", True)
