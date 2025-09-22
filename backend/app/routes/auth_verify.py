from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.deps import get_db
from app.crud import user as crud_user
from app.core.security import create_verification_token, decode
from app.services.mailer import send_verification_email
import os

router = APIRouter(prefix="/api/auth", tags=["auth"])


class VerifyRequest(BaseModel):
    email: EmailStr


@router.post("/request-verify")
def request_verify(payload: VerifyRequest, db: Session = Depends(get_db)):
    user = crud_user.get_user_by_email(db, payload.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    token = create_verification_token(user.id)
    link = f"/api/auth/confirm-verify?token={token}"
    # Send email in production; in development log and return token for tests
    env = os.getenv('ENVIRONMENT', 'development')
    if env == 'development':
        print(f"[DEV VERIFICATION LINK] {link}")
        # Return token in response to simplify tests
        return {"ok": True, "message": "Verification link generated (dev).", "token": token}
    else:
        send_verification_email(user.email, link)
        return {"ok": True, "message": "Verification email queued."}


class ConfirmQuery(BaseModel):
    token: str


@router.get("/confirm-verify")
def confirm_verify(token: str, db: Session = Depends(get_db)):
    try:
        payload = decode(token)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    if payload.get("type") != "verify":
        raise HTTPException(status_code=400, detail="Not a verification token")
    uid = int(payload.get("sub"))
    user = crud_user.get_user_by_id(db, uid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_verified = True
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"ok": True, "message": "User verified."}
