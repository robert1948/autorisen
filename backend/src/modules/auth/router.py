"""Authentication API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header

from . import schemas, service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.TokenResponse, status_code=201)
def register(payload: schemas.RegisterRequest) -> schemas.TokenResponse:
    user = service.create_user(payload)
    return service.create_access_token(user)


@router.post("/login", response_model=schemas.TokenResponse)
def login(payload: schemas.LoginRequest) -> schemas.TokenResponse:
    user = service.authenticate(payload)
    return service.create_access_token(user)


def _current_user(authorization: str = Header(default=None)) -> schemas.UserProfile:
    token = service.bearer_token_from_header(authorization)
    return service.decode_token(token)


@router.get("/me", response_model=schemas.UserProfile)
def read_profile(current_user: schemas.UserProfile = Depends(_current_user)) -> schemas.UserProfile:
    return current_user
