# backend/src/routes/__init__.py

from fastapi import APIRouter
from src.routes.developer import router as developer_router
from src.routes.user import router as user_router

router = APIRouter()

# Mount developer and user routes to /api prefix
router.include_router(developer_router)
router.include_router(user_router)
