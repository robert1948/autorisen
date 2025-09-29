"""Authentication API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from . import service
from .schemas import LoginRequest, RegisterRequest, TokenResponse, UserProfile

router = APIRouter(prefix="/auth", tags=["auth"])
auth_scheme = HTTPBearer(auto_error=False)


@router.post("/register", status_code=201)
def register(payload: RegisterRequest) -> dict[str, bool]:
    try:
        service.register(payload.email, payload.password, payload.full_name)
        return {"ok": True}
    except ValueError as exc:  # user exists
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest) -> TokenResponse:
    try:
        token, expires_at = service.login(payload.email, payload.password)
        return TokenResponse(access_token=token, expires_at=expires_at)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials") from exc


def _authenticate(creds: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> str:
    if not creds:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing auth")
    try:
        return service.current_user(creds.credentials)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token") from exc


@router.get("/me", response_model=UserProfile)
def me(email: str = Depends(_authenticate)) -> UserProfile:
    profile = service.profile(email)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    return profile
