"""
Core authentication module for CapeControl API
Centralized authentication and authorization utilities
"""

import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
from app.config import settings

logger = logging.getLogger(__name__)

# JWT Configuration
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

security = HTTPBearer()

class AuthenticationError(HTTPException):
    """Custom authentication error"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

class AuthorizationError(HTTPException):
    """Custom authorization error"""
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Token creation error: {e}")
        raise AuthenticationError("Failed to create access token")

def verify_token(token: str) -> Dict[str, Any]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise AuthenticationError("Invalid token payload")
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.JWTError as e:
        logger.error(f"JWT verification error: {e}")
        raise AuthenticationError("Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Get current user from JWT token
    This is the main function that routes are importing
    """
    try:
        token = credentials.credentials
        payload = verify_token(token)
        
        # Extract user information from token
        user_data = {
            "user_id": payload.get("user_id"),
            "username": payload.get("sub"),
            "email": payload.get("email"),
            "role": payload.get("role", "user"),
            "permissions": payload.get("permissions", []),
            "is_active": payload.get("is_active", True),
            "exp": payload.get("exp")
        }
        
        # Validate required fields
        if not user_data["user_id"] or not user_data["username"]:
            raise AuthenticationError("Invalid user data in token")
        
        logger.info(f"Authenticated user: {user_data['username']}")
        return user_data
        
    except AuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise AuthenticationError("Authentication failed")

async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Get current active user (extends get_current_user)"""
    if not current_user.get("is_active", False):
        raise AuthenticationError("User account is inactive")
    return current_user

async def require_role(required_role: str):
    """Dependency to require specific role"""
    async def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_role = current_user.get("role", "user")
        if user_role != required_role and user_role != "admin":  # Admin can access everything
            raise AuthorizationError(f"Role '{required_role}' required")
        return current_user
    return role_checker

async def require_permission(required_permission: str):
    """Dependency to require specific permission"""
    async def permission_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        permissions = current_user.get("permissions", [])
        if required_permission not in permissions and "admin" not in permissions:
            raise AuthorizationError(f"Permission '{required_permission}' required")
        return current_user
    return permission_checker

# Additional utility functions
def hash_password(password: str) -> str:
    """Hash password (placeholder - implement proper hashing)"""
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password (placeholder - implement proper verification)"""
    return hash_password(plain_password) == hashed_password

def get_user_permissions(user_role: str) -> list:
    """Get permissions based on user role"""
    role_permissions = {
        "admin": ["read", "write", "delete", "manage_users", "view_analytics"],
        "manager": ["read", "write", "view_analytics"],
        "user": ["read"],
        "viewer": ["read"]
    }
    return role_permissions.get(user_role, ["read"])

# Export all functions
__all__ = [
    "get_current_user",
    "get_current_active_user", 
    "require_role",
    "require_permission",
    "create_access_token",
    "verify_token",
    "hash_password",
    "verify_password",
    "get_user_permissions",
    "AuthenticationError",
    "AuthorizationError"
]