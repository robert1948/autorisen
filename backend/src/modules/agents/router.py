"""Agent registry CRUD endpoints."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, WebSocket
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from backend.src.db import models
from backend.src.db.session import get_session
from backend.src.modules.auth.deps import get_verified_user as get_current_user

from . import schemas
from .executor import AgentExecutor, TaskCreate, TaskResponse

# Import CapeAI Guide router
try:
    from .cape_ai_guide.router import router as cape_ai_guide_router
except ImportError:
    cape_ai_guide_router = None

# Import Domain Specialist router
try:
    from .cape_ai_domain_specialist.router import (
        router as cape_ai_domain_specialist_router,
    )
except ImportError:
    cape_ai_domain_specialist_router = None

router = APIRouter(prefix="/agents", tags=["agents"])

# Include specialized agent routers
if cape_ai_guide_router:
    router.include_router(cape_ai_guide_router)
if cape_ai_domain_specialist_router:
    router.include_router(cape_ai_domain_specialist_router)


def _get_agent(db: Session, agent_id: str, owner: models.User) -> models.Agent:
    agent = db.scalar(
        select(models.Agent).where(
            models.Agent.id == agent_id, models.Agent.owner_id == owner.id
        )
    )
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="agent not found"
        )
    return agent


@router.get("", response_model=list[schemas.AgentResponse])
def list_agents(
    owner: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> list[schemas.AgentResponse]:
    agents = db.scalars(
        select(models.Agent).where(models.Agent.owner_id == owner.id)
    ).all()
    return list(agents)


@router.post(
    "", response_model=schemas.AgentResponse, status_code=status.HTTP_201_CREATED
)
def create_agent(
    payload: schemas.AgentCreate,
    owner: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> schemas.AgentResponse:
    existing = db.scalar(select(models.Agent).where(models.Agent.slug == payload.slug))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="slug already in use"
        )

    agent = models.Agent(
        owner_id=owner.id,
        slug=payload.slug,
        name=payload.name,
        description=payload.description,
        visibility=payload.visibility,
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


@router.patch("/{agent_id}", response_model=schemas.AgentResponse)
def update_agent(
    agent_id: str,
    payload: schemas.AgentUpdate,
    owner: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> schemas.AgentResponse:
    agent = _get_agent(db, agent_id, owner)

    if payload.name is not None:
        agent.name = payload.name
    if payload.description is not None:
        agent.description = payload.description
    if payload.visibility is not None:
        agent.visibility = payload.visibility

    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


@router.post(
    "/{agent_id}/versions",
    response_model=schemas.AgentVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_version(
    agent_id: str,
    payload: schemas.AgentVersionCreate,
    owner: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> schemas.AgentVersionResponse:
    agent = _get_agent(db, agent_id, owner)

    existing = db.scalar(
        select(models.AgentVersion).where(
            models.AgentVersion.agent_id == agent.id,
            models.AgentVersion.version == payload.version,
        )
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="version already exists"
        )

    version = models.AgentVersion(
        agent_id=agent.id,
        version=payload.version,
        manifest=payload.manifest,
        changelog=payload.changelog,
        status=payload.status,
    )
    if payload.status == "published":
        version.published_at = models.func.now()

    db.add(version)
    db.commit()
    db.refresh(version)
    return version


@router.post(
    "/{agent_id}/versions/{version_id}/publish",
    response_model=schemas.AgentVersionResponse,
)
def publish_version(
    agent_id: str,
    version_id: str,
    owner: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> schemas.AgentVersionResponse:
    agent = _get_agent(db, agent_id, owner)
    version = db.scalar(
        select(models.AgentVersion).where(
            models.AgentVersion.id == version_id,
            models.AgentVersion.agent_id == agent.id,
        )
    )
    if version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="version not found"
        )

    # Demote currently published versions for this agent.
    db.execute(
        update(models.AgentVersion)
        .where(
            models.AgentVersion.agent_id == agent.id,
            models.AgentVersion.status == "published",
        )
        .values(status="archived")
    )

    version.status = "published"
    version.published_at = datetime.now()
    db.add(version)
    db.commit()
    db.refresh(version)
    return version


@router.get("/{agent_id}", response_model=schemas.AgentResponse)
def get_agent(
    agent_id: str,
    owner: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> schemas.AgentResponse:
    agent = _get_agent(db, agent_id, owner)
    return agent


# Task execution endpoints
@router.post("/{agent_id}/tasks", response_model=TaskResponse)
async def create_task(
    agent_id: str,
    task_data: TaskCreate,
    owner: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> TaskResponse:
    """Execute an agent task."""

    # Verify agent exists and user has access
    _get_agent(db, agent_id, owner)

    # Set user_id from authenticated user
    task_data.user_id = owner.id
    task_data.agent_id = agent_id

    # Execute task
    executor = AgentExecutor(db)
    return await executor.execute_task(task_data)


@router.websocket("/{agent_id}/tasks/stream")
async def stream_task_execution(
    websocket: WebSocket,
    agent_id: str,
    db: Session = Depends(get_session),
):
    """Stream real-time task execution updates via WebSocket."""

    await websocket.accept()

    try:
        # Receive task data
        data = await websocket.receive_json()
        task_data = TaskCreate(**data)
        task_data.agent_id = agent_id

        # Execute task with WebSocket streaming
        executor = AgentExecutor(db)
        await executor.execute_task(task_data, websocket)

    except Exception as e:
        await websocket.send_text(f"Error: {str(e)}")
    finally:
        await websocket.close()


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task_status(
    task_id: str,
    owner: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> TaskResponse:
    """Get task execution status and results."""

    task = db.scalar(
        select(models.Task)
        .where(models.Task.id == task_id)
        .where(models.Task.user_id == owner.id)
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    return TaskResponse(
        id=task.id,
        status=task.status,
        agent_id=task.agent_id,
        goal=task.goal,
        created_at=task.created_at,
        started_at=task.started_at,
        completed_at=task.completed_at,
        result=task.result,
        error_message=task.error_message,
    )
