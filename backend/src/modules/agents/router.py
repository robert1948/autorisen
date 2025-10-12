"""Agent registry CRUD endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from backend.src.db import models
from backend.src.db.session import get_session
from backend.src.modules.auth.deps import get_current_user

from . import schemas

router = APIRouter(prefix="/agents", tags=["agents"])


def _get_agent(db: Session, agent_id: str, owner: models.User) -> models.Agent:
    agent = db.scalar(
        select(models.Agent).where(models.Agent.id == agent_id, models.Agent.owner_id == owner.id)
    )
    if agent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="agent not found")
    return agent


@router.get("", response_model=list[schemas.AgentResponse])
def list_agents(
    owner: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> list[schemas.AgentResponse]:
    agents = db.scalars(select(models.Agent).where(models.Agent.owner_id == owner.id)).all()
    return list(agents)


@router.post("", response_model=schemas.AgentResponse, status_code=status.HTTP_201_CREATED)
def create_agent(
    payload: schemas.AgentCreate,
    owner: models.User = Depends(get_current_user),
    db: Session = Depends(get_session),
) -> schemas.AgentResponse:
    existing = db.scalar(select(models.Agent).where(models.Agent.slug == payload.slug))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="slug already in use")

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


@router.post("/{agent_id}/versions", response_model=schemas.AgentVersionResponse, status_code=status.HTTP_201_CREATED)
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
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="version already exists")

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
            models.AgentVersion.id == version_id, models.AgentVersion.agent_id == agent.id
        )
    )
    if version is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="version not found")

    # Demote currently published versions for this agent.
    db.execute(
        update(models.AgentVersion)
        .where(models.AgentVersion.agent_id == agent.id, models.AgentVersion.status == "published")
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
