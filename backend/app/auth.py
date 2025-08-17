# backend/app/auth.py

from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from typing import Optional, Dict, Any

import bcrypt

# Try to use bcrypt directly if passlib has issues
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    USE_PASSLIB = True
except Exception as e:
    print(f"⚠️ Passlib bcrypt issue detected: {e}")
    USE_PASSLIB = False

# Security scheme for Bearer token authentication
security = HTTPBearer()

def get_password_hash(password: str) -> str:
    """Hash password with fallback for bcrypt version issues"""
    if USE_PASSLIB:
        try:
            return pwd_context.hash(password)
        except Exception as e:
            print(f"⚠️ Passlib hash failed, using bcrypt directly: {e}")
    
    # Fallback to direct bcrypt usage
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password with fallback for bcrypt version issues"""
    if USE_PASSLIB:
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            print(f"⚠️ Passlib verify failed, using bcrypt directly: {e}")
    
    # Fallback to direct bcrypt usage
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        # If that fails, try the original passlib method as last resort
        return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, secret_key: str, algorithm: str, expires_delta: timedelta = timedelta(minutes=30)):
    """Create JWT access token with expiration"""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify JWT token and return payload (helper function).
    
    Args:
        token: JWT token string to verify
        
    Returns:
        Token payload if valid, None if invalid
    """
    try:
        from app.core.settings import get_settings
        settings = get_settings()
        
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # Check expiration
        exp = payload.get("exp")
        if exp:
            now_ts = datetime.utcnow().timestamp()
            if isinstance(exp, datetime):
                exp_ts = exp.timestamp()
            else:
                exp_ts = float(exp)
            if now_ts > exp_ts:
                return None
                
        return payload
    except Exception:
        return None

async def get_current_user(token: str = Depends(security)) -> Dict[str, Any]:
    """
    Get current user from JWT token for route authentication.
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        User information decoded from token
        
    Raises:
        HTTPException: If token is invalid, expired, or malformed
    """
    try:
        # Extract token from Bearer format
        if hasattr(token, 'credentials'):
            token_str = token.credentials
        else:
            token_str = str(token)
        
        # Get settings for JWT configuration
        from app.core.settings import get_settings
        settings = get_settings()
        
        # Decode and verify JWT token
        try:
            payload = jwt.decode(
                token_str, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            
            # Check if token has expired
            exp = payload.get("exp")
            if exp is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token missing expiration",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Verify expiration
            now_ts = datetime.utcnow().timestamp()
            # exp can be int (timestamp) or datetime
            if isinstance(exp, datetime):
                exp_ts = exp.timestamp()
            else:
                exp_ts = float(exp)
            if now_ts > exp_ts:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Extract user information
            user_id = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token missing user identifier",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Return user data from token
            return {
                "user_id": user_id,
                "username": payload.get("username"),
                "email": payload.get("email"),
                "exp": exp,
                "iat": payload.get("iat"),
                "token_type": payload.get("token_type", "access")
            }
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token validation failed: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Handle any other unexpected errors
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user_optional(token: Optional[str] = Depends(security)) -> Optional[Dict[str, Any]]:
    """
    Get current user from JWT token, but don't raise exception if token is missing.
    Used for optional authentication endpoints.
    
    Args:
        token: Optional JWT token from Authorization header
        
    Returns:
        User information if token is valid, None if missing or invalid
    """
    if not token:
        return None
        
    try:
        # Use the token verification logic without raising exceptions
        if hasattr(token, 'credentials'):
            token_str = token.credentials
        else:
            token_str = str(token)
            
        return verify_token(token_str)
    except Exception:
        return None