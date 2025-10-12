"""Public marketplace endpoints for published agents."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.src.db import models
from backend.src.db.session import get_session

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


@router.get("/agents", response_model=list[dict])
def list_published_agents(db: Session = Depends(get_session)) -> list[dict]:
    stmt = (
        select(models.Agent)
        .join(models.AgentVersion)
        .where(models.AgentVersion.status == "published")
        .order_by(models.Agent.updated_at.desc())
    )
    agents = db.scalars(stmt).unique().all()

    results: list[dict] = []
    for agent in agents:
        published_version = next(
            (version for version in agent.versions if version.status == "published"),
            None,
        )
        if not published_version:
            continue
        results.append(
            {
                "id": agent.id,
                "slug": agent.slug,
                "name": agent.name,
                "description": agent.description,
                "owner_id": agent.owner_id,
                "updated_at": agent.updated_at,
                "version": {
                    "id": published_version.id,
                    "version": published_version.version,
                    "published_at": published_version.published_at,
                    "manifest": published_version.manifest,
                },
            }
        )

    return results


@router.get("/agents/{slug}", response_model=dict)
def get_agent_detail(slug: str, db: Session = Depends(get_session)) -> dict:
    stmt = select(models.Agent).where(models.Agent.slug == slug)
    agent = db.scalar(stmt)
    if agent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="agent not found")

    published_version = next((version for version in agent.versions if version.status == "published"), None)
    versions = [
        {
            "id": version.id,
            "version": version.version,
            "status": version.status,
            "created_at": version.created_at,
            "published_at": version.published_at,
            "manifest": version.manifest,
        }
        for version in agent.versions
    ]

    return {
        "id": agent.id,
        "slug": agent.slug,
        "name": agent.name,
        "description": agent.description,
        "owner_id": agent.owner_id,
        "created_at": agent.created_at,
        "updated_at": agent.updated_at,
        "published_version": published_version.id if published_version else None,
        "versions": versions,
    }
