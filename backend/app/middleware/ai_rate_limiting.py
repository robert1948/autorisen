"""AI Rate Limiting Middleware"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from collections import defaultdict
import time

class AIRateLimitingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, ai_requests_per_minute: int = 20):
        super().__init__(app)
        self.ai_requests_per_minute = ai_requests_per_minute
        self.ai_request_counts = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # Check if this is an AI-related endpoint
        if "/ai/" in str(request.url) or "/chat/" in str(request.url):
            client_ip = request.client.host
            current_time = time.time()
            
            # Clean old requests (older than 1 minute)
            self.ai_request_counts[client_ip] = [
                req_time for req_time in self.ai_request_counts[client_ip]
                if current_time - req_time < 60
            ]
            
            # Check if AI rate limit exceeded
            if len(self.ai_request_counts[client_ip]) >= self.ai_requests_per_minute:
                from starlette.responses import JSONResponse
                return JSONResponse(
                    status_code=429,
                    content={"detail": "AI rate limit exceeded. Please wait before making more AI requests."}
                )
            
            # Record current AI request
            self.ai_request_counts[client_ip].append(current_time)
        
        response = await call_next(request)
        return response
