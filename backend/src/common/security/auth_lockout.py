from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Optional, Tuple

from backend.src.core.config import settings
from backend.src.core.redis import get_store

_LOCKOUT_LUA = """
local key = KEYS[1]
local now = tonumber(ARGV[1])
local lock_after = tonumber(ARGV[2])
local lock_seconds = tonumber(ARGV[3])
local ttl_seconds = tonumber(ARGV[4])
local action = ARGV[5]

local fail_count = tonumber(redis.call('HGET', key, 'fail_count') or '0')
local locked_until = tonumber(redis.call('HGET', key, 'locked_until') or '0')

if action == 'success' then
  redis.call('DEL', key)
  return {0, 0, 0}
end

if locked_until > now then
  return {1, locked_until, fail_count}
end

if action == 'fail' then
  fail_count = tonumber(redis.call('HINCRBY', key, 'fail_count', 1) or '0')
  if fail_count >= lock_after then
    locked_until = now + lock_seconds
    redis.call('HSET', key, 'locked_until', locked_until)
  end
  redis.call('EXPIRE', key, ttl_seconds)
  if locked_until > now then
    return {1, locked_until, fail_count}
  end
  return {0, 0, fail_count}
end

-- action == 'check'
return {0, locked_until, fail_count}
""".strip()


@dataclass(frozen=True)
class LockoutPolicy:
    lock_after_failures: int = 5
    lock_seconds: int = 15 * 60


POLICY = LockoutPolicy()


def _enabled() -> bool:
    flag = os.getenv("AUTH_LOCKOUT_ENABLED")
    if flag is not None:
        return flag.strip().lower() in {"1", "true", "yes"}

    if settings.env == "test":
        return os.getenv("AUTH_LOCKOUT_TESTING", "").strip().lower() in {
            "1",
            "true",
            "yes",
        }

    return True


def _key(email_norm: str) -> str:
    return f"lockout:email:{email_norm}"


def check_lockout(email_norm: str) -> Tuple[bool, Optional[int], int]:
    """Return (locked, locked_until_ts, fail_count)."""

    if not _enabled() or not email_norm:
        return (False, None, 0)

    store = get_store()
    now = int(time.time())

    if hasattr(store, "eval"):
        try:
            locked, locked_until, fail_count = store.eval(  # type: ignore[attr-defined]
                _LOCKOUT_LUA,
                1,
                _key(email_norm),
                now,
                POLICY.lock_after_failures,
                POLICY.lock_seconds,
                max(POLICY.lock_seconds, 900),
                "check",
            )
            locked_i = int(locked)
            locked_until_i = int(locked_until)
            fail_count_i = int(fail_count)
            return (locked_i == 1, locked_until_i or None, fail_count_i)
        except Exception:
            pass

    state = store.get(_key(email_norm))
    if not isinstance(state, dict):
        return (False, None, 0)

    locked_until = int(state.get("locked_until") or 0)
    fail_count = int(state.get("fail_count") or 0)
    if locked_until and locked_until > now:
        return (True, locked_until, fail_count)

    return (False, locked_until or None, fail_count)


def record_failure(email_norm: str) -> Tuple[bool, Optional[int], int]:
    """Increment failure count and return (locked, locked_until_ts, fail_count)."""

    if not _enabled() or not email_norm:
        return (False, None, 0)

    store = get_store()
    now = int(time.time())

    if hasattr(store, "eval"):
        try:
            locked, locked_until, fail_count = store.eval(  # type: ignore[attr-defined]
                _LOCKOUT_LUA,
                1,
                _key(email_norm),
                now,
                POLICY.lock_after_failures,
                POLICY.lock_seconds,
                max(POLICY.lock_seconds, 900),
                "fail",
            )
            locked_i = int(locked)
            locked_until_i = int(locked_until)
            fail_count_i = int(fail_count)
            return (locked_i == 1, locked_until_i or None, fail_count_i)
        except Exception:
            pass

    state = store.get(_key(email_norm))
    if not isinstance(state, dict):
        state = {"fail_count": 0, "locked_until": 0}

    locked_until = int(state.get("locked_until") or 0)
    fail_count = int(state.get("fail_count") or 0)

    if locked_until and locked_until > now:
        return (True, locked_until, fail_count)

    fail_count += 1
    if fail_count >= POLICY.lock_after_failures:
        locked_until = now + POLICY.lock_seconds

    state["fail_count"] = fail_count
    state["locked_until"] = locked_until

    store.setex(_key(email_norm), max(POLICY.lock_seconds, 900), state)

    return (locked_until > now, locked_until or None, fail_count)


def clear_lockout(email_norm: str) -> None:
    if not _enabled() or not email_norm:
        return

    store = get_store()
    now = int(time.time())

    if hasattr(store, "eval"):
        try:
            store.eval(  # type: ignore[attr-defined]
                _LOCKOUT_LUA,
                1,
                _key(email_norm),
                now,
                POLICY.lock_after_failures,
                POLICY.lock_seconds,
                max(POLICY.lock_seconds, 900),
                "success",
            )
            return
        except Exception:
            pass

    try:
        store.delete(_key(email_norm))
    except Exception:
        return
