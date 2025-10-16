"""
Input Sanitization Middleware
Enterprise-grade input validation and sanitization for security
"""

import html
import json
import logging
import re
from typing import Any

import bleach
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """
    Enterprise input sanitization middleware for security protection
    Handles XSS prevention, SQL injection protection, and input validation
    """
    
    def __init__(self, app, max_content_length: int = 10 * 1024 * 1024):  # 10MB default
        super().__init__(app)
        self.max_content_length = max_content_length
        
        # Rate limiting tracking (simple in-memory for now)
        self._request_counts = {}
        self._blocked_ips = set()
        
        # Performance monitoring
        self._request_counter = 0
        self._security_checks_performed = 0
        self._threats_blocked = 0
        
        # Define dangerous patterns
        self.sql_injection_patterns = [
            r'(\bunion\b.*\bselect\b)',
            r'(\bselect\b.*\bfrom\b)',
            r'(\binsert\b.*\binto\b)',
            r'(\bupdate\b.*\bset\b)',
            r'(\bdelete\b.*\bfrom\b)',
            r'(\bdrop\b.*\btable\b)',
            r'(\balter\b.*\btable\b)',
            r'(--|\#|\/\*)',
            r'(\bor\b.*=.*\bor\b)',
            r'(\band\b.*=.*\band\b)',
            r'(\'.*\bor\b.*\')',
            r'(\".*\bor\b.*\")',
        ]
        
        # XSS patterns
        self.xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>.*?</iframe>',
            r'<object[^>]*>.*?</object>',
            r'<embed[^>]*>.*?</embed>',
            r'<link[^>]*>',
            r'<meta[^>]*>',
        ]
        
        # Compile patterns for performance
        self.compiled_sql_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.sql_injection_patterns]
        self.compiled_xss_patterns = [re.compile(pattern, re.IGNORECASE | re.DOTALL) for pattern in self.xss_patterns]
        
        # Allowed HTML tags and attributes for bleach
        self.allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
        self.allowed_attributes = {
            '*': ['class', 'id'],
            'a': ['href', 'title'],
            'img': ['src', 'alt', 'width', 'height'],
        }
        
        logger.info("✅ InputSanitizationMiddleware initialized with performance monitoring")
    
    def get_security_stats(self) -> dict[str, Any]:
        """Get security middleware performance statistics"""
        return {
            "requests_processed": self._request_counter,
            "security_checks_performed": self._security_checks_performed,
            "threats_blocked": self._threats_blocked,
            "blocked_ips_count": len(self._blocked_ips),
            "tracked_ips_count": len(self._request_counts)
        }
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request with comprehensive input sanitization"""
        
        try:
            # TEMPORARY: Skip sanitization for auth endpoints to debug timeout issue
            if request.url.path.startswith('/api/auth/'):
                logger.info(f"⚡ Bypassing input sanitization for auth endpoint: {request.url.path}")
                return await call_next(request)
            
            # Increment request counter for monitoring
            self._request_counter += 1
            
            # Get client IP for tracking
            client_ip = self._get_client_ip(request)
            
            # Check if IP is blocked
            if client_ip in self._blocked_ips:
                logger.warning(f"Blocked request from IP: {client_ip}")
                self._threats_blocked += 1
                return JSONResponse(
                    status_code=403,
                    content={"error": "Access denied", "details": "IP temporarily blocked"}
                )
            
            # Check content length
            if hasattr(request, 'headers') and 'content-length' in request.headers:
                content_length = int(request.headers.get('content-length', 0))
                if content_length > self.max_content_length:
                    logger.warning(f"Request content too large: {content_length} bytes")
                    return JSONResponse(
                        status_code=413,
                        content={"error": "Request entity too large", "max_size": self.max_content_length}
                    )
            
            # Sanitize query parameters
            if request.query_params:
                self._security_checks_performed += 1
                sanitized_query = self._sanitize_query_params(dict(request.query_params))
                if not sanitized_query['is_safe']:
                    self._track_malicious_request(client_ip, "query_params")
                    self._threats_blocked += 1
                    logger.warning(f"Malicious query parameters detected from {client_ip}: {sanitized_query['threats']}")
                    return JSONResponse(
                        status_code=400,
                        content={
                            "error": "Invalid input detected",
                            "details": "Query parameters contain potentially malicious content",
                            "threats": sanitized_query['threats']
                        }
                    )
            
            # Sanitize request body for POST/PUT/PATCH requests
            if request.method in ['POST', 'PUT', 'PATCH']:
                try:
                    # Get content type
                    content_type = request.headers.get('content-type', '').lower()
                    
                    if 'application/json' in content_type:
                        # Read and sanitize JSON body
                        body = await request.body()
                        if body:
                            self._security_checks_performed += 1
                            sanitized_body = await self._sanitize_json_body(body)
                            if not sanitized_body['is_safe']:
                                self._track_malicious_request(client_ip, "json_body")
                                self._threats_blocked += 1
                                logger.warning(f"Malicious JSON body detected from {client_ip}: {sanitized_body['threats']}")
                                return JSONResponse(
                                    status_code=400,
                                    content={
                                        "error": "Invalid input detected",
                                        "details": "Request body contains potentially malicious content",
                                        "threats": sanitized_body['threats']
                                    }
                                )
                    
                    elif 'application/x-www-form-urlencoded' in content_type:
                        # Handle form data
                        try:
                            self._security_checks_performed += 1
                            form_data = await request.form()
                            sanitized_form = self._sanitize_form_data(dict(form_data))
                            if not sanitized_form['is_safe']:
                                self._track_malicious_request(client_ip, "form_data")
                                self._threats_blocked += 1
                                logger.warning(f"Malicious form data detected from {client_ip}: {sanitized_form['threats']}")
                                return JSONResponse(
                                    status_code=400,
                                    content={
                                        "error": "Invalid input detected",
                                        "details": "Form data contains potentially malicious content",
                                        "threats": sanitized_form['threats']
                                    }
                                )
                        except Exception as e:
                            logger.warning(f"Form data processing error: {e}")
                
                except Exception as e:
                    logger.error(f"Body sanitization error: {e}")
                    # Continue processing if sanitization fails
                    pass
            
            # Process the request
            response = await call_next(request)
            
            # Periodic cleanup to prevent memory bloat (every 1000 requests)
            if self._request_counter % 1000 == 0:
                self._cleanup_old_tracking_data()
            
            # Add security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
                "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; "
                "img-src 'self' data: https: blob: https://lightning-s3.s3.amazonaws.com https://lightning-s3.s3.us-east-1.amazonaws.com; "
                "connect-src 'self' "
                "https://www.cape-control.com https://cape-control.com https://capecraft.herokuapp.com "
                "https://api.openai.com https://api.anthropic.com https://generativelanguage.googleapis.com "
                "wss: https:; "
                "manifest-src 'self'; "
                "worker-src 'self' blob:; "
                "child-src 'self' blob:; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "form-action 'self'; "
                "frame-ancestors 'none'"
            )
            
            # Additional production security headers
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=(), payment=(), usb=(), magnetometer=(), gyroscope=()"
            response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
            
            return response
            
        except Exception as e:
            logger.error(f"Input sanitization middleware error: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error", "details": "Input processing failed"}
            )
    
    def _sanitize_query_params(self, params: dict[str, Any]) -> dict[str, Any]:
        """Sanitize query parameters"""
        threats = []
        
        for key, value in params.items():
            str_value = str(value)
            
            # Check for SQL injection (performance optimized)
            if self._detect_sql_injection_fast(str_value):
                threats.append(f"SQL injection in query param '{key}'")
            
            # Check for XSS
            if self._detect_xss(str_value):
                threats.append(f"XSS attempt in query param '{key}'")
            
            # Check for path traversal
            if self._detect_path_traversal(str_value):
                threats.append(f"Path traversal in query param '{key}'")
        
        return {
            'is_safe': len(threats) == 0,
            'threats': threats
        }
    
    async def _sanitize_json_body(self, body: bytes) -> dict[str, Any]:
        """Sanitize JSON request body"""
        threats = []
        
        try:
            # Parse JSON
            json_data = json.loads(body.decode('utf-8'))
            
            # Recursively check JSON values
            threats.extend(self._check_json_recursively(json_data, "body"))
            
        except json.JSONDecodeError:
            # Not valid JSON, treat as string
            body_str = body.decode('utf-8', errors='ignore')
            if self._detect_sql_injection(body_str):
                threats.append("SQL injection in request body")
            if self._detect_xss(body_str):
                threats.append("XSS attempt in request body")
        except Exception as e:
            logger.warning(f"JSON sanitization error: {e}")
        
        return {
            'is_safe': len(threats) == 0,
            'threats': threats
        }
    
    def _sanitize_form_data(self, form_data: dict[str, Any]) -> dict[str, Any]:
        """Sanitize form data"""
        threats = []
        
        for key, value in form_data.items():
            str_value = str(value)
            
            # Check for SQL injection (performance optimized)
            if self._detect_sql_injection_fast(str_value):
                threats.append(f"SQL injection in form field '{key}'")
            
            # Check for XSS
            if self._detect_xss(str_value):
                threats.append(f"XSS attempt in form field '{key}'")
            
            # Check for path traversal
            if self._detect_path_traversal(str_value):
                threats.append(f"Path traversal in form field '{key}'")
        
        return {
            'is_safe': len(threats) == 0,
            'threats': threats
        }
    
    def _check_json_recursively(self, data: Any, path: str) -> list[str]:
        """Recursively check JSON data for threats"""
        threats = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}"
                threats.extend(self._check_json_recursively(value, current_path))
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                threats.extend(self._check_json_recursively(item, current_path))
        
        elif isinstance(data, str):
            # Check string values (performance optimized)
            if self._detect_sql_injection_fast(data):
                threats.append(f"SQL injection in {path}")
            if self._detect_xss(data):
                threats.append(f"XSS attempt in {path}")
            if self._detect_path_traversal(data):
                threats.append(f"Path traversal in {path}")
        
        return threats
    
    def _detect_sql_injection(self, text: str) -> bool:
        """Detect SQL injection patterns"""
        for pattern in self.compiled_sql_patterns:
            if pattern.search(text):
                return True
        return False
    
    def _detect_xss(self, text: str) -> bool:
        """Detect XSS patterns"""
        for pattern in self.compiled_xss_patterns:
            if pattern.search(text):
                return True
        return False
    
    def _detect_path_traversal(self, text: str) -> bool:
        """Detect path traversal attempts"""
        dangerous_patterns = ['../', '..\\', '%2e%2e%2f', '%2e%2e%5c', '....//']
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in dangerous_patterns)
    
    def sanitize_html(self, text: str) -> str:
        """Sanitize HTML content using bleach"""
        try:
            return bleach.clean(text, tags=self.allowed_tags, attributes=self.allowed_attributes)
        except Exception as e:
            logger.warning(f"HTML sanitization error: {e}")
            return html.escape(text)
    
    def sanitize_string(self, text: str) -> str:
        """Basic string sanitization"""
        if not isinstance(text, str):
            return str(text)
        
        # HTML escape
        text = html.escape(text)
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request headers (considering Cloudflare/Heroku proxies)"""
        # Check for Cloudflare connecting IP first
        if 'cf-connecting-ip' in request.headers:
            return request.headers['cf-connecting-ip']
        
        # Check for X-Forwarded-For (Heroku/proxy)
        if 'x-forwarded-for' in request.headers:
            forwarded_ips = request.headers['x-forwarded-for'].split(',')
            return forwarded_ips[0].strip()
        
        # Check for X-Real-IP
        if 'x-real-ip' in request.headers:
            return request.headers['x-real-ip']
        
        # Fallback to remote address
        return getattr(request.client, 'host', 'unknown')
    
    def _track_malicious_request(self, client_ip: str, threat_type: str):
        """Track malicious requests and potentially block repeat offenders"""
        if client_ip not in self._request_counts:
            self._request_counts[client_ip] = {'count': 0, 'threats': [], 'last_seen': None}
        
        import time
        self._request_counts[client_ip]['count'] += 1
        self._request_counts[client_ip]['threats'].append(threat_type)
        self._request_counts[client_ip]['last_seen'] = time.time()
        
        # Block IP if too many malicious requests (simple threshold)
        if self._request_counts[client_ip]['count'] >= 5:
            self._blocked_ips.add(client_ip)
            logger.warning(f"IP {client_ip} blocked due to repeated malicious requests")
    
    def _cleanup_old_tracking_data(self):
        """Clean up old tracking data to prevent memory bloat"""
        import time
        current_time = time.time()
        cleanup_threshold = 3600  # 1 hour
        
        # Remove old request tracking data
        old_ips = []
        for ip, data in self._request_counts.items():
            if data.get('last_seen') and (current_time - data['last_seen']) > cleanup_threshold:
                old_ips.append(ip)
        
        for ip in old_ips:
            del self._request_counts[ip]
            self._blocked_ips.discard(ip)
        
        if old_ips:
            logger.info(f"🧹 Cleaned up tracking data for {len(old_ips)} old IPs")
    
    def _detect_sql_injection_fast(self, text: str) -> bool:
        """Fast SQL injection detection for performance"""
        # Quick check for common SQL keywords (case-insensitive)
        text_lower = text.lower()
        
        # Most common patterns for quick rejection
        if any(keyword in text_lower for keyword in ['select ', 'union ', 'drop ', 'delete ', 'insert ', 'update ']):
            # Only run full regex if suspicious keywords found
            return self._detect_sql_injection(text)
        
        return False

# Export the middleware
__all__ = ["InputSanitizationMiddleware"]