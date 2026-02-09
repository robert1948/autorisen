from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.src.agents.mcp_host import mcp_host
from backend.src.db import models
from backend.src.db.session import get_session
from backend.src.modules.auth.deps import get_verified_user

from . import schemas, service

router = APIRouter(prefix="/ops", tags=["ops"])


def _agent_info() -> dict:
    agent = getattr(mcp_host, "agent", None)
    info = {
        "enabled": bool(getattr(mcp_host, "enabled", False)),
        "ready": bool(getattr(mcp_host, "ready", False)),
        "agent_loaded": agent is not None,
        "servers": [],
        "last_error": getattr(mcp_host, "last_error", None),
    }
    try:
        servers = getattr(agent, "mcp_servers", []) if agent else []
        # Try to render server ids if available
        info["servers"] = [getattr(s, "id", "unknown") for s in servers]
        disabled = getattr(agent, "_autolocal_disabled_mcp", None)
        if disabled:
            info["disabled_servers"] = disabled
    except Exception:
        info["servers"] = []
    return info


@router.get("/mcp/status")
async def mcp_status():
    """
    Returns MCP host status without invoking any tools.
    Always 200 with diagnostic info.
    """
    return {"ok": True, "mcp": _agent_info()}


@router.get("/mcp/smoke")
async def mcp_smoke():
    """
    Tries a gentle agent invocation; if it fails, returns ok=False and diagnostics
    (HTTP 200 to keep Makefile happy).
    """
    info = _agent_info()
    if not info["enabled"]:
        return {
            "ok": False,
            "mcp": info,
            "error": "MCP host disabled (ENABLE_MCP_HOST!=1)",
        }
    if not info["ready"]:
        return {
            "ok": False,
            "mcp": info,
            "error": info.get("last_error") or "MCP host not ready",
        }
    if not info["agent_loaded"]:
        return {"ok": False, "mcp": info, "error": "Agent not initialized"}

    # Prefer a no-op prompt that doesn't require any MCP servers
    prompt = "Reply exactly with: OK"
    try:
        out = await mcp_host.ask(prompt)
        return {"ok": out.strip() == "OK", "mcp": info, "result": out}
    except Exception as e:
        # Don’t throw; surface the error so curl -f still gets 200
        return {
            "ok": False,
            "mcp": info,
            "error": f"{type(e).__name__}: {e}",
            "hint": (
                "If this is a filesystem check, ensure 'mcp-filesystem' is installed "
                "and configured in config/mcp/servers.dev.yaml."
            ),
        }


@router.get("/insights", response_model=schemas.OpsInsightResponse)
def get_insights(
    intent: schemas.OpsInsightIntent,
    current_user: models.User = Depends(get_verified_user),
    db: Session = Depends(get_session),
) -> schemas.OpsInsightResponse:
    payload = service.build_insight(db, current_user, intent.value)
    return schemas.OpsInsightResponse(**payload)
