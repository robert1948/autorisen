"""
Password Reset API Routes
RESTful endpoints for password reset functionality
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, field_validator
import re
from typing import Optional

from app.dependencies import get_db
from app.services.password_reset_service import password_reset_service
from app.services.audit_service import get_audit_logger, AuditEventType

router = APIRouter(prefix="/api/auth", tags=["password-reset"])

class PasswordResetRequestModel(BaseModel):
    """Request model for password reset"""
    email: EmailStr
    
class PasswordResetConfirmModel(BaseModel):
    """Request model for password reset confirmation"""
    token: str
    new_password: str
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        return v

class PasswordResetVerifyModel(BaseModel):
    """Request model for token verification"""
    token: str

class PasswordResetResponseModel(BaseModel):
    """Response model for password reset operations"""
    success: bool
    message: str

@router.post("/password-reset/request", response_model=PasswordResetResponseModel)
async def request_password_reset(
    request_data: PasswordResetRequestModel,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Request password reset for a user
    
    - **email**: User's email address
    
    Returns success message regardless of whether email exists (security best practice)
    """
    audit_logger = get_audit_logger()
    
    try:
        result = await password_reset_service.request_password_reset(
            db=db, 
            email=request_data.email
        )
        
        # Log the attempt
        audit_logger.log_authentication_event(
            db=db,
            event_type=AuditEventType.PASSWORD_RESET_REQUESTED,
            request=request,
            user_email=request_data.email,
            success=result["success"],
            additional_data={"user_agent": request.headers.get("user-agent", "")}
        )
        
        return PasswordResetResponseModel(
            success=result["success"],
            message=result["message"]
        )
        
    except Exception as e:
        audit_logger.log_authentication_event(
            db=db,
            event_type=AuditEventType.PASSWORD_RESET_REQUESTED,
            request=request,
            user_email=request_data.email,
            success=False,
            error_message=str(e)
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred processing your request"
        )

@router.post("/password-reset/verify", response_model=dict)
async def verify_reset_token(
    verify_data: PasswordResetVerifyModel,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Verify if a password reset token is valid
    
    - **token**: Password reset token from email
    
    Returns token validity status
    """
    audit_logger = get_audit_logger()
    
    try:
        user = await password_reset_service.verify_reset_token(
            db=db,
            token=verify_data.token
        )
        
        is_valid = user is not None
        
        # Log the verification attempt
        audit_logger.log_authentication_event(
            db=db,
            event_type=AuditEventType.PASSWORD_RESET_TOKEN_VERIFIED,
            request=request,
            user_id=str(user.id) if user else None,
            user_email=user.email if user else None,
            success=is_valid,
            additional_data={"token_length": len(verify_data.token)}
        )
        
        return {
            "valid": is_valid,
            "message": "Token is valid" if is_valid else "Invalid or expired token",
            "user_email": user.email if user else None
        }
        
    except Exception as e:
        audit_logger.log_authentication_event(
            db=db,
            event_type=AuditEventType.PASSWORD_RESET_TOKEN_VERIFIED,
            request=request,
            success=False,
            error_message=str(e)
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred verifying the token"
        )

@router.post("/password-reset/confirm", response_model=PasswordResetResponseModel)
async def confirm_password_reset(
    confirm_data: PasswordResetConfirmModel,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Complete password reset with token and new password
    
    - **token**: Valid password reset token
    - **new_password**: New password (must meet security requirements)
    
    Resets the user's password and invalidates the token
    """
    audit_logger = get_audit_logger()
    
    try:
        # First verify the user exists
        user = await password_reset_service.verify_reset_token(
            db=db,
            token=confirm_data.token
        )
        
        if not user:
            audit_logger.log_authentication_event(
                db=db,
                event_type=AuditEventType.PASSWORD_RESET_COMPLETED,
                request=request,
                success=False,
                error_message="Invalid or expired token"
            )
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Reset the password
        result = await password_reset_service.reset_password(
            db=db,
            token=confirm_data.token,
            new_password=confirm_data.new_password
        )
        
        # Log the result
        audit_logger.log_authentication_event(
            db=db,
            event_type=AuditEventType.PASSWORD_RESET_COMPLETED,
            request=request,
            user_id=str(user.id),
            user_email=user.email,
            success=result["success"],
            additional_data={"user_agent": request.headers.get("user-agent", "")}
        )
        
        if result["success"]:
            return PasswordResetResponseModel(
                success=True,
                message=result["message"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
    except HTTPException:
        raise
    except Exception as e:
        audit_logger.log_authentication_event(
            db=db,
            event_type=AuditEventType.PASSWORD_RESET_COMPLETED,
            request=request,
            success=False,
            error_message=str(e)
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred resetting your password"
        )

# Health check endpoint
@router.get("/password-reset/health")
async def password_reset_health():
    """Health check for password reset service"""
    return {
        "service": "password_reset",
        "status": "healthy",
        "features": {
            "sendgrid_available": password_reset_service.sendgrid_api_key is not None,
            "smtp_fallback": password_reset_service.smtp_username is not None,
            "email_configured": bool(password_reset_service.from_email)
        }
    }
