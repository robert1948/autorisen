
"""Authentication API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.src.db.session import get_session
from . import audit, rate_limiter, service
from .schemas import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserProfile,
)

router = APIRouter(prefix="/auth", tags=["auth"])
auth_scheme = HTTPBearer(auto_error=False)


def _client_identifier(request: Request, email: str) -> str:
    ip = request.client.host if request.client else "unknown"
    return f"{email.lower()}:{ip}"


@router.post("/register", status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_session)) -> dict[str, bool]:
    try:
        service.register(db, payload.email, payload.password, payload.full_name)
        return {"ok": True}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/login", response_model=TokenResponse)
def login(request: Request, payload: LoginRequest, db: Session = Depends(get_session)) -> TokenResponse:
    identifier = _client_identifier(request, payload.email)
    if not rate_limiter.check(identifier):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="rate limit exceeded")

    ip = request.client.host if request.client else None
    agent = request.headers.get("user-agent")

    try:
        access_token, expires_at, refresh_token = service.login(
            db,
            payload.email,
            payload.password,
            user_agent=agent,
            ip_address=ip,
        )
        audit.log_login_attempt(db, email=payload.email, success=True, ip_address=ip, user_agent=agent)
        rate_limiter.reset(identifier)
        return TokenResponse(
            access_token=access_token,
            expires_at=expires_at,
            refresh_token=refresh_token,
        )
    except ValueError as exc:
        audit.log_login_attempt(db, email=payload.email, success=False, ip_address=ip, user_agent=agent, details=str(exc))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials") from exc


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_session)) -> TokenResponse:
    try:
        access_token, expires_at, refresh_token = service.refresh_access_token(db, payload.refresh_token)
        return TokenResponse(access_token=access_token, expires_at=expires_at, refresh_token=refresh_token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid refresh token") from exc


def _authenticate(
    creds: HTTPAuthorizationCredentials = Depends(auth_scheme),
    db: Session = Depends(get_session),
) -> str:
    if not creds:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing auth")
    try:
        return service.current_user(db, creds.credentials)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token") from exc


@router.get("/me", response_model=UserProfile)
def me(email: str = Depends(_authenticate), db: Session = Depends(get_session)) -> UserProfile:
    profile = service.profile(db, email)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    return UserProfile(email=profile.email, full_name=profile.full_name)
