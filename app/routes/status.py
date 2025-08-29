# backend/app/routes/status.py
from fastapi import APIRouter
from app.version import get_app_version, now_iso

router = APIRouter(prefix="/api", tags=["status"])

@router.get("/status")
def get_status():
    v = get_app_version()
    return {
        "ok": True,
        "service": "capecontrol-backend",
        "version": v.version,
        "git_sha": v.git_sha,
        "build_time": v.build_time,
        "environment": v.environment,
        "server_time": now_iso(),
    }
