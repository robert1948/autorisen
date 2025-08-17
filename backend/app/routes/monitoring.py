"""Monitoring Routes"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def monitoring_root():
    return {"message": "monitoring endpoint"}
