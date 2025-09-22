from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.deps import get_db
from app.crud import user as crud_user
from app.core.security import create_reset_token, decode, is_reset_token, hash_password
from app.utils.rate_limiter import rate_limit
from app.services.mailer import send_verification_email
import os

router = APIRouter(prefix="/api/auth", tags=["auth"])


class ResetRequest(BaseModel):
    email: EmailStr


class ConfirmReset(BaseModel):
    token: str
    new_password: str


@router.post('/request-reset')
def request_reset(payload: ResetRequest, db: Session = Depends(get_db)):
    # Rate-limit by email to avoid enumeration abuse
    from app.utils.rate_limiter import check_rate_limit
    try:
        check_rate_limit('request_reset', payload.email, limit=5, period=300)
    except Exception:
        raise
    user = crud_user.get_user_by_email(db, payload.email)
    # Always return 200 to avoid leaking whether a user exists
    if not user:
        return {"ok": True, "message": "If that account exists you'll receive reset instructions."}

    token = create_reset_token(user.id)
    link = f"/api/auth/confirm-reset?token={token}"
    env = os.getenv('ENVIRONMENT', 'development')
    if env == 'development':
        print(f"[DEV RESET LINK] {link}")
        return {"ok": True, "message": "Password reset link generated (dev).", "token": token}
    else:
        send_verification_email(user.email, link)
        return {"ok": True, "message": "Password reset email queued."}


@router.post('/confirm-reset')
def confirm_reset(payload: ConfirmReset, db: Session = Depends(get_db)):
    try:
        data = decode(payload.token)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    if data.get('type') != 'reset':
        raise HTTPException(status_code=400, detail="Not a reset token")
    uid = int(data.get('sub'))
    user = crud_user.get_user_by_id(db, uid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update password and set password_changed_at
    user.password_hash = hash_password(payload.new_password)
    from datetime import datetime, timezone
    user.password_changed_at = datetime.now(timezone.utc)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"ok": True, "message": "Password updated."}
