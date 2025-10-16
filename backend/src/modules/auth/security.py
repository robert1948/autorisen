from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Tuple, Dict, Any

from jose import jwt, JWTError
from passlib.context import CryptContext

# ---- Config (env or settings) ----
JWT_SECRET = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY")
JWT_ALG = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_MIN = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", str(60 * 24 * 30)))
JWT_ISS = os.getenv("JWT_ISSUER")
JWT_AUD = os.getenv("JWT_AUDIENCE")

if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET/SECRET_KEY is required")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---- Password helpers ----
def verify_password(plain: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(plain, hashed)
    except Exception:
        return False

# ---- JWT helpers ----
def _now() -> datetime:
    return datetime.now(timezone.utc)

def _encode(payload: Dict[str, Any], minutes: int) -> str:
    n = _now()
    to_encode = dict(payload)
    to_encode.setdefault("iat", int(n.timestamp()))
    to_encode["exp"] = int((n + timedelta(minutes=minutes)).timestamp())
    if JWT_ISS:
        to_encode.setdefault("iss", JWT_ISS)
    if JWT_AUD:
        to_encode.setdefault("aud", JWT_AUD)
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALG)

def create_access_refresh_tokens(*, user_id: int, email: str, role: str) -> Tuple[str, str]:
    base = {"sub": str(user_id), "email": email, "role": role, "type": "access"}
    access = _encode(base, ACCESS_MIN)
    refresh = _encode({**base, "type": "refresh"}, REFRESH_MIN)
    return access, refresh

def decode_access_token(token: str) -> Dict[str, Any]:
    options = {"verify_aud": bool(JWT_AUD), "verify_iss": bool(JWT_ISS)}
    return jwt.decode(
        token,
        JWT_SECRET,
        algorithms=[JWT_ALG],
        audience=(JWT_AUD if JWT_AUD else None),
        issuer=(JWT_ISS if JWT_ISS else None),
        options=options,
    )
