"""
Enhanced Authentication Service
==============================

This service implements the secure authentication architecture with:
- JWT token generation and validation
- Role-based access control
- Password reset functionality
- Session management
- Audit logging
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models_enhanced import UserV2, Token, PasswordReset, AuditLog, UserRole
from app.schemas_enhanced import UserCreate, TokenResponse, UserResponse
import os

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
RESET_TOKEN_EXPIRE_HOURS = 24

class AuthService:
    """Enhanced authentication service with JWT and role-based access"""
    
    def __init__(self):
        self.pwd_context = pwd_context
        
    # ================================
    # Password Management
    # ================================
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password for storing"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a stored password against a provided password"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    # ================================
    # JWT Token Management
    # ================================
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create a JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token type. Expected {token_type}"
                )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    
    # ================================
    # User Authentication
    # ================================
    
    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[UserV2]:
        """Authenticate a user by email and password"""
        user = db.query(UserV2).filter(UserV2.email == email).first()
        if not user:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated"
            )
        return user
    
    def create_user_tokens(self, db: Session, user: UserV2, user_agent: str = None, ip_address: str = None) -> TokenResponse:
        """Create access and refresh tokens for a user"""
        # Create token payload
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "is_verified": user.is_verified
        }
        
        # Generate tokens
        access_token = self.create_access_token(token_data)
        refresh_token = self.create_refresh_token({"sub": str(user.id)})
        
        # Store tokens in database
        access_token_expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        # Store access token
        db_access_token = Token(
            user_id=user.id,
            token=access_token,
            token_type="access",
            expires_at=access_token_expires,
            user_agent=user_agent,
            ip_address=ip_address
        )
        db.add(db_access_token)
        
        # Store refresh token
        db_refresh_token = Token(
            user_id=user.id,
            token=refresh_token,
            token_type="refresh",
            expires_at=refresh_token_expires,
            user_agent=user_agent,
            ip_address=ip_address
        )
        db.add(db_refresh_token)
        
        # Update last login
        user.last_login_at = datetime.utcnow()
        
        db.commit()
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.from_orm(user)
        )
    
    def refresh_access_token(self, db: Session, refresh_token: str) -> TokenResponse:
        """Refresh an access token using a refresh token"""
        # Verify refresh token
        payload = self.verify_token(refresh_token, "refresh")
        user_id = int(payload.get("sub"))
        
        # Check if refresh token exists and is valid
        db_token = db.query(Token).filter(
            Token.token == refresh_token,
            Token.token_type == "refresh",
            Token.is_revoked == False,
            Token.expires_at > datetime.utcnow()
        ).first()
        
        if not db_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user
        user = db.query(UserV2).filter(UserV2.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "is_verified": user.is_verified
        }
        
        access_token = self.create_access_token(token_data)
        access_token_expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Store new access token
        db_access_token = Token(
            user_id=user.id,
            token=access_token,
            token_type="access",
            expires_at=access_token_expires,
            user_agent=db_token.user_agent,
            ip_address=db_token.ip_address
        )
        db.add(db_access_token)
        
        # Update refresh token usage
        db_token.used_at = datetime.utcnow()
        
        db.commit()
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.from_orm(user)
        )
    
    def revoke_token(self, db: Session, token: str, token_type: str = "access"):
        """Revoke a token"""
        db_token = db.query(Token).filter(
            Token.token == token,
            Token.token_type == token_type
        ).first()
        
        if db_token:
            db_token.is_revoked = True
            db.commit()
    
    def revoke_all_user_tokens(self, db: Session, user_id: int):
        """Revoke all tokens for a user"""
        db.query(Token).filter(Token.user_id == user_id).update({"is_revoked": True})
        db.commit()
    
    # ================================
    # Password Reset
    # ================================
    
    def generate_reset_token(self) -> str:
        """Generate a secure reset token"""
        return secrets.token_urlsafe(32)
    
    def create_password_reset(self, db: Session, user: UserV2, ip_address: str = None, user_agent: str = None) -> str:
        """Create a password reset token"""
        # Invalidate existing reset tokens
        db.query(PasswordReset).filter(
            PasswordReset.user_id == user.id,
            PasswordReset.is_used == False
        ).update({"is_used": True})
        
        # Create new reset token
        reset_token = self.generate_reset_token()
        expires_at = datetime.utcnow() + timedelta(hours=RESET_TOKEN_EXPIRE_HOURS)
        
        db_reset = PasswordReset(
            user_id=user.id,
            token=reset_token,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(db_reset)
        db.commit()
        
        return reset_token
    
    def verify_reset_token(self, db: Session, token: str) -> UserV2:
        """Verify a password reset token and return the user"""
        db_reset = db.query(PasswordReset).filter(
            PasswordReset.token == token,
            PasswordReset.is_used == False,
            PasswordReset.expires_at > datetime.utcnow()
        ).first()
        
        if not db_reset:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        user = db.query(UserV2).filter(UserV2.id == db_reset.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user, db_reset
    
    def reset_password(self, db: Session, token: str, new_password: str) -> bool:
        """Reset a user's password using a reset token"""
        user, db_reset = self.verify_reset_token(db, token)
        
        # Update password
        user.password_hash = self.get_password_hash(new_password)
        
        # Mark reset token as used
        db_reset.is_used = True
        db_reset.used_at = datetime.utcnow()
        
        # Revoke all existing tokens
        self.revoke_all_user_tokens(db, user.id)
        
        db.commit()
        return True
    
    # ================================
    # Role-based Access Control
    # ================================
    
    def check_role_permission(self, user_role: str, required_roles: list) -> bool:
        """Check if user role has permission"""
        return user_role in required_roles
    
    def require_roles(self, user_role: str, required_roles: list):
        """Require user to have specific roles"""
        if not self.check_role_permission(user_role, required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {required_roles}"
            )
    
    # ================================
    # Audit Logging
    # ================================
    
    def log_event(self, db: Session, user_id: Optional[int], event_type: str, 
                  event_description: str = None, success: bool = True, 
                  ip_address: str = None, user_agent: str = None, 
                  endpoint: str = None, error_message: str = None, 
                  metadata: dict = None):
        """Log an audit event"""
        audit_log = AuditLog(
            user_id=user_id,
            event_type=event_type,
            event_description=event_description,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            error_message=error_message,
            metadata=str(metadata) if metadata else None
        )
        db.add(audit_log)
        db.commit()

# Create global auth service instance
auth_service = AuthService()
