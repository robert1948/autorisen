# backend/src/modules/auth/deps.py
from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Optional

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.src.db.session import get_db

# --- Minimal, local JWT decoder (no external security import) ---
try:
    from jose import JWTError, jwt  # python-jose[cryptography]
except Exception as e:  # pragma: no cover
    raise RuntimeError(
        "python-jose is required. Add `python-jose[cryptography]` to requirements.txt"
    ) from e

try:
    from backend.src.settings import settings  # must expose JWT secret/algorithm

    JWT_SECRET = getattr(settings, "JWT_SECRET", None) or getattr(settings, "SECRET_KEY", None)
    JWT_ALG = getattr(settings, "JWT_ALGORITHM", "HS256")
    JWT_ISS = getattr(settings, "JWT_ISSUER", None)
    JWT_AUD = getattr(settings, "JWT_AUDIENCE", None)
except Exception:
    import os

    JWT_SECRET = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY")
    JWT_ALG = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ISS = os.getenv("JWT_ISSUER")
    JWT_AUD = os.getenv("JWT_AUDIENCE")

if not JWT_SECRET:
    # We avoid crashing early; requests without a token will 401 anyway.
    logging.getLogger("auth.deps").warning("JWT secret missing in settings/env")


def _decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode & validate an access token using local settings.
    - If ISS/AUD are unset, we don't enforce them.
    """
    if not JWT_SECRET:
        raise JWTError("JWT secret is not configured")

    options = {"verify_aud": bool(JWT_AUD), "verify_iss": bool(JWT_ISS)}
    return jwt.decode(
        token,
        JWT_SECRET,
        algorithms=[JWT_ALG],
        audience=JWT_AUD if JWT_AUD else None,
        issuer=JWT_ISS if JWT_ISS else None,
        options=options,
    )


log = logging.getLogger("auth.deps")

# Try to import the User model from common locations
User = None  # type: ignore
_user_import_err = None
for path in (
    "backend.src.db.models",
    "backend.src.modules.auth.models",  # preferred
    "backend.src.modules.user.models",
    "backend.src.modules.accounts.models",
    "backend.src.models.user",
):
    try:
        module = __import__(path, fromlist=["User"])
        User = getattr(module, "User", None)
        if User is not None:
            break
    except Exception as e:
        _user_import_err = e

if User is None:
    log.error("Could not import User model; last import error: %s", _user_import_err)

UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Not authenticated",
    headers={"WWW-Authenticate": "Bearer"},
)

FORBIDDEN = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Not authorized",
)


def _bearer_from_header(auth_header: Optional[str]) -> Optional[str]:
    if not auth_header:
        return None
    parts = auth_header.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


def _token_from_request(request: Request, authorization: Optional[str]) -> str:
    """
    Look for the access token in:
    1) Authorization: Bearer <token>
    2) Cookie: access_token=<token>   (optional convenience)
    """
    token = _bearer_from_header(authorization)
    if not token:
        token = request.cookies.get("access_token")
    if not token:
        raise UNAUTHORIZED
    return token


def _normalize_role(role: Optional[str]) -> Optional[str]:
    return role.lower().strip() if isinstance(role, str) else role


def _load_user_from_claims(db: Session, claims: dict) -> Any:
    """
    Load user by id (sub/user_id/uid) or by email, directly via ORM.
    """
    if User is None:
        raise RuntimeError("User model not found; fix import path in auth/deps.py")

    user = None
    # Prefer explicit user identifiers; some legacy tokens store the email in `sub`.
    user_id = claims.get("user_id") or claims.get("uid") or claims.get("sub")
    email = claims.get("email")

    try:
        if user_id is not None:
            user = db.query(User).filter(User.id == user_id).one_or_none()
    except Exception as e:
        log.warning("User lookup by id failed: %s", e)

    if user is None and email:
        try:
            user = db.query(User).filter(User.email == str(email).lower()).one_or_none()
        except Exception as e:
            log.warning("User lookup by email failed: %s", e)

    if not user:
        raise UNAUTHORIZED
    return user


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(default=None, convert_underscores=False),
) -> Any:
    """
    Decode the access token, load the current user, and apply basic gates.
    """
    token = _token_from_request(request, authorization)

    try:
        claims = _decode_access_token(token)
    except Exception as e:
        log.info("JWT decode failed: %s", e)
        raise UNAUTHORIZED

    user = _load_user_from_claims(db, claims)

    # Basic account gates (align with router)
    if not getattr(user, "is_active", True):
        raise UNAUTHORIZED

    # Some legacy flows do not mark email verification immediately; allow access unless
    # the application explicitly disables unverified logins elsewhere.
    # We still surface the flag via the response schemas.

    return user


def require_roles(*allowed_roles: str) -> Callable:
    """
    Usage:
        @router.get("/admin")
        async def admin_only(user=Depends(require_roles("admin"))):
            return {"ok": True}
    """
    allowed = {r.lower().strip() for r in allowed_roles}

    async def _dep(user=Depends(get_current_user)):
        role = _normalize_role(getattr(user, "role", None))
        if not role or role not in allowed:
            raise FORBIDDEN
        return user

    return _dep
