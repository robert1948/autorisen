"""
DDoS protection middleware using token bucket algorithm.
Pure ASGI implementation to avoid BaseHTTPMiddleware issues.
"""

import logging
import os
import time
from collections import defaultdict
from typing import Dict, Tuple

from starlette.datastructures import MutableHeaders
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

log = logging.getLogger("ddos_protection")


class DDoSProtectionMiddleware:
    """
    Middleware that implements rate limiting and burst protection.
    """

    def __init__(
        self,
        app: ASGIApp,
        limit: int = 200,
        window: int = 60,
        burst_limit: int = 50,
    ) -> None:
        self.app = app
        self.limit = limit
        self.window = window
        self.burst_limit = burst_limit
        # IP -> (count, window_start_time)
        self.requests: Dict[str, Tuple[int, float]] = defaultdict(lambda: (0, time.time()))
        # IP -> (count, last_request_time) for burst detection
        self.bursts: Dict[str, Tuple[int, float]] = defaultdict(lambda: (0, time.time()))
        # IP -> block_until timestamp for repeat offenders
        self.blocked: Dict[str, float] = {}
        
        # Check if disabled via environment variable (useful for tests)
        self.disabled = os.getenv("DISABLE_RATE_LIMIT", "").strip().lower() in {"1", "true", "yes"}

    def _get_client_ip(self, scope: Scope) -> str:
        """Extract real client IP from X-Forwarded-For header (Heroku, proxies) or fall back to socket IP."""
        headers = dict(scope.get("headers", []))
        # Heroku/proxies set X-Forwarded-For: <client>, <proxy1>, <proxy2>
        xff = headers.get(b"x-forwarded-for", b"").decode("latin-1").strip()
        if xff:
            # First entry is the real client IP
            return xff.split(",")[0].strip()
        return scope.get("client", ("0.0.0.0", 0))[0]

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        if self.disabled:
            await self.app(scope, receive, send)
            return

        # Only rate-limit API routes; let page navigation, static assets, and
        # health checks through so the browser can always load fresh code.
        path = scope.get("path", "")
        if not path.startswith("/api/"):
            await self.app(scope, receive, send)
            return

        # Exempt OAuth callback paths — these are one-shot redirects from
        # identity providers that trigger a burst of follow-up API calls
        # (CSRF, login, /me) which can trip burst detection.
        if "/oauth/" in path and "/callback" in path:
            await self.app(scope, receive, send)
            return

        client_ip = self._get_client_ip(scope)
        now = time.time()

        # 0. Check hard-block for repeat offenders
        block_until = self.blocked.get(client_ip, 0)
        if now < block_until:
            remaining = int(block_until - now)
            response = JSONResponse(
                {
                    "detail": "Too many requests — please wait before retrying",
                    "retry_after": remaining,
                },
                status_code=429,
                headers={"Retry-After": str(remaining)},
            )
            await response(scope, receive, send)
            return

        # 1. Window-based Rate Limiting
        count, start_time = self.requests[client_ip]
        
        if now - start_time > self.window:
            # Reset window
            self.requests[client_ip] = (1, now)
        else:
            if count >= self.limit:
                # Sliding block: extend the block for persistent offenders.
                # Each hit during rate-limit adds 60s (capped at 5 min).
                current_block = self.blocked.get(client_ip, now)
                new_block = max(current_block, now) + self.window
                self.blocked[client_ip] = min(new_block, now + 300)
                retry_after = int(self.blocked[client_ip] - now)
                log.warning(
                    f"Rate limit exceeded for {client_ip} — blocked for {retry_after}s"
                )
                response = JSONResponse(
                    {
                        "detail": "Too many requests",
                        "endpoint_type": "general",
                        "retry_after": retry_after,
                    },
                    status_code=429,
                    headers={"Retry-After": str(retry_after)},
                )
                await response(scope, receive, send)
                return
            self.requests[client_ip] = (count + 1, start_time)

        # 2. Burst Protection (Token Bucket-ish)
        burst_count, last_req_time = self.bursts[client_ip]
        
        # Decay burst count over time
        time_passed = now - last_req_time
        burst_count = max(0, burst_count - int(time_passed * 2))  # Decay 2 per second
        
        if burst_count >= self.burst_limit:
            # Sliding block for burst offenders: 120s hard-block
            self.blocked[client_ip] = max(
                self.blocked.get(client_ip, 0), now + 120
            )
            log.warning(f"Burst attack detected from {client_ip} — blocked for 120s")
            response = JSONResponse(
                {
                    "detail": "Burst attack detected",
                    "endpoint_type": "auth",
                    "retry_after": 120,
                },
                status_code=429,
                headers={"Retry-After": "120"},
            )
            await response(scope, receive, send)
            return
            
        self.bursts[client_ip] = (burst_count + 1, now)

        # Add headers to response
        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers["X-RateLimit-Limit"] = str(self.limit)
                headers["X-RateLimit-Remaining"] = str(max(0, self.limit - self.requests[client_ip][0]))
                headers["X-RateLimit-Reset"] = str(int(start_time + self.window))
            await send(message)

        await self.app(scope, receive, send_wrapper)
