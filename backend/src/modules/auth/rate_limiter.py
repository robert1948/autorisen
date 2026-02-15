"""
Compatibility shim for legacy imports PLUS lightweight login-attempt gating.

Exports:
- limiter, rate_limit, auth_rate_limit, configure_rate_limit
- allow_login(ip, email) -> (allowed: bool, retry_after_sec: int)
- record_login_attempt(ip, email, success: bool) -> None

Uses the login_audits table for persistent rate limiting that survives
dyno restarts. Falls back to in-memory tracking if DB is unavailable.

Env overrides:
  AUTH_LOGIN_MAX_ATTEMPTS=5
  AUTH_LOGIN_WINDOW_SEC=300    # 5 minutes
  AUTH_LOGIN_BLOCK_SEC=300     # block duration after threshold
"""

from __future__ import annotations

import logging
import os
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from typing import Deque, Dict, Tuple

from sqlalchemy import text

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

logger = logging.getLogger(__name__)

# ---- Configuration ----
_MAX = int(os.getenv("AUTH_LOGIN_MAX_ATTEMPTS", "5"))
_WIN = int(os.getenv("AUTH_LOGIN_WINDOW_SEC", "300"))  # 5 min sliding window
_BLK = int(os.getenv("AUTH_LOGIN_BLOCK_SEC", "300"))  # 5 min hard block

# ---- In-memory fallback (used when DB is unavailable) ----
_attempts: Dict[Tuple[str, str], Deque[float]] = defaultdict(deque)
_blocks: Dict[Tuple[str, str], float] = {}


def _now() -> float:
    return time.time()


def _norm(key: Tuple[str, str]) -> Tuple[str, str]:
    ip, email = key
    return (ip or "unknown"), (email or "").lower()


def _get_db_session():
    """Try to get a DB session; returns None if unavailable."""
    try:
        from backend.src.db.session import SessionLocal
        return SessionLocal()
    except Exception:
        return None


def _db_failed_count(db, ip: str, email: str, window_seconds: int) -> int:
    """Count failed login attempts in the sliding window from login_audits."""
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=window_seconds)
    row = db.execute(
        text(
            "SELECT COUNT(*) FROM login_audits "
            "WHERE ip_address = :ip AND LOWER(email) = :email "
            "AND success = false AND created_at >= :cutoff"
        ),
        {"ip": ip, "email": email, "cutoff": cutoff},
    ).scalar()
    return int(row or 0)


def _db_last_success(db, ip: str, email: str, since: datetime):
    """Check if there was a successful login after the window cutoff."""
    row = db.execute(
        text(
            "SELECT MAX(created_at) FROM login_audits "
            "WHERE ip_address = :ip AND LOWER(email) = :email "
            "AND success = true AND created_at >= :since"
        ),
        {"ip": ip, "email": email, "since": since},
    ).scalar()
    return row


def allow_login(ip: str, email: str) -> Tuple[bool, int]:
    """
    Returns (allowed, retry_after_sec). If blocked, retry_after_sec > 0.
    Uses database for persistent tracking, falls back to in-memory.
    """
    key = _norm((ip, email))
    db = _get_db_session()

    if db is not None:
        try:
            failed_count = _db_failed_count(db, key[0], key[1], _WIN)
            if failed_count >= _MAX:
                # Check if there's been a successful login that resets the block
                cutoff = datetime.now(timezone.utc) - timedelta(seconds=_WIN)
                last_ok = _db_last_success(db, key[0], key[1], cutoff)
                if last_ok is None:
                    return False, _BLK
            return True, 0
        except Exception as exc:
            logger.warning("DB rate limit check failed, using in-memory: %s", exc)
        finally:
            db.close()

    # Fallback: in-memory
    blk_until = _blocks.get(key, 0.0)
    now = _now()
    if blk_until > now:
        return False, int(round(blk_until - now))

    cutoff = now - _WIN
    dq = _attempts.get(key, deque())
    while dq and dq[0] < cutoff:
        dq.popleft()
    if len(dq) >= _MAX:
        _blocks[key] = now + _BLK
        return False, _BLK
    return True, 0


def record_login_attempt(ip: str, email: str, success: bool) -> None:
    """
    Track attempts. The login_audits table is written to by the audit module;
    this function only manages the in-memory fallback state.
    On success, clear in-memory blocks so fallback stays consistent.
    """
    key = _norm((ip, email))
    if success:
        _attempts.pop(key, None)
        _blocks.pop(key, None)
        return
    # Update in-memory fallback
    cutoff = _now() - _WIN
    dq = _attempts[key]
    while dq and dq[0] < cutoff:
        dq.popleft()
    dq.append(_now())
