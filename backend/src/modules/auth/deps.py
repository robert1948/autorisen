"""Reusable authentication dependencies for FastAPI routes."""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.src.db import models
from backend.src.db.session import get_session

from . import service

auth_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(auth_scheme),
    db: Session = Depends(get_session),
) -> models.User:
    """Resolve the currently authenticated user from the bearer token."""
    if not creds:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing auth")

    try:
        email = service.current_user(db, creds.credentials)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token") from exc

    profile = service.profile(db, email)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    return profile
