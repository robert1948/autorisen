"""CSRF utilities for the auth API."""

from __future__ import annotations

from typing import Optional

from fastapi import Cookie, Header, HTTPException, Response, status

from backend.src.core.config import settings
from backend.src.services.csrf import generate_csrf_token, validate_csrf_token

CSRF_COOKIE_NAME = "autorisen_csrf"
CSRF_HEADER_NAME = "X-CSRF-Token"
CSRF_TOKEN_MAX_AGE = 60 * 60  # 1 hour


def issue_csrf_token(response: Response) -> str:
    """Generate a CSRF token and attach it as a cookie."""

    token = generate_csrf_token()
    response.set_cookie(
        CSRF_COOKIE_NAME,
        token,
        max_age=CSRF_TOKEN_MAX_AGE,
        secure=settings.env in {"staging", "prod"},
        httponly=False,  # allow SPA to read and mirror into header
        samesite="strict",
        path="/",
    )
    return token


def require_csrf_token(
    csrf_header: Optional[str] = Header(default=None, alias=CSRF_HEADER_NAME),
    csrf_cookie: Optional[str] = Cookie(default=None, alias=CSRF_COOKIE_NAME),
) -> None:
    """Validate CSRF header + cookie. Raises HTTP 403 on failure."""

    if not csrf_header or not csrf_cookie:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Missing CSRF token"
        )
    if csrf_header != csrf_cookie:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="CSRF token mismatch"
        )
    if not validate_csrf_token(csrf_header):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid CSRF token"
        )
