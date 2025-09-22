# backend/app/core/security.py
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
import jwt  # from python-jose or PyJWT; using PyJWT already in reqs
import uuid
import json
import os
import redis
from passlib.context import CryptContext

JWT_SECRET = os.getenv("JWT_SECRET_KEY", "dev-jwt")
if JWT_SECRET == "dev-jwt":
    # Warn at runtime; in production this must be set to a secure random value
    # and ideally sourced from secrets (KMS/secret manager).
    pass
JWT_ALG    = os.getenv("JWT_ALG", "HS256")
ACCESS_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRES_MIN", "15"))
REFRESH_D  = int(os.getenv("REFRESH_TOKEN_EXPIRES_DAYS", "7"))

REDIS_URL  = os.getenv("REDIS_URL", "redis://redis:6379")
r = redis.Redis.from_url(REDIS_URL, decode_responses=True)

# password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def _now():
    return datetime.now(timezone.utc)

def create_access_token(user_id: int) -> str:
    now = _now()
    exp = now + timedelta(minutes=ACCESS_MIN)
    # Keep standard `iat` in seconds for JWT libraries but add `iat_ms` for
    # higher-precision checks against password_changed_at.
    now_ts = int(now.timestamp())
    now_ms = int(now.timestamp() * 1000)
    payload = {"sub": str(user_id), "type": "access", "exp": int(exp.timestamp()), "iat": now_ts, "iat_ms": now_ms}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def create_refresh_token(user_id: int) -> Tuple[str, str, int]:
    jti = uuid.uuid4().hex
    now = _now()
    exp_dt = now + timedelta(days=REFRESH_D)
    exp = int(exp_dt.timestamp())
    # Keep `iat` seconds and include `iat_ms` for precision
    now_ts = int(now.timestamp())
    now_ms = int(now.timestamp() * 1000)
    payload = {"sub": str(user_id), "type": "refresh", "jti": jti, "exp": exp, "iat": now_ts, "iat_ms": now_ms}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)
    # store in redis (TTL)
    ttl = int((exp_dt - _now()).total_seconds())
    r.setex(f"rt:{jti}", ttl, json.dumps({"uid": user_id, "exp": exp}))
    return token, jti, exp

def revoke_refresh_jti(jti: str):
    r.delete(f"rt:{jti}")

def is_refresh_jti_active(jti: str) -> bool:
    return r.exists(f"rt:{jti}") == 1

def decode(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])


def decode_token(token: str) -> dict:
    """Backward-compatible name used by other modules."""
    return decode(token)


def create_verification_token(user_id: int, expires_minutes: int = 60*24) -> str:
    """Create a short-lived verification token (default 24 hours)."""
    from datetime import timedelta
    now = _now()
    exp = now + timedelta(minutes=expires_minutes)
    # include iat and iat_ms for consistency
    payload = {"sub": str(user_id), "type": "verify", "exp": int(exp.timestamp()), "iat": int(now.timestamp()), "iat_ms": int(now.timestamp() * 1000)}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def is_verification_token(token: str) -> bool:
    try:
        payload = decode(token)
        return payload.get("type") == "verify"
    except Exception:
        return False


def create_reset_token(user_id: int, expires_minutes: int = 60) -> str:
    """Create a short-lived password reset token (default 60 minutes)."""
    from datetime import timedelta
    now = _now()
    exp = now + timedelta(minutes=expires_minutes)
    # include iat and iat_ms so resets can be precisely compared against password_changed_at
    payload = {"sub": str(user_id), "type": "reset", "exp": int(exp.timestamp()), "iat": int(now.timestamp()), "iat_ms": int(now.timestamp() * 1000)}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def is_reset_token(token: str) -> bool:
    try:
        payload = decode(token)
        return payload.get("type") == "reset"
    except Exception:
        return False

def rotate_refresh(token: str) -> Tuple[int, str]:
    data = decode(token)
    if data.get("type") != "refresh":
        raise ValueError("Not a refresh token")
    jti = data.get("jti")
    if not jti or not is_refresh_jti_active(jti):
        raise ValueError("Refresh revoked or expired")
    uid = int(data["sub"])
    # revoke old
    revoke_refresh_jti(jti)
    # issue new
    new_refresh, new_jti, _ = create_refresh_token(uid)
    return uid, new_refresh
