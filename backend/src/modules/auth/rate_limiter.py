"""
Compatibility shim for legacy imports PLUS lightweight login-attempt gating.

Exports:
- limiter, rate_limit, auth_rate_limit, configure_rate_limit
- allow_login(ip, email) -> (allowed: bool, retry_after_sec: int)
- record_login_attempt(ip, email, success: bool) -> None

Env overrides:
  AUTH_LOGIN_MAX_ATTEMPTS=5
  AUTH_LOGIN_WINDOW_SEC=300    # 5 minutes
  AUTH_LOGIN_BLOCK_SEC=300     # block duration after threshold
"""

from __future__ import annotations

import os
import time
from collections import defaultdict, deque
from typing import Deque, Dict, Tuple

# Re-export core decorators/middleware from the centralized module
from backend.src.core.rate_limit import (
    auth_rate_limit,
    configure_rate_limit,
    limiter,
    rate_limit,
)

__all__ = [
    "limiter",
    "rate_limit",
    "auth_rate_limit",
    "configure_rate_limit",
    "allow_login",
    "record_login_attempt",
]

# ---- Simple in-memory login gate (per (ip,email)) ----
_MAX = int(os.getenv("AUTH_LOGIN_MAX_ATTEMPTS", "5"))
_WIN = int(os.getenv("AUTH_LOGIN_WINDOW_SEC", "300"))  # 5 min sliding window
_BLK = int(os.getenv("AUTH_LOGIN_BLOCK_SEC", "300"))  # 5 min hard block

# attempts[(ip,email)] = deque[timestamps]
_attempts: Dict[Tuple[str, str], Deque[float]] = defaultdict(deque)
# blocks[(ip,email)] = block_until_timestamp
_blocks: Dict[Tuple[str, str], float] = {}


def _now() -> float:
    return time.time()


def _norm(key: Tuple[str, str]) -> Tuple[str, str]:
    ip, email = key
    return (ip or "unknown"), (email or "").lower()


def _prune(key: Tuple[str, str]) -> None:
    """Remove timestamps outside sliding window."""
    key = _norm(key)
    cutoff = _now() - _WIN
    dq = _attempts.get(key)
    if not dq:
        return
    while dq and dq[0] < cutoff:
        dq.popleft()
    if not dq:
        _attempts.pop(key, None)


def allow_login(ip: str, email: str) -> Tuple[bool, int]:
    """
    Returns (allowed, retry_after_sec). If blocked, retry_after_sec > 0.
    """
    key = _norm((ip, email))
    blk_until = _blocks.get(key, 0.0)
    now = _now()
    if blk_until > now:
        return False, int(round(blk_until - now))

    _prune(key)
    dq = _attempts.get(key, deque())
    if len(dq) >= _MAX:
        _blocks[key] = now + _BLK
        return False, _BLK
    return True, 0


def record_login_attempt(ip: str, email: str, success: bool) -> None:
    """
    Track attempts; clear on success.
    """
    key = _norm((ip, email))
    if success:
        _attempts.pop(key, None)
        _blocks.pop(key, None)
        return
    _prune(key)
    _attempts[key].append(_now())
