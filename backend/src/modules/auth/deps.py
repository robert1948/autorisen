# backend/src/modules/auth/deps.py
from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Optional, Tuple

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.src.core.redis import (
    cache_user_token_version,
    get_cached_user_token_version,
    is_jti_denied,
)
from backend.src.db.session import get_db
from backend.src.services.security import decode_jwt

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

FORBIDDEN = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
)


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
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
        raise _unauthorized("Not authenticated")
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
        raise _unauthorized("Not authenticated")
    return user


async def get_current_user_with_claims(
    request: Request,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(default=None, convert_underscores=False),
) -> Tuple[Any, Dict[str, Any], str]:
    """Return ``(user, claims, token)`` after enforcing auth guards."""

    token = _token_from_request(request, authorization)

    try:
        claims = decode_jwt(token)
    except ValueError as exc:
        message = str(exc)
        if message == "token expired":
            raise _unauthorized("Token expired") from exc
        raise _unauthorized("Invalid token") from exc

    user = _load_user_from_claims(db, claims)

    if not getattr(user, "is_active", True):
        raise _unauthorized("Not authenticated")

    jti = claims.get("jti")
    if not isinstance(jti, str):
        raise _unauthorized("Invalid token")
    if is_jti_denied(jti):
        raise _unauthorized("Token revoked")

    expected_version = get_cached_user_token_version(getattr(user, "id", ""))
    if expected_version is None:
        expected_version = int(getattr(user, "token_version", 0))
        cache_user_token_version(getattr(user, "id", ""), expected_version)

    try:
        token_version_claim = int(claims.get("token_version", -1))
    except (TypeError, ValueError):
        token_version_claim = -1
    if token_version_claim != int(expected_version):
        raise _unauthorized("Session invalidated")

    # Cache claims for downstream dependencies / logout handling
    request.state.auth_claims = claims
    request.state.auth_token = token

    return user, claims, token


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(default=None, convert_underscores=False),
) -> Any:
    user, _, _ = await get_current_user_with_claims(request, db, authorization)
    return user


async def get_verified_user(
    request: Request,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(default=None, convert_underscores=False),
) -> Any:
    user, _, _ = await get_current_user_with_claims(request, db, authorization)
    if not getattr(user, "is_email_verified", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Check your inbox or resend.",
        )
    return user


def require_roles(*allowed_roles: str) -> Callable:
    """
    Role guard that checks BOTH the scalar ``User.role`` column
    AND the many-to-many ``user_roles`` table.

    A user passes if *any* of the following match an allowed role:
    - ``user.role`` (legacy scalar column)
    - Names of ``Role`` objects linked via ``user.roles`` relationship

    Usage:
        @router.get("/admin")
        async def admin_only(user=Depends(require_roles("admin"))):
            return {"ok": True}
    """
    allowed = {r.lower().strip() for r in allowed_roles}

    async def _dep(user=Depends(get_verified_user)):
        # 1. Check scalar column (fast path)
        scalar_role = _normalize_role(getattr(user, "role", None))
        if scalar_role and scalar_role in allowed:
            return user

        # 2. Check many-to-many roles relationship
        m2m_roles = getattr(user, "roles", None)
        if m2m_roles:
            for role_obj in m2m_roles:
                role_name = _normalize_role(getattr(role_obj, "name", None))
                if role_name and role_name in allowed:
                    return user

        raise FORBIDDEN

    return _dep


def require_permissions(*required_codes: str) -> Callable:
    """
    Permission guard that checks if the user has ALL specified
    permission codes via the many-to-many ``user → roles → permissions``
    chain.

    Usage:
        @router.delete("/documents/{id}")
        async def delete_doc(user=Depends(require_permissions("rag.document.delete"))):
            ...
    """
    required = {c.lower().strip() for c in required_codes}

    async def _dep(user=Depends(get_verified_user)):
        user_perms: set[str] = set()

        # Collect from many-to-many
        m2m_roles = getattr(user, "roles", None)
        if m2m_roles:
            for role_obj in m2m_roles:
                for perm in getattr(role_obj, "permissions", []):
                    code = getattr(perm, "code", "")
                    if code:
                        user_perms.add(code.lower().strip())

        if not required.issubset(user_perms):
            raise FORBIDDEN
        return user

    return _dep


def get_org_context() -> Callable:
    """
    Dependency that extracts the tenant/organization context from
    the ``X-Organization-Id`` header and validates the user is a
    member.

    Returns ``(user, organization_id)`` tuple.

    Usage:
        @router.get("/data")
        async def scoped(ctx=Depends(get_org_context())):
            user, org_id = ctx
            ...
    """

    async def _dep(
        request: Request,
        user=Depends(get_verified_user),
        db: Session = Depends(get_db),
    ):
        org_id = request.headers.get("X-Organization-Id")
        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="X-Organization-Id header is required",
            )

        # Import lazily to avoid circular imports
        try:
            from backend.src.db.models import OrganizationMember
        except ImportError:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Organization support not configured",
            )

        membership = (
            db.query(OrganizationMember)
            .filter(
                OrganizationMember.organization_id == org_id,
                OrganizationMember.user_id == user.id,
            )
            .one_or_none()
        )
        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not a member of this organization",
            )

        return user, org_id

    return _dep
