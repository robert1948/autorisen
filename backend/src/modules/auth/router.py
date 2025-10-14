# /home/robert/Development/autolocal/backend/src/modules/auth/router.py
"""Authentication API endpoints including registration and analytics."""

from typing import Annotated, Any, Dict, Optional

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)  # <-- import Body
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.src.core.config import settings
from backend.src.modules.auth.rate_limiter import auth_rate_limit, limiter
from backend.src.db import models
from backend.src.db.session import get_session
from backend.src.modules.auth import audit, rate_limiter, service
from backend.src.modules.auth.schemas import (
    LoginRequest,
    RefreshRequest,
    RegisterStep1In,
    RegisterStep1Out,
    RegisterStep2In,
    RegisterStep2Out,
    TokenResponse,
    UserOut,
    UserRole,
)
from backend.src.services import emailer, recaptcha

router = APIRouter(prefix="/auth", tags=["auth"])
auth_scheme = HTTPBearer(auto_error=False)
REFRESH_COOKIE_NAME = "refresh_token"
REFRESH_COOKIE_PATH = "/api/auth"
REFRESH_COOKIE_MAX_AGE = service.REFRESH_TOKEN_DAYS * 24 * 60 * 60
REFRESH_COOKIE_SECURE = settings.env in {"staging", "prod"}


def _serialize_user(user: models.User) -> UserOut:
    role_value = user.role or UserRole.CUSTOMER.value
    try:
        role = UserRole(role_value).value
    except ValueError:
        role = UserRole.CUSTOMER.value

    profile_data: Dict[str, Any] = {}
    if getattr(user, "profile", None) and getattr(user.profile, "profile", None):
        if isinstance(user.profile.profile, dict):
            profile_data = dict(user.profile.profile)

    return UserOut(
        id=user.id,
        email=user.email,
        first_name=user.first_name or "",
        last_name=user.last_name or "",
        role=role,
        company_name=user.company_name or "",
        is_active=bool(user.is_active),
        is_email_verified=bool(user.is_email_verified),
        profile=profile_data,
        created_at=user.created_at,
    )


def _authenticate_user(
    db: Session,
    creds: HTTPAuthorizationCredentials | None,
) -> models.User:
    if not creds:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing auth")
    try:
        return service.current_user(db, creds.credentials)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
        ) from exc


async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(auth_scheme),
    db: Session = Depends(get_session),
) -> models.User:
    return _authenticate_user(db, creds)


@router.post("/register/step1", response_model=RegisterStep1Out, status_code=201)
@limiter.limit(auth_rate_limit)
async def register_step1(
    request: Request,
    payload: Annotated[RegisterStep1In, Body(...)],
    db: Session = Depends(get_session),
) -> RegisterStep1Out:
    ip = request.client.host if request.client else None
    recaptcha_ok = await recaptcha.verify(payload.recaptcha_token, ip)
    if not recaptcha_ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="reCAPTCHA verification failed."
        )

    try:
        temp_token = service.begin_registration(
            db,
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email,
            password=payload.password,
            role=payload.role,
        )
        return RegisterStep1Out(temp_token=temp_token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/register/step2", response_model=RegisterStep2Out)
@limiter.limit(auth_rate_limit)
async def register_step2(
    request: Request,
    payload: Annotated[RegisterStep2In, Body(...)],
    db: Session = Depends(get_session),
    creds: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> RegisterStep2Out:
    if not creds:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing auth")

    try:
        access_token, refresh_token, expires_at, user = service.complete_registration(
            db,
            temp_token=creds.credentials,
            company_name=payload.company_name,
            profile=payload.profile,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    await emailer.send_welcome_email(user.email, user.role, {"first_name": user.first_name})
    user_out = _serialize_user(user)
    return RegisterStep2Out(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=expires_at,
        user=user_out,
    )


@router.post("/resend-welcome", status_code=202)
@limiter.limit(auth_rate_limit)
async def resend_welcome(
    request: Request,
    user: models.User = Depends(get_current_user),
) -> Dict[str, bool]:
    await emailer.send_welcome_email(user.email, user.role, {"first_name": user.first_name})
    return {"ok": True}


@router.post("/analytics/track", status_code=202)
@limiter.limit(auth_rate_limit)
async def track_event(
    request: Request,
    payload: Dict[str, Any] = Body(...),  # keep Body here to declare JSON dict explicitly
    db: Session = Depends(get_session),
) -> Dict[str, bool]:
    event_type = str(payload.get("event_type", "")).strip()
    if not event_type:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="event_type is required"
        )

    step = payload.get("step")
    role_value = payload.get("role")
    details = payload.get("details")

    normalized_step = step.strip() if isinstance(step, str) and step.strip() else None
    normalized_role = None
    if isinstance(role_value, str) and role_value.strip():
        normalized_role = role_value.strip()
    elif isinstance(role_value, UserRole):
        normalized_role = role_value.value

    details_payload: Dict[str, Any] = details if isinstance(details, dict) else {}

    service.record_analytics_event(
        db,
        event_type=event_type,
        step=normalized_step,
        role=normalized_role,
        details=details_payload,
    )
    return Response(status_code=status.HTTP_202_ACCEPTED)


@router.post("/login", response_model=TokenResponse)
@limiter.limit(auth_rate_limit)
def login(
    request: Request,
    payload: Annotated[LoginRequest, Body(...)],
    response: Response,
    db: Session = Depends(get_session),
) -> TokenResponse:
    ip = request.client.host if request.client else None
    allowed, _reason = rate_limiter.allow_login(ip, payload.email)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="rate limit exceeded"
        )

    agent = request.headers.get("user-agent")

    try:
        access_token, expires_at, refresh_token = service.login(
            db,
            payload.email,
            payload.password,
            user_agent=agent,
            ip_address=ip,
        )
        audit.log_login_attempt(
            db, email=payload.email, success=True, ip_address=ip, user_agent=agent
        )
        rate_limiter.reset_login(ip, payload.email)
        response.set_cookie(
            REFRESH_COOKIE_NAME,
            refresh_token,
            max_age=REFRESH_COOKIE_MAX_AGE,
            httponly=True,
            secure=REFRESH_COOKIE_SECURE,
            samesite="lax",
            path=REFRESH_COOKIE_PATH,
        )
        return TokenResponse(
            access_token=access_token,
            expires_at=expires_at,
            refresh_token=refresh_token,
        )
    except ValueError as exc:
        audit.log_login_attempt(
            db,
            email=payload.email,
            success=False,
            ip_address=ip,
            user_agent=agent,
            details=str(exc),
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials"
        ) from exc


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit(auth_rate_limit)
def refresh(
    request: Request,
    response: Response,
    payload: Optional[RefreshRequest] = Body(None),
    db: Session = Depends(get_session),
) -> TokenResponse:
    refresh_token = payload.refresh_token if payload else None
    if not refresh_token:
        refresh_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid refresh token"
        )
    try:
        access_token, expires_at, refresh_token = service.refresh_access_token(
            db, refresh_token
        )
        response.set_cookie(
            REFRESH_COOKIE_NAME,
            refresh_token,
            max_age=REFRESH_COOKIE_MAX_AGE,
            httponly=True,
            secure=REFRESH_COOKIE_SECURE,
            samesite="lax",
            path=REFRESH_COOKIE_PATH,
        )
        return TokenResponse(
            access_token=access_token, expires_at=expires_at, refresh_token=refresh_token
        )
    except ValueError as exc:
        response.delete_cookie(REFRESH_COOKIE_NAME, path=REFRESH_COOKIE_PATH)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid refresh token"
        ) from exc


@router.get("/me", response_model=UserOut)
def me(
    user: models.User = Depends(get_current_user),
) -> UserOut:
    return _serialize_user(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_session),
) -> None:
    refresh_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if refresh_token:
        service.revoke_refresh_token(db, refresh_token)
    response.delete_cookie(REFRESH_COOKIE_NAME, path=REFRESH_COOKIE_PATH)
    response.status_code = status.HTTP_204_NO_CONTENT
