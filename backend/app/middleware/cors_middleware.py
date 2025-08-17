"""CORS Middleware"""
from starlette.middleware.base import BaseHTTPMiddleware

class CORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        return response
