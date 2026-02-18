"""Agent registry CRUD endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, WebSocket
from sqlalchemy import select, update
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.orm import Session

from backend.src.db import models
from backend.src.db.session import get_session
from backend.src.modules.auth.deps import get_verified_user as get_current_user
from backend.src.modules.marketplace.models import (
    AgentCategory,
    AgentDetail,
    AgentListing,
    MarketplaceSearchRequest,
)
from backend.src.modules.marketplace.service import MarketplaceService
from backend.src.modules.onboarding import service as onboarding_service
from backend.src.modules.ops import service as ops_service
from backend.src.modules.support import service as support_service

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

# Import Customer Agent router
try:
    from .customer_agent.router import router as customer_agent_router
except ImportError:
    customer_agent_router = None

# Import Dev Agent router
try:
    from .dev_agent.router import router as dev_agent_router
except ImportError:
    dev_agent_router = None

# Import Finance Agent router
try:
    from .finance_agent.router import router as finance_agent_router
except ImportError:
    finance_agent_router = None

# Import Content Agent router
try:
    from .content_agent.router import router as content_agent_router
except ImportError:
    content_agent_router = None

router = APIRouter(prefix="/agents", tags=["agents"])

# Include specialized agent routers
if cape_ai_guide_router:
    router.include_router(cape_ai_guide_router)
if cape_ai_domain_specialist_router:
    router.include_router(cape_ai_domain_specialist_router)
if customer_agent_router:
    router.include_router(customer_agent_router)
if dev_agent_router:
    router.include_router(dev_agent_router)
if finance_agent_router:
    router.include_router(finance_agent_router)
if content_agent_router:
    router.include_router(content_agent_router)


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


@router.get("", response_model=list[schemas.AgentResponse] | list[AgentListing])
async def list_agents(
    published: bool = False,
    q: str | None = None,
    category: AgentCategory | None = None,
    limit: int = 50,
    owner: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> list[schemas.AgentResponse] | list[AgentListing]:
    if published:
        service = MarketplaceService(db)
        request = MarketplaceSearchRequest(
            query=q,
            category=category,
            limit=limit,
            sort_by="updated",
        )
        result = await service.search_agents(request)
        return result.agents

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


@router.get("/{agent_id}", response_model=schemas.AgentResponse | AgentDetail)
async def get_agent(
    agent_id: str,
    published: bool = False,
    owner: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> schemas.AgentResponse | AgentDetail:
    if published:
        service = MarketplaceService(db)
        return await service.get_agent_detail(agent_id)
    agent = _get_agent(db, agent_id, owner)
    return agent


def _get_published_agent(db: Session, slug: str) -> tuple[models.Agent, models.AgentVersion]:
    agent = db.scalar(
        select(models.Agent)
        .options(selectinload(models.Agent.versions))
        .where(models.Agent.slug == slug)
    )
    if agent is None:
        raise HTTPException(status_code=404, detail="agent not found")
    version = next(
        (v for v in agent.versions if v.status == "published"),
        None,
    )
    if version is None:
        raise HTTPException(status_code=404, detail="published version not found")
    return agent, version


@router.post("/{slug}/launch", response_model=schemas.AgentRunResponse, status_code=201)
def launch_agent(
    slug: str,
    payload: schemas.AgentRunCreate,
    owner: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> schemas.AgentRunResponse:
    agent, _version = _get_published_agent(db, slug)
    run = models.AgentRun(
        agent_id=agent.id,
        user_id=owner.id,
        status="active",
        input_json=payload.input,
    )
    db.add(run)
    db.flush()
    db.add(
        models.AgentEvent(
            run_id=run.id,
            event_type="launch",
            payload_json={"slug": slug, "input": payload.input or {}},
        )
    )
    db.add(
        models.AuditEvent(
            user_id=owner.id,
            agent_id=agent.id,
            event_type="agent_run_launch",
            payload={"run_id": run.id, "slug": slug},
        )
    )
    db.commit()
    db.refresh(run)
    return schemas.AgentRunResponse(
        id=run.id,
        agent_id=run.agent_id,
        user_id=run.user_id,
        status=run.status,
        input_json=run.input_json,
        output_json=run.output_json,
        created_at=run.created_at,
        updated_at=run.updated_at,
    )


@router.post("/{slug}/action", response_model=schemas.AgentActionResponse)
def run_agent_action(
    slug: str,
    payload: schemas.AgentActionRequest,
    owner: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> schemas.AgentActionResponse:
    agent, _version = _get_published_agent(db, slug)
    run = db.scalar(
        select(models.AgentRun).where(
            models.AgentRun.id == payload.run_id,
            models.AgentRun.user_id == owner.id,
        )
    )
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")
    if run.agent_id != agent.id:
        raise HTTPException(status_code=400, detail="run does not match agent")

    action = payload.action.strip().lower()
    result: dict[str, Any]

    if slug == "onboarding-guide":
        if action == "next_step":
            result = onboarding_service.get_next_step(db, owner)
        elif action == "complete_step":
            step_key = str(payload.payload.get("step_key", "")).strip()
            if not step_key:
                raise HTTPException(status_code=400, detail="step_key is required")
            result = onboarding_service.set_step_status(db, owner, step_key, "completed")
        elif action == "blocked":
            step_key = str(payload.payload.get("step_key", "")).strip()
            reason = str(payload.payload.get("reason", "")).strip()
            notes = payload.payload.get("notes")
            if not step_key or not reason:
                raise HTTPException(status_code=400, detail="step_key and reason are required")
            result = onboarding_service.mark_step_blocked(
                db, owner, step_key, reason, notes=notes if isinstance(notes, str) else None
            )
        else:
            raise HTTPException(status_code=400, detail="unsupported onboarding action")
    elif slug == "cape-support-bot":
        if action == "faq_search":
            query = str(payload.payload.get("query", "")).strip() or None
            faqs = support_service.search_faqs(db, query)
            result = {
                "faqs": [
                    {
                        "id": faq.id,
                        "question": faq.question,
                        "answer": faq.answer,
                        "tags": list(faq.tags or []),
                    }
                    for faq in faqs
                ]
            }
        elif action == "create_ticket":
            subject = str(payload.payload.get("subject", "")).strip()
            body = str(payload.payload.get("body", "")).strip()
            if not subject or not body:
                raise HTTPException(status_code=400, detail="subject and body are required")
            ticket = support_service.create_ticket(
                db, user_id=owner.id, subject=subject, body=body
            )
            result = {
                "ticket": {
                    "id": ticket.id,
                    "subject": ticket.subject,
                    "body": ticket.body,
                    "status": ticket.status,
                    "created_at": ticket.created_at,
                }
            }
        elif action == "list_tickets":
            tickets = support_service.list_tickets(db, owner.id)
            result = {
                "tickets": [
                    {
                        "id": ticket.id,
                        "subject": ticket.subject,
                        "body": ticket.body,
                        "status": ticket.status,
                        "created_at": ticket.created_at,
                    }
                    for ticket in tickets
                ]
            }
        else:
            raise HTTPException(status_code=400, detail="unsupported support action")
    elif slug == "data-analyst":
        if action != "insight":
            raise HTTPException(status_code=400, detail="unsupported analyst action")
        intent = str(payload.payload.get("intent", "")).strip()
        if not intent:
            raise HTTPException(status_code=400, detail="intent is required")
        result = ops_service.build_insight(db, owner, intent)
    else:
        raise HTTPException(status_code=400, detail="unknown agent slug")

    event = models.AgentEvent(
        run_id=run.id,
        event_type=action,
        payload_json={"action": action, "result": result},
    )
    run.output_json = {"last_action": action, "result": result}
    db.add(event)
    db.add(
        models.AuditEvent(
            user_id=owner.id,
            agent_id=agent.id,
            event_type="agent_action",
            payload={"run_id": run.id, "slug": slug, "action": action},
        )
    )
    db.commit()
    db.refresh(event)
    return schemas.AgentActionResponse(
        run_id=run.id,
        event_id=event.id,
        status=run.status,
        result=result,
    )


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
        id=str(task.id),
        status=task.status,
        agent_id=task.agent_id,
        goal=task.title,
        created_at=task.created_at,
        started_at=task.started_at,
        completed_at=task.completed_at,
        result=task.output_data,
        error_message=task.error_message,
    )
