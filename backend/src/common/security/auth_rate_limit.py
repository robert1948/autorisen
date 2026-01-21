from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from typing import Optional

from fastapi import HTTPException, Request, status

from backend.src.core.config import settings
from backend.src.core.redis import incr_with_ttl


@dataclass(frozen=True)
class AuthRateLimitPolicy:
    ip_max: int
    ip_window_sec: int
    email_max: int
    email_window_sec: int


# Defaults (can be overridden via env if needed)
POLICIES: dict[str, AuthRateLimitPolicy] = {
    "login": AuthRateLimitPolicy(
        ip_max=10, ip_window_sec=60, email_max=5, email_window_sec=60
    ),
    "forgot_password": AuthRateLimitPolicy(
        ip_max=5, ip_window_sec=60, email_max=3, email_window_sec=60
    ),
    "reset_password": AuthRateLimitPolicy(
        ip_max=5, ip_window_sec=60, email_max=0, email_window_sec=60
    ),
}


def _enabled() -> bool:
    flag = os.getenv("AUTH_RATE_LIMIT_ENABLED")
    if flag is not None:
        return flag.strip().lower() in {"1", "true", "yes"}

    # Default: enabled for non-test envs; disabled in tests unless explicitly turned on.
    if settings.env == "test":
        return os.getenv("AUTH_RATE_LIMIT_TESTING", "").strip().lower() in {
            "1",
            "true",
            "yes",
        }
    return True


def normalize_email(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    candidate = value.strip().lower()
    return candidate or None


def _hash_email(email: str) -> str:
    return hashlib.sha256(email.encode("utf-8")).hexdigest()


def get_client_ip(request: Request) -> str:
    # Prefer proxy-provided client IP when present.
    xff = (request.headers.get("x-forwarded-for") or "").strip()
    if xff:
        # XFF may contain multiple values: client, proxy1, proxy2
        first = xff.split(",", 1)[0].strip()
        if first:
            return first

    xri = (request.headers.get("x-real-ip") or "").strip()
    if xri:
        return xri

    if request.client and request.client.host:
        return request.client.host

    return "unknown"


def _ip_key(endpoint: str, ip: str) -> str:
    return f"rl:auth:ip:{endpoint}:{ip}"


def _email_key(endpoint: str, email: str) -> str:
    # Hash to avoid putting raw email addresses in Redis keys.
    return f"rl:auth:email:{endpoint}:{_hash_email(email)}"


def enforce_auth_rate_limit(
    request: Request,
    *,
    endpoint: str,
    email: Optional[str] = None,
) -> None:
    """Enforce per-endpoint rate limits keyed by (IP, endpoint) and (email, endpoint)."""

    if not _enabled():
        return

    policy = POLICIES.get(endpoint)
    if policy is None:
        return

    ip = get_client_ip(request)

    # IP limit
    ip_count = incr_with_ttl(_ip_key(endpoint, ip), policy.ip_window_sec)
    if ip_count > policy.ip_max:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests",
            headers={"Retry-After": str(policy.ip_window_sec)},
        )

    # Email limit (only when present)
    normalized = normalize_email(email)
    if normalized and policy.email_max > 0:
        email_count = incr_with_ttl(
            _email_key(endpoint, normalized), policy.email_window_sec
        )
        if email_count > policy.email_max:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests",
                headers={"Retry-After": str(policy.email_window_sec)},
            )
