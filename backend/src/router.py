# backend/src/api.py

from src.routes.api.developer import router as developer_router
from src.routes.api.user import router as user_router

# Optionally, group them under a FastAPI APIRouter here if you're combining them
from fastapi import APIRouter

router = APIRouter()
router.include_router(
    developer_router, prefix="/developer", tags=["Developer"])
router.include_router(user_router, prefix="/user", tags=["User"])
