"""
DDoS protection middleware using token bucket algorithm.
Pure ASGI implementation to avoid BaseHTTPMiddleware issues.
"""

import time
import logging
import os
from collections import defaultdict
from typing import Dict, Tuple

from starlette.datastructures import MutableHeaders
from starlette.requests import Request
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
        limit: int = 100,
        window: int = 60,
        burst_limit: int = 20,
    ) -> None:
        self.app = app
        self.limit = limit
        self.window = window
        self.burst_limit = burst_limit
        # IP -> (count, window_start_time)
        self.requests: Dict[str, Tuple[int, float]] = defaultdict(lambda: (0, time.time()))
        # IP -> (count, last_request_time) for burst detection
        self.bursts: Dict[str, Tuple[int, float]] = defaultdict(lambda: (0, time.time()))
        
        # Check if disabled via environment variable (useful for tests)
        self.disabled = os.getenv("DISABLE_RATE_LIMIT", "").strip().lower() in {"1", "true", "yes"}

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        if self.disabled:
            await self.app(scope, receive, send)
            return

        client_ip = scope.get("client", ("0.0.0.0", 0))[0]
        now = time.time()

        # 1. Window-based Rate Limiting
        count, start_time = self.requests[client_ip]
        
        if now - start_time > self.window:
            # Reset window
            self.requests[client_ip] = (1, now)
        else:
            if count >= self.limit:
                log.warning(f"Rate limit exceeded for {client_ip}")
                response = JSONResponse(
                    {
                        "detail": "Too many requests",
                        "endpoint_type": "general",
                        "retry_after": int(self.window - (now - start_time)),
                    },
                    status_code=429,
                )
                await response(scope, receive, send)
                return
            self.requests[client_ip] = (count + 1, start_time)

        # 2. Burst Protection (Token Bucket-ish)
        burst_count, last_req_time = self.bursts[client_ip]
        
        # Decay burst count over time (1 token per second)
        time_passed = now - last_req_time
        burst_count = max(0, burst_count - int(time_passed * 2))  # Decay 2 per second
        
        if burst_count >= self.burst_limit:
            log.warning(f"Burst attack detected from {client_ip}")
            response = JSONResponse(
                {
                    "detail": "Burst attack detected",
                    "endpoint_type": "auth",  # Assuming auth is most sensitive
                    "retry_after": 120,
                },
                status_code=429,
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
