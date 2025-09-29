"""Authentication API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.src.db.session import get_session
from . import service
from .schemas import LoginRequest, RegisterRequest, TokenResponse, UserProfile

router = APIRouter(prefix="/auth", tags=["auth"])
auth_scheme = HTTPBearer(auto_error=False)


@router.post("/register", status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_session)) -> dict[str, bool]:
    try:
        service.register(db, payload.email, payload.password, payload.full_name)
        return {"ok": True}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_session)) -> TokenResponse:
    try:
        token, expires_at = service.login(db, payload.email, payload.password)
        return TokenResponse(access_token=token, expires_at=expires_at)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials") from exc


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
