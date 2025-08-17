"""Rate Limiting Middleware"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from collections import defaultdict
import time

class RateLimitingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old requests (older than 1 minute)
        self.request_counts[client_ip] = [
            req_time for req_time in self.request_counts[client_ip]
            if current_time - req_time < 60
        ]
        
        # Check if rate limit exceeded
        if len(self.request_counts[client_ip]) >= self.requests_per_minute:
            from fastapi import HTTPException
            from starlette.responses import JSONResponse
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again later."}
            )
        
        # Record current request
        self.request_counts[client_ip].append(current_time)
        
        response: Response = await call_next(request)
        return response

# Backwards compatibility
RateLimitMiddleware = RateLimitingMiddleware
