from __future__ import annotations

import secrets
from typing import Iterable, Literal, cast

from fastapi import APIRouter, HTTPException, Request, Response, status
from starlette.responses import JSONResponse

from backend.src.core.config import settings
from backend.src.services.csrf import generate_csrf_token, validate_csrf_token

CSRF_COOKIE = "csrftoken"
CSRF_HEADER_CANDIDATES: tuple[str, ...] = (
    "X-CSRF-Token",
    "X-CSRFToken",
    "X-XSRF-TOKEN",
)
CSRF_COOKIE_CANDIDATES: tuple[str, ...] = (
    "csrftoken",
    "csrf_token",
    "XSRF-TOKEN",
)
SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}

# CSRF is intended to protect browser/cookie flows. Some endpoints are designed for
# server-to-server POSTs and must not be blocked by CSRF.
# Keep exemptions as narrow as possible (method + path).
EXEMPT_ROUTES: set[tuple[str, str]] = {
    ("POST", "/api/payments/payfast/checkout"),
    ("POST", "/api/payments/payfast/itn"),
}

CSRF_COOKIE_NAME = CSRF_COOKIE
CSRF_HEADER_NAME = CSRF_HEADER_CANDIDATES[0]

csrf_router = APIRouter(tags=["csrf"])


def _resolve_first(values: Iterable[str | None]) -> str | None:
    for value in values:
        if value:
            return value
    return None


def _resolve_cookie_settings() -> tuple[bool, Literal["lax", "strict", "none"]]:
    desired = settings.session_cookie_samesite
    normalized = desired if desired in {"lax", "strict", "none"} else "lax"
    secure = settings.session_cookie_secure or normalized == "none"
    samesite_literal = cast(Literal["lax", "strict", "none"], normalized)
    return secure, samesite_literal


def issue_csrf_token(response: Response) -> str:
    token = generate_csrf_token()
    secure, samesite_value = _resolve_cookie_settings()
    response.set_cookie(
        CSRF_COOKIE,
        token,
        httponly=False,
        secure=secure,
        samesite=samesite_value,
        path="/",
    )
    response.headers[CSRF_HEADER_NAME] = token
    return token


def _extract_token_from_headers(request: Request) -> str | None:
    return _resolve_first(request.headers.get(name) for name in CSRF_HEADER_CANDIDATES)


def _extract_token_from_cookies(request: Request) -> str | None:
    return _resolve_first(request.cookies.get(name) for name in CSRF_COOKIE_CANDIDATES)


def require_csrf_token(request: Request) -> None:
    method = (request.method or "").upper()
    if method in SAFE_METHODS:
        return None

    if (method, request.url.path) in EXEMPT_ROUTES:
        return None

    header_token = _extract_token_from_headers(request)
    cookie_token = _extract_token_from_cookies(request)

    if not header_token or not cookie_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token missing or invalid",
        )

    if not secrets.compare_digest(header_token, cookie_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token mismatch",
        )

    if not validate_csrf_token(header_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token",
        )
    return None


from starlette.types import ASGIApp, Scope, Receive, Send


class CSRFMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)

        # Check if we should skip
        method = request.method
        if method in SAFE_METHODS:
            await self.app(scope, receive, send)
            return

        try:
            require_csrf_token(request)
        except HTTPException as exc:
            response = JSONResponse({"detail": exc.detail}, status_code=exc.status_code)
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)


@csrf_router.get("/csrf")
def get_csrf(response: Response) -> dict[str, str]:
    token = issue_csrf_token(response)
    return {"csrf": token, "csrf_token": token, "token": token}


__all__ = [
    "CSRF_COOKIE",
    "CSRF_COOKIE_NAME",
    "CSRF_COOKIE_CANDIDATES",
    "CSRF_HEADER_CANDIDATES",
    "CSRF_HEADER_NAME",
    "CSRFMiddleware",
    "csrf_router",
    "issue_csrf_token",
    "require_csrf_token",
]
