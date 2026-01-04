"""
CapeAI Domain Specialist router.

Provides HTTP endpoints for interacting with the domain-specific agent.
"""

import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, WebSocket
from sqlalchemy.orm import Session

from backend.src.core.config import get_settings
from backend.src.db.session import get_session
from backend.src.modules.auth.deps import get_verified_user as get_current_user
from backend.src.db import models
from backend.src.db.models import Task, User
from ..executor import AgentExecutor, TaskCreate, TaskResponse
from .schemas import DomainSpecialistTaskInput, DomainSpecialistTaskOutput
from .service import DomainSpecialistService

router = APIRouter(
    prefix="/cape-ai-domain-specialist",
    tags=["CapeAI Domain Specialist"],
)

_service: Optional[DomainSpecialistService] = None


def get_domain_service() -> DomainSpecialistService:
    """Lazy-init the domain specialist service."""
    global _service
    if _service is None:
        settings = get_settings()

        _service = DomainSpecialistService(
            openai_api_key=settings.openai_api_key,
            anthropic_api_key=settings.anthropic_api_key,
            model=os.getenv("CAPE_AI_DOMAIN_MODEL", "claude-3-5-haiku-20241022"),
        )
    return _service


@router.post("/ask", response_model=TaskResponse)
async def ask_domain_specialist(
    input_data: DomainSpecialistTaskInput,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    service: DomainSpecialistService = Depends(get_domain_service),
):
    """Execute a domain-specialized task by enqueuing it in the agent executor."""
    task_data = TaskCreate(
        agent_id="cape-ai-domain-specialist",
        goal=f"Domain Specialist ({input_data.domain})",
        input=input_data.dict(),
        user_id=current_user.id,
    )

    executor = AgentExecutor(db)

    # Call the service directly before persisting the result
    result: DomainSpecialistTaskOutput = await service.process_task(
        input_data, db=db, user=current_user
    )
    task_result = await executor.execute_task(task_data)

    # Persist real result payload
    db.query(models.Task).filter(models.Task.id == task_result.id).update(
        {"result": result.dict()}
    )
    db.commit()
    task_result.result = result.dict()
    return task_result


@router.websocket("/stream/{task_id}")
async def stream_domain_specialist_task(
    websocket: WebSocket, task_id: str, db: Session = Depends(get_session)
):
    """Stream updates for a domain specialist task."""
    await websocket.accept()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            await websocket.send_json({"error": "Task not found", "task_id": task_id})
            await websocket.close(code=4004)
            return

        executor = AgentExecutor(db)
        await executor.execute_task(
            TaskCreate(
                agent_id=task.agent_id,
                goal=task.goal or "",
                input=task.input or {},
                user_id=task.user_id,
            ),
            websocket,
        )

    except Exception as exc:
        await websocket.send_json({"error": str(exc), "task_id": task_id})
    finally:
        await websocket.close()


@router.get("/health")
async def domain_specialist_health(
    service: DomainSpecialistService = Depends(get_domain_service),
):
    """Health check endpoint for the Domain Specialist agent."""
    try:
        return {
            "status": "healthy",
            "agent": "cape-ai-domain-specialist",
            "model": service.model,
            "domains": [
                "workflow_automation",
                "data_analytics",
                "security_audit",
                "integration_helper",
            ],
            "timestamp": "2025-11-11T06:35:00Z",
        }
    except Exception as exc:
        return {
            "status": "unhealthy",
            "error": str(exc),
            "timestamp": "2025-11-11T06:35:00Z",
        }


@router.get("/capabilities")
async def domain_specialist_capabilities():
    """Get information about Domain Specialist agent capabilities."""
    return {
        "agent_id": "cape-ai-domain-specialist",
        "name": "CapeAI Domain Specialist",
        "description": "Specialized agent for domain-specific technical assistance",
        "domains": [
            "workflow_automation",
            "data_analytics",
            "security_audit",
            "integration_helper",
        ],
        "capabilities": {
            "workflow_automation": [
                "Trigger validation",
                "Rollback planning",
                "Run observability",
            ],
            "data_analytics": [
                "Semantic layer governance",
                "Dashboard tuning",
                "Pipeline SLA advisory",
            ],
            "security_audit": [
                "Control validation",
                "Evidence orchestration",
                "Risk register updates",
            ],
            "integration_helper": [
                "Partner API onboarding",
                "Webhook hygiene",
                "Credential rotation strategy",
            ],
        },
        "supported_formats": ["text", "code", "json", "markdown"],
        "response_time": "< 5 seconds",
        "supports_streaming": True,
    }
