# backend/src/modules/auth/router.py
from __future__ import annotations

import asyncio
import inspect
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Optional

from fastapi import (
    APIRouter,
    Body,
    Depends,
    Header,
    HTTPException,
    Request,
    Response,
    status,
)
from pydantic import BaseModel, EmailStr, constr, field_validator
from sqlalchemy.orm import Session

from backend.src.core.config import settings
from backend.src.db.session import get_db

from .csrf import issue_csrf_token, require_csrf_token
from .deps import get_current_user
from .rate_limiter import allow_login, record_login_attempt
from .security import create_access_refresh_tokens, verify_password

log = logging.getLogger("auth")
router = APIRouter(tags=["auth"])

try:
    from .schemas import UserRole as ServiceUserRole  # type: ignore
except Exception:
    ServiceUserRole = None

# ---------------------------
# Schemas
# ---------------------------


class LoginIn(BaseModel):
    email: EmailStr
    password: constr(min_length=1, max_length=256)


class TokensOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class CsrfTokenOut(BaseModel):
    csrf_token: str


class RegisterStep1In(BaseModel):
    email: EmailStr
    first_name: constr(strip_whitespace=True, max_length=50)
    last_name: constr(strip_whitespace=True, max_length=50)
    password: constr(min_length=1, max_length=256)
    confirm_password: constr(min_length=1, max_length=256)
    role: constr(strip_whitespace=True, min_length=3, max_length=40)
    recaptcha_token: Optional[str] = None

    @field_validator("password", "confirm_password")
    @classmethod
    def _password_policy(cls, value: str) -> str:
        if len(value or "") < 12:
            raise ValueError("Password must be at least 12 characters long")
        return value


class RegisterStep1Out(BaseModel):
    temp_token: str


class Profile(BaseModel):
    class Config:
        extra = "allow"


class RegisterStep2In(BaseModel):
    company_name: constr(strip_whitespace=True, max_length=100)
    profile: Profile


class RegisterStep2Out(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[str] = None
    user: dict


class MeOut(BaseModel):
    id: str
    email: EmailStr
    first_name: str
    last_name: str
    role: str
    is_active: bool
    email_verified: bool


class RefreshIn(BaseModel):
    refresh_token: str


class RefreshOut(BaseModel):
    access_token: str
    refresh_token: str
    expires_at: Optional[str] = None


# ---------------------------
# Helpers
# ---------------------------

INVALID_CREDENTIALS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid credentials",
)

REFRESH_COOKIE_NAME = "refresh_token"


def _coerce_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str):
        try:
            # Accept ISO strings with/without timezone
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    return None


def _set_refresh_cookie(response: Response, token: str, *, expires_at: Any = None) -> None:
    expires = _coerce_datetime(expires_at)
    max_age = None
    if expires:
        remaining = int((expires - datetime.now(timezone.utc)).total_seconds())
        max_age = remaining if remaining > 0 else 0
    response.set_cookie(
        REFRESH_COOKIE_NAME,
        token,
        httponly=True,
        secure=False,  # environment may terminate TLS upstream
        samesite="lax",
        path="/api/auth",
        max_age=max_age,
        expires=expires,
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(REFRESH_COOKIE_NAME, path="/api/auth")


def _resolve_refresh_token(payload: Optional[RefreshIn], request: Request) -> Optional[str]:
    if payload and payload.refresh_token:
        return payload.refresh_token
    return request.cookies.get(REFRESH_COOKIE_NAME)


def _normalize_email(e: str) -> str:
    return e.strip().lower()


def _normalize_role(r: str) -> str:
    return r.strip().lower()


def _adapt_role_for_service(role: str) -> Any:
    if not role:
        return role
    candidates = {
        role,
        role.strip(),
        role.strip().lower(),
        role.strip().title(),
        role.strip().upper(),
    }
    if ServiceUserRole:
        for cand in candidates:
            if not cand:
                continue
            try:
                return ServiceUserRole(cand)  # type: ignore[call-arg]
            except Exception:
                try:
                    return ServiceUserRole[str(cand).upper()]  # type: ignore[index]
                except Exception:
                    continue
    return role


# ---- User lookup via ORM (no service import) ----
User = None  # type: ignore
_last_user_err: Optional[BaseException] = None
_resolved_user_path: Optional[str] = None
for _path in (
    "backend.src.db.models",  # current location
    "backend.src.modules.auth.models",  # historical fallbacks
    "backend.src.modules.user.models",
    "backend.src.modules.accounts.models",
):
    try:
        _mod = __import__(_path, fromlist=["User"])
        User = getattr(_mod, "User", None)
        if User is not None:
            _resolved_user_path = _path
            break
    except Exception as e:
        _last_user_err = e

if User is None:
    log.error("auth.router: User model could not be imported; last_error=%s", _last_user_err)
else:
    log.debug("auth.router: User model resolved from %s", _resolved_user_path)


def _get_user_by_email(db: Session, email: str):
    if User is None:
        raise RuntimeError("User model not available — adjust import path in auth/router.py")
    return db.query(User).filter(User.email == email).one_or_none()


# ---- Registration function shims (relative import; support both namings) ----
_begin_reg: Optional[Callable[..., Any]] = None
_complete_reg: Optional[Callable[..., Any]] = None
_refresh_access: Optional[Callable[..., Any]] = None
_login_service: Optional[Callable[..., Any]] = None
_revoke_refresh_service: Optional[Callable[..., Any]] = None
try:
    from . import service as auth_service  # relative import prevents path drift
except Exception as e:
    auth_service = None
    log.warning("auth.router: could not import .service: %s", e)


def _pick_service_fn(candidates: list[str]) -> Optional[Callable[..., Any]]:
    if auth_service is None:
        return None
    for name in candidates:
        fn = getattr(auth_service, name, None)
        if callable(fn):
            return fn
    return None


_begin_reg = _pick_service_fn(["begin_registration_step1", "begin_registration"])
_complete_reg = _pick_service_fn(["complete_registration_step2", "complete_registration"])
_refresh_access = _pick_service_fn(["refresh_access_token"])
_login_service = _pick_service_fn(["login"])
_revoke_refresh_service = _pick_service_fn(["revoke_refresh_token", "revoke_refresh"])


def _begin_registration_adapter(
    db: Session,
    *,
    email: str,
    first_name: str,
    last_name: str,
    password_plain: str,
    role: str,
) -> str:
    if not _begin_reg:
        raise RuntimeError(
            "Registration function not found in auth.service "
            "(looked for begin_registration_step1 / begin_registration)"
        )
    params = inspect.signature(_begin_reg).parameters  # type: ignore[arg-type]
    kwargs: dict[str, Any] = {
        "db": db,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "role": _adapt_role_for_service(role),
    }
    if "password_plain" in params:
        kwargs["password_plain"] = password_plain
    elif "password" in params:
        kwargs["password"] = password_plain
    elif "password_value" in params:
        kwargs["password_value"] = password_plain
    else:
        kwargs["password"] = password_plain

    result = _begin_reg(**kwargs)  # type: ignore[misc]
    if isinstance(result, str):
        return result
    if isinstance(result, dict) and "temp_token" in result:
        return str(result["temp_token"])
    temp = getattr(result, "temp_token", None)
    if temp:
        return str(temp)
    raise RuntimeError("Registration function did not return a temp token")


def _complete_registration_adapter(db: Session, *, temp_token: str, company: dict, profile: dict):
    if not _complete_reg:
        raise RuntimeError(
            "Completion function not found in auth.service "
            "(looked for complete_registration_step2 / complete_registration)"
        )
    params = inspect.signature(_complete_reg).parameters  # type: ignore[arg-type]
    company_name = None
    if isinstance(company, dict):
        company_name = (
            company.get("company_name")
            or company.get("name")
            or company.get("company")
            or company.get("value")
        )
    elif isinstance(company, str):
        company_name = company

    kwargs: dict[str, Any] = {"db": db, "temp_token": temp_token}
    if "company_name" in params:
        kwargs["company_name"] = company_name
    elif "company" in params:
        kwargs["company"] = company
    if "profile" in params:
        kwargs["profile"] = profile
    elif "profile_data" in params:
        kwargs["profile_data"] = profile

    result = _complete_reg(**kwargs)  # type: ignore[misc]

    if isinstance(result, dict):
        return result

    if isinstance(result, tuple):
        access_token = result[0] if len(result) > 0 else None
        refresh_token = result[1] if len(result) > 1 else None
        expires_at = result[2] if len(result) > 2 else None
        user_obj = result[3] if len(result) > 3 else None
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": expires_at.isoformat() if hasattr(expires_at, "isoformat") else expires_at,
            "user": _serialize_user(user_obj),
        }

    return result


def _refresh_access_token_adapter(db: Session, refresh_token: str) -> dict:
    if not _refresh_access:
        raise RuntimeError("Refresh function not available in auth.service")

    result = _refresh_access(db=db, refresh_token=refresh_token)  # type: ignore[misc]

    if isinstance(result, dict):
        return result

    if isinstance(result, tuple):
        access_token = result[0] if len(result) > 0 else None
        expires_at = result[1] if len(result) > 1 else None
        new_refresh = result[2] if len(result) > 2 else None
        return {
            "access_token": access_token,
            "expires_at": expires_at.isoformat() if hasattr(expires_at, "isoformat") else expires_at,
            "refresh_token": new_refresh,
        }

    return {
        "access_token": None,
        "expires_at": None,
        "refresh_token": None,
    }


def _serialize_user(user: Any) -> dict:
    if user is None:
        return {}
    data = {
        "id": getattr(user, "id", None),
        "email": getattr(user, "email", None),
        "first_name": getattr(user, "first_name", None),
        "last_name": getattr(user, "last_name", None),
        "role": getattr(user, "role", None),
        "is_active": getattr(user, "is_active", getattr(user, "active", None)),
        "email_verified": getattr(user, "email_verified", getattr(user, "is_email_verified", None)),
        "company_name": getattr(user, "company_name", None),
    }

    profile = getattr(user, "profile", None)
    if profile is not None:
        data["profile"] = getattr(profile, "profile", profile)

    return data


# -------------
# Health (quick)
# -------------


@router.get("/health", include_in_schema=False)
async def auth_health():
    return {"ok": True}


@router.get("/csrf", response_model=CsrfTokenOut, status_code=200)
async def csrf_token(response: Response):
    token = issue_csrf_token(response)
    return CsrfTokenOut(csrf_token=token)


# ---------------------------
# Registration — Step 1 (init)
# ---------------------------


@router.post("/register/step1", response_model=RegisterStep1Out, status_code=201)
async def register_step1(
    payload: RegisterStep1In,
    db: Session = Depends(get_db),
    _: None = Depends(require_csrf_token),
):
    email = _normalize_email(payload.email)
    role = _normalize_role(payload.role)

    # Optional: reCAPTCHA enforcement unless disabled
    if not getattr(settings, "disable_recaptcha", False):
        if not payload.recaptcha_token:
            raise HTTPException(status_code=400, detail="Missing reCAPTCHA token")
        # TODO: verify token server-side if required

    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    try:
        temp_token = _begin_registration_adapter(
            db=db,
            email=email,
            first_name=payload.first_name.strip(),
            last_name=payload.last_name.strip(),
            password_plain=payload.password,
            role=role,
        )
        log.info("register_step1_ok email=%s role=%s", email, role)
        return RegisterStep1Out(temp_token=temp_token)
    except ValueError as ve:
        log.warning("register_step1_conflict email=%s err=%s", email, ve)
        raise HTTPException(status_code=409, detail=str(ve)) from ve
    except HTTPException:
        raise
    except Exception as e:
        log.exception("register_step1_error email=%s: %s", email, e)
        raise HTTPException(status_code=500, detail="Registration failed") from e


# -----------------------------
# Registration — Step 2 (commit)
# -----------------------------


@router.post("/register/step2", response_model=RegisterStep2Out, status_code=200)
async def register_step2(
    payload: RegisterStep2In,
    db: Session = Depends(get_db),
    _: None = Depends(require_csrf_token),
    authorization: Optional[str] = Header(default=None, convert_underscores=False),
) -> RegisterStep2Out:
    bearer_parts = (authorization or "").split()
    temp_token = bearer_parts[1] if len(bearer_parts) == 2 and bearer_parts[0].lower() == "bearer" else None
    if not temp_token:
        raise HTTPException(status_code=401, detail="Missing registration token")
    try:
        result = _complete_registration_adapter(
            db=db,
            temp_token=temp_token,
            company={"company_name": payload.company_name},
            profile=payload.profile.model_dump(),
        )
        if isinstance(result, dict):
            log.info(
                "register_step2_ok email=%s user_id=%s",
                result.get("user", {}).get("email"),
                result.get("user", {}).get("id"),
            )
            expires_at = result.get("expires_at")
            return RegisterStep2Out(
                access_token=result.get("access_token"),
                refresh_token=result.get("refresh_token"),
                expires_at=expires_at,
                user=result.get("user", {}),
            )

        log.info("register_step2_ok (non-dict result) type=%s", type(result).__name__)
        return RegisterStep2Out(access_token="", refresh_token=None, expires_at=None, user={})
    except ValueError as ve:
        log.warning("register_step2_invalid temp: %s", ve)
        raise HTTPException(status_code=400, detail=str(ve)) from ve
    except HTTPException:
        raise
    except Exception as e:
        log.exception("register_step2_error: %s", e)
        raise HTTPException(status_code=500, detail="Registration failed") from e


# -----------
# Login Route
# -----------


@router.post("/login", response_model=TokensOut, status_code=200)
async def login(
    payload: LoginIn,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    user_agent: Optional[str] = Header(default=None),
    _: None = Depends(require_csrf_token),
):
    email = _normalize_email(payload.email)

    ip = request.client.host if request.client else "unknown"
    allowed, retry_after = allow_login(ip, email)
    if not allowed:
        log.warning("login_rate_limited email=%s ip=%s retry=%s", email, ip, retry_after)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts",
            headers={"Retry-After": str(retry_after)},
        )

    user = _get_user_by_email(db, email)
    user_found = bool(user)
    log.info("login_attempt email=%s found=%s ip=%s ua=%s", email, user_found, ip, user_agent)

    if _login_service:
        try:
            access_token, expires_at, refresh_token = _login_service(  # type: ignore[misc]
                db=db,
                email=email,
                password=payload.password,
                user_agent=user_agent,
                ip_address=ip,
            )
            log.info(
                "login_success email=%s user_id=%s", email, getattr(user, "id", None)
            )
            record_login_attempt(ip, email, success=True)
            _set_refresh_cookie(response, refresh_token, expires_at=expires_at)
            return TokensOut(access_token=access_token, refresh_token=refresh_token)
        except ValueError:
            record_login_attempt(ip, email, success=False)
            raise INVALID_CREDENTIALS
        except HTTPException:
            raise
        except Exception as e:
            log.exception("login_service_error email=%s: %s", email, e)
            raise HTTPException(status_code=500, detail="Authentication failed") from e

    # Fallback: manual verification when service login is unavailable
    if not user:
        await asyncio.sleep(0)
        try:
            verify_password(
                payload.password, "$2b$12$invalidinvalidinvalidinvalidinvalidinvalidinvalidinvalid"
            )
        except Exception:
            pass
        record_login_attempt(ip, email, success=False)
        raise INVALID_CREDENTIALS

    ok = False
    stored_hash = getattr(user, "password_hash", getattr(user, "hashed_password", ""))
    try:
        ok = verify_password(payload.password, stored_hash)
    except Exception as e:
        log.warning("login_verify_error email=%s err=%s", email, e)

    log.info(
        "login_status email=%s ok=%s is_active=%s email_verified=%s role=%s",
        email,
        ok,
        getattr(user, "is_active", None),
        getattr(user, "email_verified", None),
        getattr(user, "role", None),
    )

    if not ok or not getattr(user, "is_active", True):
        record_login_attempt(ip, email, success=False)
        raise INVALID_CREDENTIALS

    try:
        access, refresh = create_access_refresh_tokens(
            user_id=user.id, email=user.email, role=user.role
        )
        log.info("login_success email=%s user_id=%s", email, user.id)
        record_login_attempt(ip, email, success=True)
        fallback_expiry = datetime.now(timezone.utc) + timedelta(days=7)
        _set_refresh_cookie(response, refresh, expires_at=fallback_expiry)
        return TokensOut(access_token=access, refresh_token=refresh)
    except Exception as e:
        log.exception("login_token_error email=%s: %s", email, e)
        raise HTTPException(status_code=500, detail="Authentication failed") from e


# -----------
# Refresh JWT
# -----------


@router.post("/refresh", response_model=RefreshOut, status_code=200)
async def refresh(
    request: Request,
    response: Response,
    payload: Optional[RefreshIn] = Body(default=None),
    db: Session = Depends(get_db),
) -> RefreshOut:
    token = _resolve_refresh_token(payload, request)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    try:
        result = _refresh_access_token_adapter(db, token)
    except ValueError as ve:
        log.info("refresh_invalid_token: %s", ve)
        raise HTTPException(status_code=400, detail="Invalid refresh token") from ve
    except Exception as e:
        log.exception("refresh_error: %s", e)
        raise HTTPException(status_code=401, detail="Invalid refresh token") from e

    access_token = result.get("access_token") if isinstance(result, dict) else None
    refresh_token = result.get("refresh_token") if isinstance(result, dict) else None
    expires_at = result.get("expires_at") if isinstance(result, dict) else None

    if not access_token or not refresh_token:
        raise HTTPException(status_code=400, detail="Invalid refresh token")

    _set_refresh_cookie(response, refresh_token, expires_at=expires_at)
    return RefreshOut(access_token=access_token, refresh_token=refresh_token, expires_at=expires_at)


# ----
# /me
# ----


@router.get("/me", response_model=MeOut)
async def me(current_user=Depends(get_current_user)):
    return MeOut(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role=current_user.role,
        is_active=current_user.is_active,
        email_verified=bool(
            getattr(
                current_user,
                "email_verified",
                getattr(current_user, "is_email_verified", True),
            )
        ),
    )


@router.post("/logout", status_code=204)
async def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    _: None = Depends(require_csrf_token),
):
    token = request.cookies.get(REFRESH_COOKIE_NAME)
    if token and _revoke_refresh_service:
        try:
            _revoke_refresh_service(db=db, refresh_token=token)
        except Exception as e:
            log.warning("logout_revoke_failed: %s", e)

    _clear_refresh_cookie(response)
    response.status_code = status.HTTP_204_NO_CONTENT
    return None
