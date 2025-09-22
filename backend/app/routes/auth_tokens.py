# backend/app/routes/auth_tokens.py
from fastapi import APIRouter, HTTPException, Response, Request
import os
from pydantic import BaseModel, EmailStr

# Token helpers (Redis-backed refresh rotation)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    rotate_refresh,
    revoke_refresh_jti,
    decode,
)
from app.utils.rate_limiter import rate_limit, check_rate_limit

router = APIRouter(prefix="/api/auth", tags=["auth-tokens"])

# ---------------------------------------------------------------------------
# Dev-only user checker
# This stub exists only to make local development and tests convenient. The
# router containing this handler is only mounted when `ENVIRONMENT=development`
# (see `backend/app/main.py`). In production you should remove or replace
# this with a real DB-backed lookup.
def get_user_by_email_and_password(email: str, password: str):
    """
    VERY SIMPLE DEV STUB.
    Accepts any email/password and returns a stable pseudo user id.
    Swap this for a real DB query + password verification in production.
    """
    # return the email as the 'id' so tokens issued in dev include the email
    # as the `sub` claim; `get_current_user` supports email subs and will
    # resolve the real DB user by email. This avoids mismatches between a
    # pseudo numeric id and the real DB id in development tests.
    return {"id": email, "email": email}
# ---------------------------------------------------------------------------

# Cookie configuration for refresh token
ENV = os.getenv("ENVIRONMENT", "development")
COOKIE_NAME = "refresh_token"
COOKIE_PATH = "/api/auth"
COOKIE_HTTPONLY = True
# In production (non-development) we require secure cookies and use samesite=None
# to allow cross-site contexts (remember this requires HTTPS).
if ENV == "development":
    COOKIE_SAMESITE = "lax"
    COOKIE_SECURE = False
else:
    COOKIE_SAMESITE = "none"
    COOKIE_SECURE = True

# Request models
class LoginIn(BaseModel):
    email: EmailStr
    password: str


@router.post("/login", summary="Login (sets refresh cookie; returns access token)")
def login(payload: LoginIn, response: Response):
    # Rate-limit by email
    try:
        check_rate_limit('login', payload.email, limit=10, period=60)
    except Exception:
        raise

    user = get_user_by_email_and_password(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access = create_access_token(user["id"])
    refresh, _jti, _exp = create_refresh_token(user["id"])

    # Set refresh token cookie (httpOnly so JS cannot read it)
    response.set_cookie(
        key=COOKIE_NAME,
        value=refresh,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path=COOKIE_PATH,
        max_age=60 * 60 * 24 * 7,  # 7 days (keep in sync with REFRESH_TOKEN_EXPIRES_DAYS)
    )
    return {"access_token": access, "token_type": "bearer"}


@router.post("/refresh", summary="Rotate refresh cookie; return a new access token")
def refresh(request: Request, response: Response):
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        user_id, new_refresh = rotate_refresh(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    # issue new access
    access = create_access_token(user_id)

    # rotate cookie
    response.set_cookie(
        key=COOKIE_NAME,
        value=new_refresh,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path=COOKIE_PATH,
        max_age=60 * 60 * 24 * 7,
    )
    return {"access_token": access, "token_type": "bearer"}


@router.post("/logout", summary="Revoke refresh token and clear cookie")
def logout(request: Request, response: Response):
    token = request.cookies.get(COOKIE_NAME)
    if token:
        try:
            jti = decode(token).get("jti")
            if jti:
                revoke_refresh_jti(jti)
        except Exception:
            # ignore malformed token during logout
            pass

    response.delete_cookie(key=COOKIE_NAME, path=COOKIE_PATH)
    return {"ok": True}
