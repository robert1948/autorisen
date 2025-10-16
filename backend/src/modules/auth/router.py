# backend/src/modules/auth/router.py
from __future__ import annotations

import asyncio
import logging
from typing import Optional, Callable, Any

from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel, EmailStr, Field, constr
from sqlalchemy.orm import Session

from backend.src.db.session import get_db
from backend.src.core.config import settings
from .security import verify_password, create_access_refresh_tokens
from .deps import get_current_user

log = logging.getLogger("auth")
router = APIRouter(prefix="/api/auth", tags=["auth"])

# ---------------------------
# Schemas
# ---------------------------


class LoginIn(BaseModel):
    email: EmailStr
    password: constr(min_length=8, max_length=256)


class TokensOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RegisterStep1In(BaseModel):
    email: EmailStr
    first_name: constr(strip_whitespace=True, max_length=50)
    last_name: constr(strip_whitespace=True, max_length=50)
    password: constr(min_length=8, max_length=256)
    confirm_password: constr(min_length=8, max_length=256)
    role: constr(strip_whitespace=True, min_length=3, max_length=40)
    recaptcha_token: Optional[str] = None


class RegisterStep1Out(BaseModel):
    temp_token: str


class Company(BaseModel):
    company_name: constr(strip_whitespace=True, max_length=100) = Field(..., title="Company Name")


class Profile(BaseModel):
    class Config:
        extra = "allow"


class RegisterStep2In(BaseModel):
    temp_token: str
    company: Company
    profile: Profile


class OkOut(BaseModel):
    ok: bool = True


class MeOut(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    role: str
    is_active: bool
    email_verified: bool


# ---------------------------
# Helpers
# ---------------------------

INVALID_CREDENTIALS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid credentials",
)


def _normalize_email(e: str) -> str:
    return e.strip().lower()


def _normalize_role(r: str) -> str:
    return r.strip().lower()


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
    result = _begin_reg(  # type: ignore[misc]
        db=db,
        email=email,
        first_name=first_name,
        last_name=last_name,
        password_plain=password_plain,
        role=role,
    )
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
    return _complete_reg(db=db, temp_token=temp_token, company=company, profile=profile)  # type: ignore[misc]


# -------------
# Health (quick)
# -------------


@router.get("/health", include_in_schema=False)
async def auth_health():
    return {"ok": True}


# ---------------------------
# Registration — Step 1 (init)
# ---------------------------


@router.post("/register/step1", response_model=RegisterStep1Out, status_code=200)
async def register_step1(payload: RegisterStep1In, db: Session = Depends(get_db)):
    email = _normalize_email(payload.email)
    role = _normalize_role(payload.role)

    # Optional: reCAPTCHA enforcement unless disabled
    if not settings.DISABLE_RECAPTCHA:
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
    except HTTPException:
        raise
    except Exception as e:
        log.exception("register_step1_error email=%s: %s", email, e)
        raise HTTPException(status_code=500, detail="Registration failed") from e


# -----------------------------
# Registration — Step 2 (commit)
# -----------------------------


@router.post("/register/step2", response_model=OkOut, status_code=200)
async def register_step2(payload: RegisterStep2In, db: Session = Depends(get_db)) -> OkOut:
    try:
        user = _complete_registration_adapter(
            db=db,
            temp_token=payload.temp_token,
            company=payload.company.dict(),
            profile=payload.profile.dict(),
        )
        try:
            log.info(
                "register_step2_ok email=%s user_id=%s",
                getattr(user, "email", None),
                getattr(user, "id", None),
            )
        except Exception:
            log.info("register_step2_ok (no user object returned)")
        return OkOut()
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
    db: Session = Depends(get_db),
    user_agent: Optional[str] = Header(default=None),
):
    email = _normalize_email(payload.email)

    user = _get_user_by_email(db, email)
    user_found = bool(user)
    log.info("login_attempt email=%s found=%s ua=%s", email, user_found, user_agent)

    # If user not found, do a fake verify to keep timing similar
    if not user:
        await asyncio.sleep(0)
        try:
            verify_password(
                payload.password, "$2b$12$invalidinvalidinvalidinvalidinvalidinvalidinvalidinvalid"
            )
        except Exception:
            pass
        raise INVALID_CREDENTIALS

    # Password check
    ok = False
    try:
        ok = verify_password(payload.password, user.password_hash)
    except Exception as e:
        # Bad hash format or drift → treat as invalid
        log.warning("login_verify_error email=%s err=%s", email, e)

    log.info(
        "login_status email=%s ok=%s is_active=%s email_verified=%s role=%s",
        email,
        ok,
        getattr(user, "is_active", None),
        getattr(user, "email_verified", None),
        getattr(user, "role", None),
    )

    # Gate checks: unify as 401 to avoid account probing
    if not ok or not getattr(user, "is_active", True) or not getattr(user, "email_verified", True):
        raise INVALID_CREDENTIALS

    try:
        access, refresh = create_access_refresh_tokens(
            user_id=user.id, email=user.email, role=user.role
        )
        log.info("login_success email=%s user_id=%s", email, user.id)
        return TokensOut(access_token=access, refresh_token=refresh)
    except Exception as e:
        log.exception("login_token_error email=%s: %s", email, e)
        raise HTTPException(status_code=500, detail="Authentication failed") from e


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
        email_verified=current_user.email_verified,
    )
