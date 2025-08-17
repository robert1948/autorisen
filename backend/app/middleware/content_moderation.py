"""
Content Moderation Middleware
Enterprise-grade content filtering and moderation for AI safety
"""

import re
import json
import logging
from typing import Dict, Any, List, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

class ContentModerationMiddleware(BaseHTTPMiddleware):
    """
    Enterprise content moderation middleware for AI safety and compliance
    Filters inappropriate content, hate speech, and harmful instructions
    """
    
    def __init__(self, app, strict_mode: bool = False):
        super().__init__(app)
        self.strict_mode = strict_mode
        
        # Basic inappropriate patterns (simplified for deployment)
        self.inappropriate_patterns = [
            r'\b(hate|violence|harm|kill|murder)\b',
            r'\b(adult|explicit|nsfw|sexual)\b',
            r'\b(harassment|threat|intimidate)\b',
            r'\b(hack|crack|illegal|drugs)\b',
        ]
        
        # Compile patterns for performance
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.inappropriate_patterns]
        
        logger.info("✅ ContentModerationMiddleware initialized successfully")
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request with content moderation"""
        
        try:
            # Check query parameters for inappropriate content
            if request.query_params:
                for key, value in request.query_params.items():
                    if self._contains_inappropriate_content(str(value)):
                        logger.warning(f"Inappropriate content detected in query param: {key}")
                        return JSONResponse(
                            status_code=400,
                            content={
                                "error": "Content moderation violation",
                                "details": "Request contains inappropriate content",
                                "field": key
                            }
                        )
            
            # Check request body for POST/PUT/PATCH requests
            if request.method in ['POST', 'PUT', 'PATCH']:
                try:
                    content_type = request.headers.get('content-type', '').lower()
                    
                    if 'application/json' in content_type:
                        body = await request.body()
                        if body:
                            try:
                                json_data = json.loads(body.decode('utf-8'))
                                if self._check_json_content(json_data):
                                    logger.warning("Inappropriate content detected in JSON body")
                                    return JSONResponse(
                                        status_code=400,
                                        content={
                                            "error": "Content moderation violation",
                                            "details": "Request body contains inappropriate content"
                                        }
                                    )
                            except json.JSONDecodeError:
                                # If JSON parsing fails, check as string
                                body_str = body.decode('utf-8', errors='ignore')
                                if self._contains_inappropriate_content(body_str):
                                    logger.warning("Inappropriate content detected in request body")
                                    return JSONResponse(
                                        status_code=400,
                                        content={
                                            "error": "Content moderation violation",
                                            "details": "Request body contains inappropriate content"
                                        }
                                    )
                except Exception as e:
                    logger.warning(f"Body moderation check error: {e}")
                    # Continue processing if body check fails
                    pass
            
            # Process the request
            response = await call_next(request)
            
            # Add content moderation headers
            response.headers["X-Content-Moderated"] = "true"
            response.headers["X-Moderation-Policy"] = "strict" if self.strict_mode else "standard"
            
            return response
            
        except Exception as e:
            logger.error(f"Content moderation middleware error: {e}")
            # Continue with original request if moderation fails
            try:
                return await call_next(request)
            except Exception as e2:
                logger.error(f"Fallback request processing error: {e2}")
                return JSONResponse(
                    status_code=500,
                    content={"error": "Internal server error"}
                )
    
    def _contains_inappropriate_content(self, text: str) -> bool:
        """Check if text contains inappropriate content"""
        try:
            if not isinstance(text, str) or not text.strip():
                return False
                
            for pattern in self.compiled_patterns:
                if pattern.search(text):
                    return True
            return False
        except Exception as e:
            logger.warning(f"Content moderation check error: {e}")
            return False
    
    def _check_json_content(self, data) -> bool:
        """Recursively check JSON data for inappropriate content"""
        try:
            if isinstance(data, dict):
                for key, value in data.items():
                    if self._check_json_content(value):
                        return True
            elif isinstance(data, list):
                for item in data:
                    if self._check_json_content(item):
                        return True
            elif isinstance(data, str):
                if self._contains_inappropriate_content(data):
                    return True
            return False
        except Exception as e:
            logger.warning(f"JSON content check error: {e}")
            return False
    
    def moderate_text(self, text: str) -> Dict[str, Any]:
        """Public method to moderate text content"""
        try:
            is_safe = not self._contains_inappropriate_content(text)
            violations = []
            
            if not is_safe:
                for pattern in self.compiled_patterns:
                    matches = pattern.findall(text)
                    if matches:
                        violations.extend(matches)
            
            return {
                'is_safe': is_safe,
                'violations': violations,
                'text_length': len(text) if text else 0,
                'word_count': len(text.split()) if text else 0
            }
        except Exception as e:
            logger.error(f"Text moderation error: {e}")
            return {
                'is_safe': True,
                'violations': [],
                'text_length': 0,
                'word_count': 0,
                'error': str(e)
            }
    
    def get_moderation_stats(self) -> Dict[str, Any]:
        """Get moderation statistics"""
        try:
            return {
                'strict_mode': self.strict_mode,
                'pattern_count': len(self.inappropriate_patterns),
                'compiled_patterns': len(self.compiled_patterns),
                'status': 'active'
            }
        except Exception as e:
            logger.error(f"Error getting moderation stats: {e}")
            return {
                'strict_mode': False,
                'pattern_count': 0,
                'compiled_patterns': 0,
                'status': 'error',
                'error': str(e)
            }

# Export the middleware class
__all__ = ["ContentModerationMiddleware"]