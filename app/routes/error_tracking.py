"""Error_tracking Routes"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def error_tracking_root():
    return {"message": "error_tracking endpoint"}
