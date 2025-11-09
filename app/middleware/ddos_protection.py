"""
Lightweight DDoS protection middleware used for local validation.

The implementation keeps in-memory counters to emulate burst detection,
tracks basic IP reputation, and annotates responses with diagnostic headers
that the test-suite expects.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import DefaultDict, Deque, Dict, Tuple

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

ClientKey = Tuple[str, str]


class DDoSProtectionMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        *,
        burst_threshold: int = 20,
        window: int = 60,
        block_duration: int = 120,
        reputation_threshold: int = -5,
    ) -> None:
        super().__init__(app)
        self.ddos_config = {
            "burst_threshold": burst_threshold,
            "window": window,
            "block_duration": block_duration,
            "reputation_threshold": reputation_threshold,
        }
        self.request_times: DefaultDict[ClientKey, Deque[float]] = defaultdict(deque)
        self.blocked_until: Dict[str, float] = {}
        self.ip_reputation: DefaultDict[str, int] = defaultdict(int)
        self.rate_limits: Dict[str, Dict[str, int]] = {
            "general": {"minute": 120, "hour": 3000},
            "auth": {"minute": 60, "hour": 1500},
            "ai": {"minute": 30, "hour": 500},
        }

    async def dispatch(self, request: Request, call_next):
        ip = self._client_ip(request)
        endpoint_type = self.get_endpoint_type(request.url.path)
        now = time.time()

        if self._is_blocked(ip, now):
            self.update_ip_reputation(ip, -1)
            return self._blocked_response(ip, endpoint_type, burst=False)

        self._prune(ip, endpoint_type, now)
        if self.detect_burst_attack(ip, now, endpoint_type):
            duration = self.calculate_block_duration(ip)
            self.blocked_until[ip] = now + duration
            self.update_ip_reputation(ip, -2)
            return self._blocked_response(ip, endpoint_type, burst=True)

        self._record_request(ip, endpoint_type, now)

        response = await call_next(request)

        return self._annotate_response(response, ip, endpoint_type)

    # ------------------------------------------------------------------ helpers
    def get_endpoint_type(self, path: str) -> str:
        if path.startswith("/api/ai"):
            return "ai"
        if path.startswith("/api/auth"):
            return "auth"
        return "general"

    def detect_burst_attack(
        self, ip: str, current_time: float, endpoint_type: str = "general"
    ) -> bool:
        key = (ip, endpoint_type)
        window = self.ddos_config["window"]
        burst_threshold = self.ddos_config["burst_threshold"]
        timestamps = self.request_times[key]
        while timestamps and current_time - timestamps[0] > window:
            timestamps.popleft()
        return len(timestamps) >= burst_threshold

    def calculate_block_duration(self, ip: str) -> int:
        base = self.ddos_config["block_duration"]
        reputation = self.ip_reputation[ip]
        # Increase block time if reputation is poor
        if reputation < self.ddos_config["reputation_threshold"]:
            return int(base * 1.5)
        return base

    def update_ip_reputation(self, ip: str, delta: int) -> int:
        self.ip_reputation[ip] += delta
        # Clamp reputation to avoid runaway values
        self.ip_reputation[ip] = max(-50, min(50, self.ip_reputation[ip]))
        return self.ip_reputation[ip]

    # ------------------------------------------------------------------ internals
    def _client_ip(self, request: Request) -> str:
        client = request.client
        if client:
            return client.host or "unknown"
        return request.headers.get("X-Forwarded-For", "unknown").split(",")[0].strip()

    def _record_request(self, ip: str, endpoint_type: str, timestamp: float) -> None:
        key = (ip, endpoint_type)
        self.request_times[key].append(timestamp)
        self.update_ip_reputation(ip, 1)

    def _prune(self, ip: str, endpoint_type: str, current_time: float) -> None:
        key = (ip, endpoint_type)
        window = self.ddos_config["window"]
        timestamps = self.request_times[key]
        while timestamps and current_time - timestamps[0] > window:
            timestamps.popleft()

    def _is_blocked(self, ip: str, now: float) -> bool:
        until = self.blocked_until.get(ip, 0.0)
        return until > now

    def _remaining(
        self, ip: str, endpoint_type: str, window_seconds: int
    ) -> int:
        key = (ip, endpoint_type)
        now = time.time()
        timestamps = self.request_times[key]
        count = sum(1 for ts in timestamps if now - ts <= window_seconds)
        limit = self.rate_limits.get(endpoint_type, {}).get(
            "minute" if window_seconds == 60 else "hour", 0
        )
        if limit == 0:
            return 0
        return max(limit - count, 0)

    def _annotate_response(
        self, response: Response, ip: str, endpoint_type: str
    ) -> Response:
        headers = response.headers
        headers["X-DDoS-Protection"] = "active"
        headers["X-IP-Reputation"] = str(self.ip_reputation[ip])
        headers["X-Block-Status"] = "allowed"
        headers["X-RateLimit-Type"] = endpoint_type

        rate_conf = self.rate_limits.get(endpoint_type, self.rate_limits["general"])
        headers["X-RateLimit-Limit-Minute"] = str(rate_conf.get("minute", 0))
        headers["X-RateLimit-Remaining-Minute"] = str(self._remaining(ip, endpoint_type, 60))
        if "hour" in rate_conf:
            headers["X-RateLimit-Limit-Hour"] = str(rate_conf["hour"])

        return response

    def _blocked_response(
        self,
        ip: str,
        endpoint_type: str,
        *,
        burst: bool,
    ) -> Response:
        detail = "Burst attack detected" if burst else "Temporarily blocked"
        self.blocked_until.setdefault(
            ip, time.time() + self.ddos_config["block_duration"]
        )
        body = {
            "detail": detail,
            "endpoint_type": endpoint_type,
            "retry_after": int(self.blocked_until[ip] - time.time()),
        }
        response = JSONResponse(body, status_code=429)
        response.headers["Retry-After"] = str(body["retry_after"])
        response.headers["X-DDoS-Protection"] = "active"
        response.headers["X-IP-Reputation"] = str(self.ip_reputation[ip])
        response.headers["X-Block-Status"] = "blocked"
        response.headers["X-RateLimit-Type"] = endpoint_type
        rate_conf = self.rate_limits.get(endpoint_type, self.rate_limits["general"])
        response.headers["X-RateLimit-Limit-Minute"] = str(rate_conf.get("minute", 0))
        response.headers["X-RateLimit-Limit-Hour"] = str(rate_conf.get("hour", 0))
        return response


__all__ = ["DDoSProtectionMiddleware"]
