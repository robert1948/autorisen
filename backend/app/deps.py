# backend/app/deps.py
from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import decode_token
from app.crud import user as crud_user

bearer = HTTPBearer(auto_error=False)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)) -> User:
    if not creds or not creds.scheme.lower() == "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = decode_token(creds.credentials)
        sub = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    # sub may be an email (legacy) or a numeric user id
    user = None
    if sub is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    try:
        uid = int(sub)
    except Exception:
        uid = None
    if uid is not None:
        user = crud_user.get_user_by_id(db, uid)
    else:
        user = crud_user.get_user_by_email(db, sub)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    # Invalidate tokens issued before a user's password change. Tokens include an
    # 'iat' claim set at issuance time. If the user's `password_changed_at` is set
    # and is after the token `iat`, the token should be rejected.
    # Prefer high-precision iat_ms (ms) if available; otherwise fall back to iat
    # (seconds) converted to ms.
    iat_ms = None
    # Try parsing iat_ms first; if it's missing or malformed, fall back to iat
    if "iat_ms" in payload:
        try:
            iat_ms = int(payload.get("iat_ms"))
        except Exception:
            iat_ms = None
    # If iat_ms wasn't usable, try legacy iat (seconds)
    if iat_ms is None and "iat" in payload:
        try:
            iat_ms = int(payload.get("iat")) * 1000
        except Exception:
            iat_ms = None

    if iat_ms is not None and user.password_changed_at is not None:
        pwd_changed_ms = int(user.password_changed_at.timestamp() * 1000)
        if iat_ms <= pwd_changed_ms:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalid due to password change")
    return user
