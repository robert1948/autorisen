"""
Enhanced Authentication Service
==============================

Implements secure authentication with:
- JWT access & refresh tokens
- Role-based access control
- Password reset workflows
- Audit logging

Refactored to use timezone-aware UTC datetimes via utc_now().
"""

from __future__ import annotations

import os
import secrets
from datetime import timedelta
from typing import Any

from fastapi import HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.utils.datetime import utc_now
from app.models_enhanced import AuditLog, PasswordReset, Token, UserV2
from app.schemas_enhanced import TokenResponse, UserResponse

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
RESET_TOKEN_EXPIRE_HOURS = 24


class AuthService:
    """Authentication service providing token management and password workflows."""

    def __init__(self) -> None:
        self.pwd_context = pwd_context

    # Password Management -------------------------------------------------
    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    # JWT Token Management ------------------------------------------------
    def create_access_token(
        self, data: dict[str, Any], expires_delta: timedelta | None = None
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = utc_now() + expires_delta
        else:
            expire = utc_now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def create_refresh_token(self, data: dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = utc_now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def verify_token(self, token: str, token_type: str = "access") -> dict[str, Any]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token type. Expected {token_type}",
                )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

    # User Authentication -------------------------------------------------
    def authenticate_user(
        self, db: Session, email: str, password: str
    ) -> UserV2 | None:
        user = db.query(UserV2).filter(UserV2.email == email).first()
        if not user:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated",
            )
        return user

    def create_user_tokens(
        self,
        db: Session,
        user: UserV2,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> TokenResponse:
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "is_verified": user.is_verified,
        }
        access_token = self.create_access_token(token_data)
        refresh_token = self.create_refresh_token({"sub": str(user.id)})

        access_token_expires = utc_now() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
        refresh_token_expires = utc_now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        db.add(
            Token(
                user_id=user.id,
                token=access_token,
                token_type="access",
                expires_at=access_token_expires,
                user_agent=user_agent,
                ip_address=ip_address,
            )
        )
        db.add(
            Token(
                user_id=user.id,
                token=refresh_token,
                token_type="refresh",
                expires_at=refresh_token_expires,
                user_agent=user_agent,
                ip_address=ip_address,
            )
        )

        user.last_login_at = utc_now()
        db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.from_orm(user),
        )

    def refresh_access_token(self, db: Session, refresh_token: str) -> TokenResponse:
        payload = self.verify_token(refresh_token, "refresh")
        user_id = int(payload.get("sub"))

        db_token = (
            db.query(Token)
            .filter(
                Token.token == refresh_token,
                Token.token_type == "refresh",
                Token.is_revoked == False,  # noqa: E712
                Token.expires_at > utc_now(),
            )
            .first()
        )
        if not db_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        user = db.query(UserV2).filter(UserV2.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "is_verified": user.is_verified,
        }
        access_token = self.create_access_token(token_data)
        access_token_expires = utc_now() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

        db.add(
            Token(
                user_id=user.id,
                token=access_token,
                token_type="access",
                expires_at=access_token_expires,
                user_agent=db_token.user_agent,
                ip_address=db_token.ip_address,
            )
        )
        db_token.used_at = utc_now()
        db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.from_orm(user),
        )

    # Token Revocation ----------------------------------------------------
    def revoke_token(self, db: Session, token: str, token_type: str = "access") -> None:
        db_token = (
            db.query(Token)
            .filter(Token.token == token, Token.token_type == token_type)
            .first()
        )
        if db_token:
            db_token.is_revoked = True
            db.commit()

    def revoke_all_user_tokens(self, db: Session, user_id: int) -> None:
        db.query(Token).filter(Token.user_id == user_id).update({"is_revoked": True})
        db.commit()

    # Password Reset ------------------------------------------------------
    def generate_reset_token(self) -> str:
        return secrets.token_urlsafe(32)

    def create_password_reset(
        self,
        db: Session,
        user: UserV2,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> str:
        db.query(PasswordReset).filter(
            PasswordReset.user_id == user.id,
            PasswordReset.is_used == False,  # noqa: E712
        ).update({"is_used": True})

        reset_token = self.generate_reset_token()
        expires_at = utc_now() + timedelta(hours=RESET_TOKEN_EXPIRE_HOURS)
        db.add(
            PasswordReset(
                user_id=user.id,
                token=reset_token,
                expires_at=expires_at,
                ip_address=ip_address,
                user_agent=user_agent,
            )
        )
        db.commit()
        return reset_token

    def verify_reset_token(
        self, db: Session, token: str
    ) -> tuple[UserV2, PasswordReset]:
        db_reset = (
            db.query(PasswordReset)
            .filter(
                PasswordReset.token == token,
                PasswordReset.is_used == False,  # noqa: E712
                PasswordReset.expires_at > utc_now(),
            )
            .first()
        )
        if not db_reset:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )
        user = db.query(UserV2).filter(UserV2.id == db_reset.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user, db_reset

    def reset_password(self, db: Session, token: str, new_password: str) -> bool:
        user, db_reset = self.verify_reset_token(db, token)
        user.password_hash = self.get_password_hash(new_password)
        db_reset.is_used = True
        db_reset.used_at = utc_now()
        self.revoke_all_user_tokens(db, user.id)
        db.commit()
        return True

    # Role-based Access Control ------------------------------------------
    def check_role_permission(self, user_role: str, required_roles: list[str]) -> bool:
        return user_role in required_roles

    def require_roles(self, user_role: str, required_roles: list[str]) -> None:
        if not self.check_role_permission(user_role, required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {required_roles}",
            )

    # Audit Logging -------------------------------------------------------
    def log_event(
        self,
        db: Session,
        user_id: int | None,
        event_type: str,
        event_description: str | None = None,
        success: bool = True,
        ip_address: str | None = None,
        user_agent: str | None = None,
        endpoint: str | None = None,
        error_message: str | None = None,
        metadata: dict | None = None,
    ) -> None:
        """Persist an audit log event."""
        audit_log = AuditLog(
            user_id=user_id,
            event_type=event_type,
            event_description=event_description,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            error_message=error_message,
            metadata=str(metadata) if metadata else None,
        )
        db.add(audit_log)
        db.commit()


# Global instance
auth_service = AuthService()
