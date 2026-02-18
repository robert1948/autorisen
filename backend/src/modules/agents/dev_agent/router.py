"""
Dev Agent Router

FastAPI router providing endpoints for the Dev Agent.
Assists developers with building, testing, and publishing AI agents.
"""

import os
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.src.core.config import get_settings
from backend.src.db.session import get_session
from backend.src.modules.auth.deps import get_verified_user as get_current_user
from backend.src.db.models import User
from .schemas import DevAgentTaskInput, DevAgentTaskOutput
from .service import DevAgentService

router = APIRouter(prefix="/dev-agent", tags=["Dev Agent"])

_service = None


def get_dev_agent_service() -> DevAgentService:
    """Get or create Dev Agent service instance."""
    global _service
    if _service is None:
        settings = get_settings()
        _service = DevAgentService(
            openai_api_key=settings.openai_api_key,
            anthropic_api_key=settings.anthropic_api_key,
            model=os.getenv("DEV_AGENT_MODEL", "claude-3-5-haiku-20241022"),
        )
    return _service


@router.post("/ask", response_model=DevAgentTaskOutput)
async def ask_dev_agent(
    input_data: DevAgentTaskInput,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    service: DevAgentService = Depends(get_dev_agent_service),
):
    """
    Submit a query to the Dev Agent.

    The agent helps developers build, test, debug, and publish AI agents
    on the CapeControl platform.
    """
    try:
        result = await service.process_query(input_data, db=db, user=current_user)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        )


@router.get("/health")
async def dev_agent_health():
    """Health check endpoint for the Dev Agent."""
    return {
        "status": "healthy",
        "agent": "dev-agent",
        "model": os.getenv("DEV_AGENT_MODEL", "claude-3-5-haiku-20241022"),
        "knowledge_base": "operational",
        "capabilities": [
            "agent_building",
            "code_review",
            "debugging",
            "testing",
            "publishing",
        ],
    }


@router.get("/capabilities")
async def dev_agent_capabilities():
    """Get information about Dev Agent capabilities."""
    return {
        "agent_id": "dev-agent",
        "name": "Dev Agent",
        "description": "Expert AI assistant for building and deploying agents on CapeControl",
        "capabilities": [
            "Agent architecture guidance",
            "Code generation and review",
            "LLM integration patterns",
            "Tool calling implementation",
            "Test writing and debugging",
            "Marketplace publishing",
            "Performance optimization",
        ],
        "supported_task_types": [
            "general",
            "build",
            "test",
            "debug",
            "publish",
            "optimize",
            "review",
        ],
    }
