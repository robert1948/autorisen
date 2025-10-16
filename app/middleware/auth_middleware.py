# backend/app/middleware/auth_middleware.py
"""
Authentication Middleware for CapeControl
=====================================

Enhanced middleware for handling authentication with proper logout support.
"""

import logging
from datetime import datetime

from fastapi import Request, status
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.database import get_db
from app.models_enhanced import Token

logger = logging.getLogger(__name__)

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware to handle token validation and automatic logout"""
    
    def __init__(self, app):
        super().__init__(app)
        self.security = HTTPBearer()
        
        # Endpoints that don't require authentication
        self.public_endpoints = {
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/auth/v2/register",
            "/api/auth/v2/login",
            "/api/auth/v2/validate-email",
            "/api/auth/v2/validate-password",
            "/api/auth/v2/reset-password",
            "/api/status"
        }
    
    async def dispatch(self, request: Request, call_next):
        # Skip authentication for public endpoints
        if any(request.url.path.startswith(endpoint) for endpoint in self.public_endpoints):
            return await call_next(request)
        
        # Check for Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return await call_next(request)
        
        token = auth_header.split(" ")[1]
        
        # Validate token in database
        db = next(get_db())
        try:
            db_token = db.query(Token).filter(
                Token.token == token,
                Token.token_type == "access",
                Token.is_revoked == False,
                Token.expires_at > datetime.utcnow()
            ).first()
            
            if not db_token:
                # Token is invalid, revoked, or expired
                logger.warning(f"Invalid token used: {token[:20]}...")
                
                # Force client logout by returning 401
                return Response(
                    content='{"detail": "Token invalid or expired", "logout_required": true}',
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    headers={
                        "Content-Type": "application/json",
                        "WWW-Authenticate": "Bearer",
                        "X-Logout-Required": "true"
                    }
                )
            
            # Update token last used timestamp
            db_token.used_at = datetime.utcnow()
            db.commit()
            
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return Response(
                content='{"detail": "Authentication failed"}',
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Bearer"}
            )
        finally:
            db.close()
        
        return await call_next(request)


def handle_logout_required_response():
    """Handler for frontend to detect logout requirement"""
    pass
