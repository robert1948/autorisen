# backend/src/modules/auth/router.py
from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import inspect
import json
import logging
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, Callable, Dict, Optional, Tuple
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse

import httpx
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    Header,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)
from sqlalchemy.orm import Session

from backend.src.core.config import settings
from backend.src.core.email_verify import (
    EmailTokenError,
    issue_email_token,
    parse_email_token,
)
from backend.src.core.redis import (
    cache_user_token_version,
    clear_user_token_version_cache,
    denylist_jti,
)
from backend.src.db import models
from backend.src.db.session import get_db
from backend.src.db.models import AnalyticsEvent
from backend.src.services import recaptcha as recaptcha_service
from backend.src.services.emailer import (
    send_password_reset_email,
    send_verification_email,
)
from backend.src.services.security import decode_jwt

from .csrf import csrf_router, issue_csrf_token, require_csrf_token
from .schemas import LoginRequest, LoginResponse, MeResponse, AnalyticsEventIn
from .deps import (
    _bearer_from_header,
    _load_user_from_claims,
    _token_from_request,
    get_current_user,
    get_current_user_with_claims,
)
from .audit import log_login_attempt
from .rate_limiter import allow_login, record_login_attempt
from .security import create_access_refresh_tokens, verify_password

log = logging.getLogger("auth")

router = APIRouter(
    tags=["auth"],
    dependencies=[Depends(require_csrf_token)],  # CSRF check runs before validation
)
router.include_router(csrf_router)
try:
    from .schemas import UserRole as ServiceUserRole  # type: ignore
except ImportError:
    ServiceUserRole = None

_GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
_GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"
_GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
_GOOGLE_USERINFO_ENDPOINT = "https://openidconnect.googleapis.com/v1/userinfo"
_LINKEDIN_AUTH_ENDPOINT = "https://www.linkedin.com/oauth/v2/authorization"
_LINKEDIN_TOKEN_ENDPOINT = "https://www.linkedin.com/oauth/v2/accessToken"
_LINKEDIN_USERINFO_ENDPOINT = "https://api.linkedin.com/v2/userinfo"

# ---------------------------
# Schemas
# ---------------------------


PasswordStr = Annotated[str, StringConstraints(min_length=1, max_length=256)]
StrongPasswordStr = Annotated[str, StringConstraints(min_length=12, max_length=256)]
ResetTokenStr = Annotated[str, StringConstraints(min_length=10, max_length=255)]
FirstNameStr = Annotated[str, StringConstraints(strip_whitespace=True, max_length=50)]
LastNameStr = Annotated[str, StringConstraints(strip_whitespace=True, max_length=50)]
RoleStr = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=3, max_length=40)
]
CompanyNameStr = Annotated[
    str, StringConstraints(strip_whitespace=True, max_length=100)
]
IdTokenStr = Annotated[str, StringConstraints(min_length=10, max_length=4096)]


# LoginIn replaced by LoginRequest from schemas
# TokensOut replaced by LoginResponse from schemas


class SocialTokensOut(LoginResponse):
    email: EmailStr


class CsrfTokenOut(BaseModel):
    csrf_token: str


class ForgotPasswordIn(BaseModel):
    email: EmailStr


class ForgotPasswordOut(BaseModel):
    message: str = (
        "If an account exists for that email, you'll receive reset instructions shortly."
    )


class VerificationResendIn(BaseModel):
    email: EmailStr


class ResetPasswordIn(BaseModel):
    token: ResetTokenStr
    password: PasswordStr
    confirm_password: PasswordStr

    @field_validator("password", "confirm_password")
    @classmethod
    def _password_policy(cls, value: str) -> str:
        if len(value or "") < 12:
            raise ValueError("Password must be at least 12 characters long")
        return value

    @model_validator(mode="after")
    def _passwords_match(self) -> "ResetPasswordIn":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class ResetPasswordOut(BaseModel):
    message: str = "Your password has been updated."


class RegisterStep1In(BaseModel):
    email: EmailStr
    first_name: FirstNameStr
    last_name: LastNameStr
    password: PasswordStr
    confirm_password: PasswordStr
    role: RoleStr
    recaptcha_token: Optional[str] = None

    @field_validator("password", "confirm_password")
    @classmethod
    def _password_policy(cls, value: str) -> str:
        if len(value or "") < 12:
            raise ValueError("Password must be at least 12 characters long")
        return value


class RegisterStep1Out(BaseModel):
    temp_token: str


class Profile(BaseModel):
    model_config = ConfigDict(extra="allow")


class RegisterStep2In(BaseModel):
    company_name: CompanyNameStr
    profile: Profile


class RegisterStep2Out(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[str] = None
    user: dict


class RegisterIn(BaseModel):
    first_name: FirstNameStr
    last_name: LastNameStr
    email: EmailStr
    password: StrongPasswordStr
    confirm_password: StrongPasswordStr
    role: RoleStr = "Customer"
    company_name: CompanyNameStr = ""
    profile: Profile = Field(default_factory=Profile)
    recaptcha_token: Optional[str] = None

    @model_validator(mode="after")
    def _passwords_match(self) -> "RegisterIn":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


# MeOut replaced by MeResponse from schemas


class RefreshIn(BaseModel):
    refresh_token: str


class RefreshOut(BaseModel):
    access_token: str
    refresh_token: str
    expires_at: Optional[str] = None


class GoogleLoginIn(BaseModel):
    id_token: Optional[IdTokenStr] = None
    code: Optional[str] = None
    redirect_uri: Optional[str] = None
    recaptcha_token: Optional[str] = None

    @model_validator(mode="after")
    def _require_code_or_token(self) -> "GoogleLoginIn":
        if not self.id_token and not self.code:
            raise ValueError("Provide either id_token or code.")
        if self.code and not self.redirect_uri:
            raise ValueError(
                "redirect_uri is required when exchanging an authorization code."
            )
        return self


class LinkedInLoginIn(BaseModel):
    access_token: Optional[str] = None
    code: Optional[str] = None
    redirect_uri: Optional[str] = None
    recaptcha_token: Optional[str] = None

    @model_validator(mode="after")
    def _require_code_or_token(self) -> "LinkedInLoginIn":
        if not self.access_token and not self.code:
            raise ValueError("Provide either access_token or code.")
        if self.code and not self.redirect_uri:
            raise ValueError(
                "redirect_uri is required when exchanging an authorization code."
            )
        return self


class LogoutIn(BaseModel):
    all_devices: bool = Field(default=False, alias="all_devices")


class LogoutOut(BaseModel):
    message: str = "Logged out"


# ---------------------------
# Helpers
# ---------------------------

INVALID_CREDENTIALS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid credentials",
)

REFRESH_COOKIE_NAME = "refresh_token"


def _coerce_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str):
        try:
            # Accept ISO strings with/without timezone
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    return None


def _set_refresh_cookie(
    response: Response, token: str, *, expires_at: Any = None
) -> None:
    expires = _coerce_datetime(expires_at)
    max_age = None
    if expires:
        remaining = int((expires - datetime.now(timezone.utc)).total_seconds())
        max_age = remaining if remaining > 0 else 0

    same_site = settings.session_cookie_samesite
    cookie_secure = settings.session_cookie_secure or same_site == "none"
    samesite_value = "none" if same_site == "none" else same_site

    response.set_cookie(
        REFRESH_COOKIE_NAME,
        token,
        httponly=True,
        secure=cookie_secure,
        samesite=samesite_value,
        path="/api/auth",
        max_age=max_age,
        expires=expires,
    )


def _clear_refresh_cookie(response: Response) -> None:
    same_site = settings.session_cookie_samesite
    cookie_secure = settings.session_cookie_secure or same_site == "none"
    samesite_value = "none" if same_site == "none" else same_site
    response.delete_cookie(
        REFRESH_COOKIE_NAME,
        path="/api/auth",
        samesite=samesite_value,
        secure=cookie_secure,
    )


def _resolve_refresh_token(
    payload: Optional[RefreshIn], request: Request
) -> Optional[str]:
    if payload and payload.refresh_token:
        return payload.refresh_token
    return request.cookies.get(REFRESH_COOKIE_NAME)


def _normalize_email(e: str) -> str:
    return e.strip().lower()


def _normalize_role(r: str) -> str:
    return r.strip().lower()


async def _verify_recaptcha_token(
    token: Optional[str],
    request: Request,
    *,
    required: bool = True,
) -> None:
    if getattr(settings, "disable_recaptcha", False):
        return
    if not token:
        if required:
            raise HTTPException(status_code=400, detail="Missing reCAPTCHA token")
        return

    remote_ip = (
        getattr(request.client, "host", None) if request and request.client else None
    )
    try:
        ok = await recaptcha_service.verify(token, remote_ip)
    except Exception as exc:  # pragma: no cover
        log.warning("recaptcha_verify_failed err=%s", exc)
        ok = False
    if not ok:
        raise HTTPException(status_code=400, detail="reCAPTCHA verification failed")


_OAUTH_COOKIE_PATH = "/api/auth/oauth"
_OAUTH_STATE_MAX_AGE = 600  # seconds


def _state_cookie_name(provider: str) -> str:
    return f"oauth_state_{provider}"


def _default_callback_target() -> str:
    origin = str(settings.frontend_origin).rstrip("/")
    return f"{origin}/auth/callback"


def _urlsafe_b64decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _sign_oauth_state(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    secret = str(settings.secret_key).encode("utf-8")
    signature = hmac.new(secret, raw, hashlib.sha256).digest()
    token = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
    sig = base64.urlsafe_b64encode(signature).decode("ascii").rstrip("=")
    return f"{token}.{sig}"


def _decode_oauth_state_token(token: str) -> Dict[str, Any]:
    try:
        payload_b64, sig_b64 = token.split(".", 1)
    except ValueError as exc:
        raise ValueError("invalid token format") from exc

    payload = _urlsafe_b64decode(payload_b64)
    provided_signature = _urlsafe_b64decode(sig_b64)
    secret = str(settings.secret_key).encode("utf-8")
    expected_signature = hmac.new(secret, payload, hashlib.sha256).digest()

    if not hmac.compare_digest(provided_signature, expected_signature):
        raise ValueError("signature mismatch")

    data = json.loads(payload.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("invalid payload")
    return data


def _issue_oauth_state(
    provider: str, *, return_to: str, next_path: Optional[str]
) -> Tuple[str, str]:
    state_value = f"{provider}:{secrets.token_urlsafe(24)}"
    payload = {
        "provider": provider,
        "state": state_value,
        "return_to": return_to,
        "next_path": next_path,
        "issued": int(time.time()),
    }
    return state_value, _sign_oauth_state(payload)


def _append_query_params(url: str, params: Dict[str, Optional[str]]) -> str:
    parsed = urlparse(url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    for key, value in params.items():
        if value is None:
            continue
        query[key] = value
    new_query = urlencode(query, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


def _normalize_return_to(value: Optional[str]) -> str:
    default_target = _default_callback_target()
    if not value:
        return default_target

    candidate = value.strip()
    if not candidate:
        return default_target

    default_parts = urlparse(default_target)
    candidate_parts = urlparse(candidate)

    if candidate_parts.scheme and candidate_parts.scheme not in {"http", "https"}:
        return default_target

    if candidate_parts.netloc and candidate_parts.netloc != default_parts.netloc:
        return default_target

    if not candidate_parts.netloc:
        base = f"{default_parts.scheme}://{default_parts.netloc}"
        joined = urljoin(base + "/", candidate_parts.path or "")
        joined_parts = urlparse(joined)
        merged = joined_parts._replace(
            query=candidate_parts.query,
            fragment=candidate_parts.fragment,
        )
        return urlunparse(merged)

    return candidate


def _normalize_next_path(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    candidate = value.strip()
    if not candidate:
        return None
    if candidate.startswith("/"):
        return candidate
    parsed = urlparse(candidate)
    if not parsed.scheme and not parsed.netloc and parsed.path:
        return "/" + parsed.path.lstrip("/")
    return None


def _consume_oauth_state(
    provider: str, request: Request, received_state: str
) -> Dict[str, Any]:
    cookie_value = request.cookies.get(_state_cookie_name(provider))
    if not cookie_value:
        raise HTTPException(
            status_code=400,
            detail="OAuth session expired. Please restart the sign-in process.",
        )

    try:
        payload = _decode_oauth_state_token(cookie_value)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="OAuth session verification failed. Please try again.",
        ) from exc

    if payload.get("provider") != provider:
        raise HTTPException(status_code=400, detail="OAuth provider mismatch.")

    if payload.get("state") != received_state:
        raise HTTPException(status_code=400, detail="OAuth state mismatch.")

    issued = payload.get("issued")
    if not isinstance(issued, (int, float)):
        raise HTTPException(status_code=400, detail="OAuth session is invalid.")

    if time.time() - float(issued) > _OAUTH_STATE_MAX_AGE:
        raise HTTPException(status_code=400, detail="OAuth session has expired.")

    return payload


def _oauth_start(
    provider: str,
    *,
    request: Request,
    client_id: Optional[str],
    callback_override: Optional[str],
    auth_endpoint: str,
    scope: str,
    extra_params: Optional[Dict[str, str]] = None,
    return_to: Optional[str] = None,
    next_path: Optional[str] = None,
    prefer_json: bool = False,
) -> Response:
    if not client_id:
        raise HTTPException(
            status_code=500, detail=f"{provider.title()} OAuth is not configured."
        )

    callback_url = callback_override or str(
        request.url_for(f"oauth_{provider}_callback")
    )
    final_destination = _normalize_return_to(return_to)
    next_clean = _normalize_next_path(next_path)
    state_value, cookie_token = _issue_oauth_state(
        provider, return_to=final_destination, next_path=next_clean
    )

    params: Dict[str, str] = {
        "client_id": client_id,
        "redirect_uri": callback_url,
        "response_type": "code",
        "scope": scope,
        "state": state_value,
    }
    if extra_params:
        params.update(extra_params)

    redirect_url = f"{auth_endpoint}?{urlencode(params)}"
    if prefer_json:
        response: Response = JSONResponse(
            {
                "provider": provider,
                "state": state_value,
                "authorization_url": redirect_url,
                "expires_in": _OAUTH_STATE_MAX_AGE,
            }
        )
    else:
        response = RedirectResponse(
            redirect_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT
        )
    same_site = settings.session_cookie_samesite
    cookie_secure = settings.session_cookie_secure or same_site == "none"
    samesite_value = "none" if same_site == "none" else same_site

    response.set_cookie(
        _state_cookie_name(provider),
        cookie_token,
        max_age=_OAUTH_STATE_MAX_AGE,
        httponly=True,
        secure=cookie_secure,
        samesite=samesite_value,
        path=_OAUTH_COOKIE_PATH,
    )
    return response


def _oauth_callback(
    provider: str,
    request: Request,
    *,
    code: Optional[str],
    state: Optional[str],
    error: Optional[str],
    error_description: Optional[str],
) -> RedirectResponse:
    if not state:
        raise HTTPException(status_code=400, detail="Missing OAuth state parameter.")

    payload = _consume_oauth_state(provider, request, state)
    return_to = payload.get("return_to") or _default_callback_target()
    next_path = payload.get("next_path")

    params: Dict[str, Optional[str]] = {"state": state}
    if error:
        params["error"] = error
        if error_description:
            params["error_description"] = error_description
        if isinstance(next_path, str) and next_path:
            params["next"] = next_path
    else:
        if not code:
            raise HTTPException(
                status_code=400, detail="Missing authorization code from provider."
            )
        params["code"] = code
        if isinstance(next_path, str) and next_path:
            params["next"] = next_path

    redirect_target = _append_query_params(return_to, params)
    response = RedirectResponse(redirect_target, status_code=status.HTTP_302_FOUND)
    same_site = settings.session_cookie_samesite
    cookie_secure = settings.session_cookie_secure or same_site == "none"
    samesite_value = "none" if same_site == "none" else same_site
    response.delete_cookie(
        _state_cookie_name(provider),
        path=_OAUTH_COOKIE_PATH,
        samesite=samesite_value,
        secure=cookie_secure,
    )
    return response


async def _google_exchange_code(_code: str, _redirect_uri: str) -> Dict[str, Any]:
    """Exchange OAuth code for tokens (currently disabled)."""
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(status_code=500, detail="Google OAuth is not configured.")

    # Google OAuth integration is currently disabled
    # This is a placeholder for future implementation
    raise HTTPException(
        status_code=501, detail="Google OAuth integration is not yet implemented."
    )


async def _google_fetch_profile(
    *,
    id_token: Optional[str],
    access_token: Optional[str],
) -> Dict[str, Any]:
    if id_token:
        params = {"id_token": id_token}
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(_GOOGLE_TOKENINFO_URL, params=params)
        except httpx.HTTPError as exc:  # pragma: no cover
            log.warning("google_tokeninfo_http_error err=%s", exc)
            raise HTTPException(
                status_code=400, detail="Unable to verify Google token."
            ) from exc
    elif access_token:
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(_GOOGLE_USERINFO_ENDPOINT, headers=headers)
        except httpx.HTTPError as exc:  # pragma: no cover
            log.warning("google_userinfo_http_error err=%s", exc)
            raise HTTPException(
                status_code=400, detail="Unable to fetch Google profile."
            ) from exc
    else:
        raise HTTPException(status_code=400, detail="Google token missing.")

    if response.status_code != 200:
        log.warning(
            "google_profile_failed status=%s body=%s",
            response.status_code,
            response.text[:256],
        )
        raise HTTPException(status_code=400, detail="Unable to fetch Google profile.")

    data = response.json()

    client_id = settings.google_client_id
    audience = data.get("aud") or data.get("audience")
    if client_id and audience and audience != client_id:
        log.warning(
            "google_token_invalid_audience audience=%s expected=%s", audience, client_id
        )
        raise HTTPException(
            status_code=400, detail="Google token is not intended for this application."
        )

    email = data.get("email")
    if not email:
        raise HTTPException(
            status_code=400, detail="Google account did not provide an email."
        )

    verified = str(data.get("email_verified", data.get("verified_email", ""))).lower()
    if verified not in {"true", "1", "yes"}:
        raise HTTPException(
            status_code=400, detail="Google account email is not verified."
        )

    return {
        "email": email,
        "first_name": data.get("given_name") or "",
        "last_name": data.get("family_name") or "",
        "provider_uid": data.get("sub") or data.get("id") or email,
    }


async def _linkedin_exchange_code(_code: str, _redirect_uri: str) -> str:
    """Exchange OAuth code for access token (currently disabled)."""
    if not settings.linkedin_client_id or not settings.linkedin_client_secret:
        raise HTTPException(status_code=500, detail="LinkedIn OAuth is not configured.")

    # LinkedIn OAuth integration is currently disabled
    # This is a placeholder for future implementation
    raise HTTPException(
        status_code=501, detail="LinkedIn OAuth integration is not yet implemented."
    )


async def _linkedin_fetch_profile(access_token: str) -> Dict[str, Any]:
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(_LINKEDIN_USERINFO_ENDPOINT, headers=headers)
    except httpx.HTTPError as exc:  # pragma: no cover
        log.warning("linkedin_userinfo_http_error err=%s", exc)
        raise HTTPException(
            status_code=400, detail="Unable to fetch LinkedIn profile."
        ) from exc

    if response.status_code != 200:
        log.warning(
            "linkedin_profile_failed status=%s body=%s",
            response.status_code,
            response.text[:256],
        )
        raise HTTPException(status_code=400, detail="Unable to fetch LinkedIn profile.")

    data = response.json()
    email = data.get("email") or data.get("email_verified")
    if not email:
        raise HTTPException(
            status_code=400, detail="LinkedIn account did not provide an email."
        )

    return {
        "email": email,
        "first_name": data.get("given_name") or data.get("localizedFirstName") or "",
        "last_name": data.get("family_name") or data.get("localizedLastName") or "",
        "provider_uid": data.get("sub") or data.get("id") or email,
    }


def _finalize_social_login(
    *,
    provider: str,
    provider_uid: str,
    email: str,
    first_name: Optional[str],
    last_name: Optional[str],
    db: Session,
    response: Response,
    request: Request,
    ip: Optional[str],
) -> SocialTokensOut:
    user_agent = request.headers.get("user-agent")

    if not _social_login_service:
        log.error("social_login_unavailable provider=%s", provider)
        raise HTTPException(status_code=500, detail="Social login unavailable.")

    try:
        access_token, expires_at, refresh_token, user = _social_login_service(  # type: ignore[misc]
            db=db,
            provider=provider,
            provider_uid=provider_uid,
            email=email,
            first_name=first_name,
            last_name=last_name,
            user_agent=user_agent,
            ip_address=ip,
        )
    except HTTPException:
        raise
    except Exception as exc:
        log.exception(
            "social_login_service_error provider=%s email=%s err=%s",
            provider,
            email,
            exc,
        )
        raise HTTPException(status_code=500, detail="Authentication failed") from exc

    _set_refresh_cookie(response, refresh_token, expires_at=expires_at)
    log.info(
        "social_login_success provider=%s email=%s user_id=%s",
        provider,
        email,
        getattr(user, "id", None),
    )
    return SocialTokensOut(
        access_token=access_token,
        refresh_token=refresh_token,
        email=email,
        email_verified=bool(getattr(user, "is_email_verified", True)),
    )


def _adapt_role_for_service(role: str) -> Any:
    if not role:
        return role
    candidates = {
        role,
        role.strip(),
        role.strip().lower(),
        role.strip().title(),
        role.strip().upper(),
    }
    if ServiceUserRole:
        for cand in candidates:
            if not cand:
                continue
            try:
                return ServiceUserRole(cand)  # type: ignore[call-arg]
            except (ValueError, KeyError):
                try:
                    return ServiceUserRole[str(cand).upper()]  # type: ignore[index]
                except (ValueError, KeyError):
                    continue
    return role


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
    log.error(
        "auth.router: User model could not be imported; last_error=%s", _last_user_err
    )
else:
    log.debug("auth.router: User model resolved from %s", _resolved_user_path)


def _get_user_by_email(db: Session, email: str):
    if User is None:
        raise RuntimeError(
            "User model not available — adjust import path in auth/router.py"
        )
    return db.query(User).filter(User.email == email).one_or_none()


_VERIFY_RESEND_WINDOW_SECONDS = 300
_verify_resend_cache: Dict[str, float] = {}


def _verification_url(token: str) -> str:
    origin = str(settings.frontend_origin).rstrip("/")
    return f"{origin}/verify-email/{token}"


def _dispatch_verification_email(user: Any) -> str:
    token_version = int(getattr(user, "token_version", 0))
    token = issue_email_token(getattr(user, "id"), token_version)
    url = _verification_url(token)
    send_verification_email(
        getattr(user, "email"),
        url,
        first_name=getattr(user, "first_name", None),
    )
    return token


# ---- Registration function shims (relative import; support both namings) ----
_begin_reg: Optional[Callable[..., Any]] = None
_complete_reg: Optional[Callable[..., Any]] = None
_refresh_access: Optional[Callable[..., Any]] = None
_login_service: Optional[Callable[..., Any]] = None
_revoke_refresh_service: Optional[Callable[..., Any]] = None
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
_complete_reg = _pick_service_fn(
    ["complete_registration_step2", "complete_registration"]
)
_refresh_access = _pick_service_fn(["refresh_access_token"])
_login_service = _pick_service_fn(["login"])
_revoke_refresh_service = _pick_service_fn(["revoke_refresh_token", "revoke_refresh"])
_init_password_reset_service = _pick_service_fn(["initiate_password_reset"])
_complete_password_reset_service = _pick_service_fn(["complete_password_reset"])
_social_login_service = _pick_service_fn(["social_login"])


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
    fn: Callable[..., Any] = _begin_reg  # type: ignore
    params = inspect.signature(fn).parameters
    kwargs: dict[str, Any] = {
        "db": db,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "role": _adapt_role_for_service(role),
    }
    if "password_plain" in params:
        kwargs["password_plain"] = password_plain
    elif "password" in params:
        kwargs["password"] = password_plain
    elif "password_value" in params:
        kwargs["password_value"] = password_plain
    else:
        kwargs["password"] = password_plain

    result = fn(**kwargs)  # type: ignore
    if isinstance(result, str):
        return result
    if isinstance(result, dict) and "temp_token" in result:
        return str(result["temp_token"])
    temp = getattr(result, "temp_token", None)
    if temp:
        return str(temp)
    raise RuntimeError("Registration function did not return a temp token")


def _complete_registration_adapter(
    db: Session, *, temp_token: str, company: dict, profile: dict
):
    if not _complete_reg:
        raise RuntimeError(
            "Completion function not found in auth.service "
            "(looked for complete_registration_step2 / complete_registration)"
        )
    fn: Callable[..., Any] = _complete_reg  # type: ignore
    params = inspect.signature(fn).parameters
    company_name = None
    if isinstance(company, dict):
        company_name = (
            company.get("company_name")
            or company.get("name")
            or company.get("company")
            or company.get("value")
        )
    elif isinstance(company, str):
        company_name = company

    kwargs: dict[str, Any] = {"db": db, "temp_token": temp_token}
    if "company_name" in params:
        kwargs["company_name"] = company_name
    elif "company" in params:
        kwargs["company"] = company
    if "profile" in params:
        kwargs["profile"] = profile
    elif "profile_data" in params:
        kwargs["profile_data"] = profile

    result = fn(**kwargs)  # type: ignore

    if isinstance(result, dict):
        return result

    if isinstance(result, tuple):
        access_token = result[0] if len(result) > 0 else None
        refresh_token = result[1] if len(result) > 1 else None
        expires_at = result[2] if len(result) > 2 else None
        user_obj = result[3] if len(result) > 3 else None
        expires_value = (
            expires_at.isoformat() if isinstance(expires_at, datetime) else expires_at
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": expires_value,
            "user": _serialize_user(user_obj),
        }

    return result


def _refresh_access_token_adapter(db: Session, refresh_token: str) -> dict:
    if not _refresh_access:
        raise RuntimeError("Refresh function not available in auth.service")

    result = _refresh_access(db=db, refresh_token=refresh_token)  # type: ignore[misc]

    if isinstance(result, dict):
        return result

    if isinstance(result, tuple):
        access_token = result[0] if len(result) > 0 else None
        expires_at = result[1] if len(result) > 1 else None
        new_refresh = result[2] if len(result) > 2 else None
        expires_value = (
            expires_at.isoformat() if isinstance(expires_at, datetime) else expires_at
        )
        return {
            "access_token": access_token,
            "expires_at": expires_value,
            "refresh_token": new_refresh,
        }

    return {
        "access_token": None,
        "expires_at": None,
        "refresh_token": None,
    }


def _serialize_user(user: Any) -> dict:
    if user is None:
        return {}
    data = {
        "id": getattr(user, "id", None),
        "email": getattr(user, "email", None),
        "first_name": getattr(user, "first_name", None),
        "last_name": getattr(user, "last_name", None),
        "role": getattr(user, "role", None),
        "is_active": getattr(user, "is_active", getattr(user, "active", None)),
        "email_verified": getattr(
            user, "email_verified", getattr(user, "is_email_verified", None)
        ),
        "company_name": getattr(user, "company_name", None),
    }

    profile = getattr(user, "profile", None)
    if profile is not None:
        data["profile"] = getattr(profile, "profile", profile)

    return data


# -------------
# Health (quick)
# -------------


@router.get("/health", include_in_schema=False)
async def auth_health():
    return {"ok": True}


# --- CSRF token endpoint (updated to satisfy tests) ---
@router.get("/csrf", status_code=200)
async def csrf_token(response: Response):
    """
    Return a CSRF token in JSON and mirror it into the session cookie.
    """
    token = issue_csrf_token(response)
    return {"csrf": token, "csrf_token": token, "token": token}


# ---------------------------
# Registration — Step 1 (init)
# ---------------------------


@router.post("/register/step1", response_model=RegisterStep1Out, status_code=201)
async def register_step1(
    payload: RegisterStep1In,
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(require_csrf_token),
):
    email = _normalize_email(payload.email)
    role = _normalize_role(payload.role)

    await _verify_recaptcha_token(payload.recaptcha_token, request)

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
    except ValueError as ve:
        log.warning("register_step1_conflict email=%s err=%s", email, ve)
        raise HTTPException(status_code=409, detail=str(ve)) from ve
    except HTTPException:
        raise
    except Exception as e:
        log.exception("register_step1_error email=%s: %s", email, e)
        raise HTTPException(status_code=500, detail="Registration failed") from e


# -----------------------------
# Registration — Step 2 (commit)
# -----------------------------


@router.post("/register/step2", response_model=RegisterStep2Out, status_code=200)
async def register_step2(
    payload: RegisterStep2In,
    db: Session = Depends(get_db),
    _: None = Depends(require_csrf_token),
    authorization: Optional[str] = Header(default=None, convert_underscores=False),
) -> RegisterStep2Out:
    bearer_parts = (authorization or "").split()
    temp_token = (
        bearer_parts[1]
        if len(bearer_parts) == 2 and bearer_parts[0].lower() == "bearer"
        else None
    )
    if not temp_token:
        raise HTTPException(status_code=401, detail="Missing registration token")
    try:
        result = _complete_registration_adapter(
            db=db,
            temp_token=temp_token,
            company={"company_name": payload.company_name},
            profile=payload.profile.model_dump(),
        )
        if isinstance(result, dict):
            user_data = result.get("user", {})
            user_email = user_data.get("email")
            user_id = user_data.get("id")
            log.info("register_step2_ok email=%s user_id=%s", user_email, user_id)
            if user_email:
                try:
                    user_obj = _get_user_by_email(db, user_email)
                    if user_obj is not None and not getattr(
                        user_obj, "is_email_verified", False
                    ):
                        _dispatch_verification_email(user_obj)
                except Exception as exc:  # pragma: no cover - SMTP issues
                    log.exception("verification_email_failed email=%s", user_email)
                    raise HTTPException(
                        status_code=500,
                        detail="Unable to send verification email",
                    ) from exc
            raw_access_token = result.get("access_token")
            access_token = str(raw_access_token) if raw_access_token else ""

            raw_refresh = result.get("refresh_token")
            refresh_token = (
                str(raw_refresh) if isinstance(raw_refresh, (str, bytes)) else None
            )
            if isinstance(raw_refresh, str):
                refresh_token = raw_refresh

            expires_raw = result.get("expires_at")
            if isinstance(expires_raw, datetime):
                expires_value: Optional[str] = expires_raw.isoformat()
            elif expires_raw is not None:
                expires_value = str(expires_raw)
            else:
                expires_value = None

            user_payload = result.get("user", {})
            if not isinstance(user_payload, dict):
                user_payload = {}

            return RegisterStep2Out(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_value,
                user=user_payload,
            )

        log.info("register_step2_ok (non-dict result) type=%s", type(result).__name__)
        return RegisterStep2Out(
            access_token="", refresh_token=None, expires_at=None, user={}
        )
    except ValueError as ve:
        log.warning("register_step2_invalid temp: %s", ve)
        raise HTTPException(status_code=400, detail=str(ve)) from ve
    except HTTPException:
        raise
    except Exception as e:
        log.exception("register_step2_error: %s", e)
        raise HTTPException(status_code=500, detail="Registration failed") from e


@router.post("/register", response_model=LoginResponse, status_code=201)
async def register_single(
    payload: RegisterIn,
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(require_csrf_token),
):
    email = _normalize_email(payload.email)
    role = _normalize_role(payload.role) or payload.role

    await _verify_recaptcha_token(payload.recaptcha_token, request, required=False)

    try:
        temp_token = _begin_registration_adapter(
            db=db,
            email=email,
            first_name=payload.first_name.strip(),
            last_name=payload.last_name.strip(),
            password_plain=payload.password,
            role=role,
        )
        result = _complete_registration_adapter(
            db=db,
            temp_token=temp_token,
            company={"company_name": payload.company_name},
            profile=payload.profile.model_dump(),
        )
    except ValueError as exc:
        log.warning("register_single_conflict email=%s err=%s", email, exc)
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover
        log.exception("register_single_error email=%s err=%s", email, exc)
        raise HTTPException(status_code=500, detail="Registration failed") from exc

    if isinstance(result, dict):
        access_token = result.get("access_token")
        refresh_token = result.get("refresh_token")
    elif isinstance(result, tuple):
        access_token = result[0] if len(result) > 0 else None
        refresh_token = result[1] if len(result) > 1 else None
    else:
        access_token = refresh_token = None

    if not access_token or not refresh_token:
        raise HTTPException(status_code=500, detail="Registration failed")

    try:
        user_obj = _get_user_by_email(db, email)
        if user_obj and not getattr(user_obj, "is_email_verified", False):
            user_obj.is_email_verified = True
            user_obj.email_verified_at = datetime.now(timezone.utc)
            db.add(user_obj)
            db.commit()
    except Exception as exc:  # pragma: no cover
        log.exception("register_single_finalize email=%s err=%s", email, exc)

    return LoginResponse(
        access_token=access_token, refresh_token=refresh_token, email_verified=True
    )


@router.post("/verify/resend", status_code=202)
async def resend_verification(
    payload: VerificationResendIn,
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(require_csrf_token),
):
    email = _normalize_email(payload.email)
    ip = request.client.host if request.client else "unknown"
    cache_key = f"{email}:{ip}"
    now = time.monotonic()
    last_sent = _verify_resend_cache.get(cache_key, 0)
    if now - last_sent < _VERIFY_RESEND_WINDOW_SECONDS:
        raise HTTPException(
            status_code=429, detail="Please wait before requesting another email."
        )

    user = _get_user_by_email(db, email)
    if user and not getattr(user, "is_email_verified", False):
        try:
            _dispatch_verification_email(user)
        except Exception as exc:  # pragma: no cover - SMTP issues
            log.exception("verification_email_resend_failed email=%s", email)
            raise HTTPException(
                status_code=500, detail="Unable to send verification email"
            ) from exc

    _verify_resend_cache[cache_key] = now
    return {
        "message": "If an account exists for that email, a verification link has been sent."
    }


@router.get("/verify")
async def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        payload = parse_email_token(token)
    except EmailTokenError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if User is None:
        raise HTTPException(status_code=500, detail="Configuration error")

    user = db.query(User).filter(User.id == str(payload.get("sub"))).one_or_none()
    if not user:
        raise HTTPException(status_code=400, detail="Verification link is invalid")

    expected_version = int(payload.get("v", -1))
    current_version = int(getattr(user, "token_version", 0))
    if current_version != expected_version:
        raise HTTPException(status_code=400, detail="Verification link has expired")

    if not getattr(user, "is_email_verified", False):
        user.is_email_verified = True
        user.email_verified_at = datetime.now(timezone.utc)
        new_version = current_version + 1
        user.token_version = new_version
        db.add(user)
        db.commit()
        clear_user_token_version_cache(getattr(user, "id", ""))
        cache_user_token_version(getattr(user, "id", ""), new_version)
        log.info("email_verified user_id=%s", getattr(user, "id", None))
    else:
        log.info("email_verify_redundant user_id=%s", getattr(user, "id", None))

    return RedirectResponse(url="/welcome?email_verified=1", status_code=307)


# -----------
# Login Route
# -----------


@router.post("/login", response_model=LoginResponse, status_code=200)
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    user_agent: Optional[str] = Header(default=None),
    _: None = Depends(require_csrf_token),
):
    email = _normalize_email(payload.email)

    await _verify_recaptcha_token(payload.recaptcha_token, request)

    ip = request.client.host if request.client else "unknown"
    allowed, retry_after = allow_login(ip, email)
    if not allowed:
        log.warning(
            "login_rate_limited email=%s ip=%s retry=%s", email, ip, retry_after
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts",
            headers={"Retry-After": str(retry_after)},
        )

    user = _get_user_by_email(db, email)
    user_found = bool(user)
    log.info(
        "login_attempt email=%s found=%s ip=%s ua=%s", email, user_found, ip, user_agent
    )

    if user and not getattr(user, "is_email_verified", False):
        record_login_attempt(ip, email, success=False)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Check your inbox or resend.",
        )

    if _login_service:
        try:
            access_token, expires_at, refresh_token = _login_service(  # type: ignore[misc]
                db=db,
                email=email,
                password=payload.password,
                user_agent=user_agent,
                ip_address=ip,
            )
            log.info(
                "login_success email=%s user_id=%s", email, getattr(user, "id", None)
            )
            record_login_attempt(ip, email, success=True)
            log_login_attempt(
                db,
                email=email,
                success=True,
                ip_address=ip,
                user_agent=user_agent,
                details="login_success",
            )
            _set_refresh_cookie(response, refresh_token, expires_at=expires_at)
            return LoginResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                email_verified=True,
            )
        except ValueError as exc:
            record_login_attempt(ip, email, success=False)
            raise INVALID_CREDENTIALS from exc
        except HTTPException:
            raise
        except Exception as e:
            log.exception("login_service_error email=%s: %s", email, e)
            raise HTTPException(status_code=500, detail="Authentication failed") from e

    # Fallback: manual verification when service login is unavailable
    if not user:
        await asyncio.sleep(0)
        try:
            verify_password(
                payload.password,
                "$2b$12$invalidinvalidinvalidinvalidinvalidinvalidinvalidinvalid",
            )
        except Exception:
            pass
        record_login_attempt(ip, email, success=False)
        raise INVALID_CREDENTIALS

    ok = False
    stored_hash = getattr(user, "password_hash", getattr(user, "hashed_password", ""))
    try:
        ok = verify_password(payload.password, stored_hash)
    except Exception as e:
        log.warning("login_verify_error email=%s err=%s", email, e)

    log.info(
        "login_status email=%s ok=%s is_active=%s email_verified=%s role=%s",
        email,
        ok,
        getattr(user, "is_active", None),
        getattr(user, "email_verified", None),
        getattr(user, "role", None),
    )

    if not ok or not getattr(user, "is_active", True):
        record_login_attempt(ip, email, success=False)
        raise INVALID_CREDENTIALS

    try:
        access, refresh_token = create_access_refresh_tokens(
            user_id=user.id,
            email=user.email,
            role=user.role,
            token_version=getattr(user, "token_version", 1),
        )
        log.info("login_success email=%s user_id=%s", email, user.id)
        record_login_attempt(ip, email, success=True)
        log_login_attempt(
            db,
            email=email,
            success=True,
            ip_address=ip,
            user_agent=user_agent,
            details="login_success",
        )
        fallback_expiry = datetime.now(timezone.utc) + timedelta(days=7)
        _set_refresh_cookie(response, refresh_token, expires_at=fallback_expiry)
        return LoginResponse(
            access_token=access, refresh_token=refresh_token, email_verified=True
        )
    except Exception as e:
        log.exception("login_token_error email=%s: %s", email, e)
        raise HTTPException(status_code=500, detail="Authentication failed") from e


@router.post("/login/google", response_model=SocialTokensOut, status_code=200)
async def login_google(
    payload: GoogleLoginIn,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    _: None = Depends(require_csrf_token),
):
    await _verify_recaptcha_token(payload.recaptcha_token, request, required=True)

    ip = request.client.host if request.client else "unknown"

    id_token = payload.id_token
    access_token: Optional[str] = None
    if payload.code:
        token_data = await _google_exchange_code(
            payload.code, payload.redirect_uri or ""
        )
        id_token = id_token or token_data.get("id_token")
        access_token = token_data.get("access_token")

    profile = await _google_fetch_profile(id_token=id_token, access_token=access_token)
    email = _normalize_email(profile["email"])

    try:
        tokens = _finalize_social_login(
            provider="google",
            provider_uid=profile["provider_uid"],
            email=email,
            first_name=profile.get("first_name"),
            last_name=profile.get("last_name"),
            db=db,
            response=response,
            request=request,
            ip=ip,
        )
        record_login_attempt(ip, email, success=True)
        log_login_attempt(
            db,
            email=email,
            success=True,
            ip_address=ip,
            user_agent=request.headers.get("user-agent"),
            details="login_success_google",
        )
        return tokens
    except HTTPException:
        record_login_attempt(ip, email, success=False)
        raise


@router.post("/login/linkedin", response_model=SocialTokensOut, status_code=200)
async def login_linkedin(
    payload: LinkedInLoginIn,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    _: None = Depends(require_csrf_token),
):
    await _verify_recaptcha_token(payload.recaptcha_token, request, required=True)

    ip = request.client.host if request.client else "unknown"

    access_token = payload.access_token
    if payload.code:
        access_token = await _linkedin_exchange_code(
            payload.code, payload.redirect_uri or ""
        )

    if not access_token:
        raise HTTPException(status_code=400, detail="LinkedIn access token missing.")

    profile = await _linkedin_fetch_profile(access_token)
    email = _normalize_email(profile["email"])

    try:
        tokens = _finalize_social_login(
            provider="linkedin",
            provider_uid=profile["provider_uid"],
            email=email,
            first_name=profile.get("first_name"),
            last_name=profile.get("last_name"),
            db=db,
            response=response,
            request=request,
            ip=ip,
        )
        record_login_attempt(ip, email, success=True)
        log_login_attempt(
            db,
            email=email,
            success=True,
            ip_address=ip,
            user_agent=request.headers.get("user-agent"),
            details="login_success_linkedin",
        )
        return tokens
    except HTTPException:
        record_login_attempt(ip, email, success=False)
        raise


# -----------------
# Password Recovery
# -----------------


@router.get("/oauth/google/start")
async def oauth_google_start(
    request: Request, return_to: Optional[str] = None, next_url: Optional[str] = None
):
    accept_header = request.headers.get("accept", "").lower()
    prefer_json = (
        request.query_params.get("format") == "json"
        or "application/json" in accept_header
    )
    return _oauth_start(
        "google",
        request=request,
        client_id=settings.google_client_id,
        callback_override=settings.google_callback_url,
        auth_endpoint=_GOOGLE_AUTH_ENDPOINT,
        scope="openid email profile",
        extra_params={"access_type": "offline", "prompt": "select_account"},
        return_to=return_to,
        next_path=next_url,
        prefer_json=prefer_json,
    )


@router.get("/oauth/google/callback")
async def oauth_google_callback(
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
):
    return _oauth_callback(
        "google",
        request,
        code=code,
        state=state,
        error=error,
        error_description=error_description,
    )


@router.get("/oauth/linkedin/start")
async def oauth_linkedin_start(
    request: Request, return_to: Optional[str] = None, next_url: Optional[str] = None
):
    accept_header = request.headers.get("accept", "").lower()
    prefer_json = (
        request.query_params.get("format") == "json"
        or "application/json" in accept_header
    )
    return _oauth_start(
        "linkedin",
        request=request,
        client_id=settings.linkedin_client_id,
        callback_override=settings.linkedin_callback_url,
        auth_endpoint=_LINKEDIN_AUTH_ENDPOINT,
        scope="openid email profile",
        extra_params={"prompt": "consent"},
        return_to=return_to,
        next_path=next_url,
        prefer_json=prefer_json,
    )


@router.get("/oauth/linkedin/callback")
async def oauth_linkedin_callback(
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
):
    return _oauth_callback(
        "linkedin",
        request,
        code=code,
        state=state,
        error=error,
        error_description=error_description,
    )


@router.post("/password/forgot", response_model=ForgotPasswordOut, status_code=200)
async def forgot_password(
    payload: ForgotPasswordIn,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
    user_agent: Optional[str] = Header(default=None),
    _: None = Depends(require_csrf_token),
) -> ForgotPasswordOut:
    email = _normalize_email(payload.email)
    ip = request.client.host if request.client else "unknown"

    if not _init_password_reset_service:
        log.error("password_reset_initiate_missing")
        raise HTTPException(status_code=500, detail="Password reset unavailable")

    outcome = "error"
    user_id: Optional[str] = None
    try:
        result = _init_password_reset_service(db=db, email=email)  # type: ignore[misc]
    except Exception as e:
        try:
            db.rollback()
        except Exception:
            pass
        log.exception("password_reset_initiate_error email=%s err=%s", email, e)
        result = None
        outcome = "error"

    if result:
        user, raw_token, expires_at = result
        user_id = getattr(user, "id", None)
        outcome = "issued"
        reset_url = f"{str(settings.frontend_origin).rstrip('/')}/reset-password?token={raw_token}"
        background_tasks.add_task(
            send_password_reset_email,
            user.email,
            reset_url,
            expires_at,
        )
        log.info(
            "password_reset_token_issued user_id=%s email=%s expires_at=%s",
            getattr(user, "id", None),
            user.email,
            expires_at.isoformat(),
        )
    else:
        outcome = "no_user"
        log.info("password_reset_initiate_no_user email=%s", email)

    try:
        db.add(
            models.AuditEvent(
                user_id=user_id,
                event_type="auth_password_reset_requested",
                payload={
                    "email": email,
                    "outcome": outcome,
                },
                ip_address=ip,
                user_agent=user_agent,
            )
        )
        db.commit()
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass

    return ForgotPasswordOut()


@router.post("/password/reset", response_model=ResetPasswordOut, status_code=200)
async def reset_password(
    payload: ResetPasswordIn,
    request: Request,
    db: Session = Depends(get_db),
    user_agent: Optional[str] = Header(default=None),
    _: None = Depends(require_csrf_token),
) -> ResetPasswordOut:
    if not _complete_password_reset_service:
        log.error("password_reset_complete_missing")
        raise HTTPException(status_code=500, detail="Password reset unavailable")

    token_preview = (payload.token or "")[:6] + "***"
    ip = request.client.host if request.client else "unknown"

    try:
        user = _complete_password_reset_service(  # type: ignore[misc]
            db=db,
            token=payload.token,
            new_password=payload.password,
        )
    except ValueError as ve:
        log.warning("password_reset_invalid token=%s err=%s", token_preview, ve)

        audit_user_id: Optional[str] = None
        try:
            normalized_token = (payload.token or "").strip()
            if normalized_token:
                token_hash = hashlib.sha256(normalized_token.encode()).hexdigest()
                record = (
                    db.query(models.PasswordResetToken)
                    .filter(models.PasswordResetToken.token_hash == token_hash)
                    .one_or_none()
                )
                if record is not None:
                    audit_user_id = getattr(record, "user_id", None)
        except Exception:
            try:
                db.rollback()
            except Exception:
                pass

        try:
            db.add(
                models.AuditEvent(
                    user_id=audit_user_id,
                    event_type="auth_password_reset_completed",
                    payload={
                        "success": False,
                        "reason": "invalid_or_expired",
                        "token_preview": token_preview,
                    },
                    ip_address=ip,
                    user_agent=user_agent,
                )
            )
            db.commit()
        except Exception:
            try:
                db.rollback()
            except Exception:
                pass

        raise HTTPException(
            status_code=400, detail="Invalid or expired reset token"
        ) from ve
    except Exception as e:
        log.exception("password_reset_error token=%s err=%s", token_preview, e)
        raise HTTPException(status_code=500, detail="Unable to reset password") from e

    clear_user_token_version_cache(getattr(user, "id", ""))
    try:
        db.add(
            models.AuditEvent(
                user_id=getattr(user, "id", None),
                event_type="auth_password_reset_completed",
                payload={
                    "success": True,
                },
                ip_address=ip,
                user_agent=user_agent,
            )
        )
        db.commit()
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
    log.info("password_reset_success user_id=%s", getattr(user, "id", None))
    return ResetPasswordOut()


# -----------
# Refresh JWT
# -----------


@router.post("/refresh", response_model=RefreshOut, status_code=200)
async def refresh(
    request: Request,
    response: Response,
    payload: Optional[RefreshIn] = Body(default=None),
    db: Session = Depends(get_db),
) -> RefreshOut:
    token = _resolve_refresh_token(payload, request)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    try:
        result = _refresh_access_token_adapter(db, token)
    except ValueError as ve:
        log.info("refresh_invalid_token: %s", ve)
        raise HTTPException(status_code=401, detail="Invalid refresh token") from ve
    except Exception as e:
        log.exception("refresh_error: %s", e)
        raise HTTPException(status_code=401, detail="Invalid refresh token") from e

    access_token = result.get("access_token") if isinstance(result, dict) else None
    refresh_token = result.get("refresh_token") if isinstance(result, dict) else None
    expires_at = result.get("expires_at") if isinstance(result, dict) else None

    if not access_token or not refresh_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    _set_refresh_cookie(response, refresh_token, expires_at=expires_at)
    return RefreshOut(
        access_token=access_token, refresh_token=refresh_token, expires_at=expires_at
    )


# ----
# /me
# ----


@router.get("/me", response_model=MeResponse)
async def me(current_user=Depends(get_current_user)):
    return MeResponse(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role=current_user.role,
        is_active=current_user.is_active,
        email_verified=bool(
            getattr(
                current_user,
                "email_verified",
                getattr(current_user, "is_email_verified", True),
            )
        ),
    )


@router.post("/logout", response_model=LogoutOut, status_code=200)
async def logout(
    request: Request,
    response: Response,
    payload: LogoutIn = Body(default_factory=LogoutIn),
    db: Session = Depends(get_db),
    _: None = Depends(require_csrf_token),
    authorization: Optional[str] = Header(default=None, convert_underscores=False),
):
    user: Optional[Any] = None
    claims: Dict[str, Any] = {}
    token: Optional[str] = None
    try:
        user, claims, token = await get_current_user_with_claims(
            request, db, authorization
        )
    except HTTPException as exc:
        if exc.status_code != status.HTTP_401_UNAUTHORIZED:
            raise

        if exc.detail == "Token expired":
            try:
                token = _token_from_request(request, authorization)
            except HTTPException:
                token = None
        else:
            token = _bearer_from_header(authorization) or request.cookies.get(
                "access_token"
            )

        if token:
            try:
                claims = decode_jwt(token, verify_exp=False)
            except ValueError:
                claims = {}
        else:
            claims = {}

        if claims:
            try:
                user = _load_user_from_claims(db, claims)
            except HTTPException:
                user = None
    jti = claims.get("jti") if isinstance(claims, dict) else None
    exp = claims.get("exp") if isinstance(claims, dict) else None
    if isinstance(jti, str) and isinstance(exp, int):
        try:
            denylist_jti(jti, exp)
        except Exception as e:
            log.warning("logout_denylist_failed jti=%s err=%s", jti, e)

    if payload.all_devices and user is not None:
        current_version = int(getattr(user, "token_version", 1))
        new_version = current_version + 1
        setattr(user, "token_version", new_version)
        db.add(user)
        db.commit()
        clear_user_token_version_cache(getattr(user, "id", ""))
        cache_user_token_version(getattr(user, "id", ""), new_version)
    else:
        db.commit()

    refresh_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if refresh_token and _revoke_refresh_service:
        try:
            _revoke_refresh_service(db=db, refresh_token=refresh_token)
        except Exception as e:
            log.warning("logout_revoke_failed: %s", e)
        else:
            db.commit()

    _clear_refresh_cookie(response)
    if not token:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return LogoutOut()


@router.post("/analytics/track", status_code=204)
async def track_analytics(
    event: AnalyticsEventIn,
    db: Session = Depends(get_db),
) -> None:
    """
    Log lightweight analytics events (step views, submissions, errors, completion).
    """
    db_event = AnalyticsEvent(
        event_type=event.event_type,
        step=event.step,
        role=event.role,
        details=event.details,
    )
    db.add(db_event)
    db.commit()
    return None
