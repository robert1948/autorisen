from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import os
import re
from typing import Optional
from datetime import datetime

from app import models, schemas
from app.dependencies import get_db
from app.auth import get_password_hash, verify_password, create_access_token
from app.services.audit_service import get_audit_logger, AuditEventType, AuditLogLevel
from app.config import settings

router = APIRouter()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM

@router.get("/v2/validate-email", tags=["auth-v2"])
async def validate_email(email: str, db: Session = Depends(get_db)):
    try:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return {
                "available": False,
                "reason": "invalid_format",
                "message": "Please enter a valid email address"
            }
        normalized_email = email.lower().strip()
        existing_user = db.query(models.User).filter(models.User.email == normalized_email).first()
        if existing_user:
            return {
                "available": False,
                "reason": "already_exists",
                "message": "This email is already registered. Try logging in or use a different email."
            }
        return {"available": True, "message": "Email is available"}
    except Exception as e:
        print(f"❌ Email validation error: {e}")
        return {
            "available": None,
            "reason": "validation_error",
            "message": "Unable to validate email. Please try again."
        }

@router.post("/v2/validate-password", tags=["auth-v2"])
async def validate_password(password_data: dict):
    password = password_data.get("password", "")
    requirements = {
        "minLength": len(password) >= 12,
        "hasUpper": bool(re.search(r'[A-Z]', password)),
        "hasLower": bool(re.search(r'[a-z]', password)),
        "hasNumber": bool(re.search(r'[0-9]', password)),
        "hasSpecial": bool(re.search(r'[^A-Za-z0-9]', password))
    }
    score = sum([
        25 if requirements["minLength"] else 0,
        20 if requirements["hasUpper"] else 0,
        20 if requirements["hasLower"] else 0,
        20 if requirements["hasNumber"] else 0,
        15 if requirements["hasSpecial"] else 0
    ])
    all_valid = all(requirements.values())
    return {
        "valid": all_valid,
        "score": min(score, 100),
        "requirements": requirements,
        "message": "Strong password" if all_valid else "Password doesn't meet requirements"
    }

@router.post("/v2/register", response_model=schemas.UserOut, tags=["auth-v2"])
async def register_v2(
    user: schemas.UserCreateV2Production,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db)
):
    audit_logger = get_audit_logger()
    try:
        normalized_email = user.email.lower().strip()
        existing_user = db.query(models.User).filter(models.User.email == normalized_email).first()
        if existing_user:
            audit_logger.log_authentication_event(
                db=db,
                event_type=AuditEventType.USER_REGISTRATION_FAILED,
                request=request,
                user_email=normalized_email,
                success=False,
                error_message="Email already registered",
                additional_data={"reason": "duplicate_email", "user_role": user.user_role}
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered. Please use a different email or try logging in."
            )
        hashed_password = get_password_hash(user.password)
        name_parts = user.full_name.strip().split(' ', 1)
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        db_user = models.User(
            email=normalized_email,
            password_hash=hashed_password,
            role=user.user_role,
            first_name=first_name,
            last_name=last_name,
            company=user.company_name.strip() if user.company_name else None,
            terms_accepted_at=datetime.utcnow()
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        audit_logger.log_authentication_event(
            db=db,
            event_type=AuditEventType.USER_REGISTRATION,
            request=request,
            user_id=str(db_user.id),
            user_email=db_user.email,
            user_role=db_user.role,
            success=True,
            additional_data={
                "user_role": user.user_role,
                "company_name": user.company_name,
                "registration_method": "v2_direct"
            }
        )
        background_tasks.add_task(send_welcome_email_task, {
            'full_name': user.full_name,
            'email': user.email,
            'user_role': user.user_role,
            'company_name': user.company_name or '',
            'userId': db_user.id
        })
        print(f"✅ User registered successfully: {user.email} as {user.user_role}")
        return {"id": str(db_user.id), "email": db_user.email}
    except HTTPException:
        raise
    except IntegrityError as e:
        db.rollback()
        print(f"❌ Database integrity error: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered. Please use a different email."
        )
    except Exception as e:
        db.rollback()
        print(f"❌ Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again later."
        )

async def send_welcome_email_task(user_data: dict):
    try:
        from app.email_service import email_service
        await email_service.send_registration_notification(user_data)
        print(f"✅ Welcome email sent to {user_data['email']}")
    except Exception as e:
        print(f"⚠️  Failed to send welcome email to {user_data['email']}: {e}")
