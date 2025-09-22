from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.security.passwords import verify_password
from app.settings import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

# ---- Schemas ----
class LoginIn(BaseModel):
    email: EmailStr
    password: str

class AuthOK(BaseModel):
    ok: bool

# ---- Helpers ----
def _issue_access_token(user_id: int, ttl_minutes: int = 60) -> str:
    now = datetime.now(tz=timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ttl_minutes)).timestamp()),
        "env": settings.environment,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")

def _cookie_kwargs():
    is_prod = settings.environment in ("staging", "production")
    return dict(
        httponly=True,
        secure=settings.cookie_secure if hasattr(settings, "cookie_secure") else is_prod,
        samesite="lax" if not is_prod else "none",
        domain=getattr(settings, "cookie_domain", None),  # e.g. ".cape-control.com" for split-origin
        max_age=60 * 60,  # 1 hour
        path="/",
    )

# ---- Routes ----
@router.post("/login", response_model=AuthOK)
def login(data: LoginIn, response: Response, db: Session = Depends(get_db)):
    user: Optional[User] = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # If you enforce email verification:
    if getattr(user, "is_verified", True) is False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not verified")

    token = _issue_access_token(user.id)
    response.set_cookie("access_token", token, **_cookie_kwargs())
    return {"ok": True}

@router.post("/logout", response_model=AuthOK)
def logout(response: Response):
    # Clear cookie
    response.delete_cookie("access_token", path="/")
    return {"ok": True}
