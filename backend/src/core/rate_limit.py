"""Shared rate limiting configuration."""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.src.core.config import settings

auth_rate_limit = f"{settings.rate_limit_per_min}/minute"
limiter = Limiter(key_func=get_remote_address, default_limits=[])

