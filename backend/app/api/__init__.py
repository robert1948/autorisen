# backend/app/api/__init__.py
from fastapi import APIRouter

# Import individual route modules
# Import individual routers
from app.api.agents import router as agents_router, alias_router

# from app.api import auth, dashboard, monitoring, etc.

# Create a top-level router to aggregate all
api_router = APIRouter()

# Mount routers
api_router.include_router(agents_router)  # /api/v1/agents/*
api_router.include_router(alias_router)  # /api/agents/* (dev alias)
