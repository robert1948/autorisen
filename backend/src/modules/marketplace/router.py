"""
CapeControl Agent Marketplace API

Comprehensive marketplace endpoints for agent discovery, publishing, installation,
ratings, analytics, and management.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Body
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Dict, Any

from backend.src.db import models
from backend.src.db.session import get_session
from .models import (
    MarketplaceSearchRequest,
    MarketplaceSearchResponse,
    AgentListing,
    AgentDetail,
    AgentInstallRequest,
    AgentInstallResponse,
    PublishAgentRequest,
    MarketplaceAnalytics,
    AgentValidationResult,
    AgentCategory,
)
from .service import MarketplaceService

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


@router.post("/search", response_model=MarketplaceSearchResponse)
async def search_agents(
    request: MarketplaceSearchRequest, db: Session = Depends(get_session)
) -> MarketplaceSearchResponse:
    """
    Search for agents in the marketplace with advanced filtering.

    Supports:
    - Text search across names and descriptions
    - Category filtering
    - Rating filtering
    - Tag-based filtering
    - Multiple sorting options
    - Pagination
    """
    service = MarketplaceService(db)
    return await service.search_agents(request)


@router.get("/search", response_model=MarketplaceSearchResponse)
async def search_agents_get(
    query: str = None,
    category: AgentCategory = None,
    min_rating: float = None,
    sort_by: str = "popularity",
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_session),
) -> MarketplaceSearchResponse:
    """
    GET endpoint for agent search (for simple URL-based searches).
    """
    request = MarketplaceSearchRequest(
        query=query,
        category=category,
        min_rating=min_rating,
        sort_by=sort_by,
        page=page,
        limit=limit,
    )
    service = MarketplaceService(db)
    return await service.search_agents(request)


@router.get("/agents", response_model=list[AgentListing])
async def list_published_agents(
    category: AgentCategory = None, limit: int = 50, db: Session = Depends(get_session)
) -> list[AgentListing]:
    """
    List published agents with optional category filtering.
    """
    request = MarketplaceSearchRequest(
        category=category, limit=limit, sort_by="updated"
    )
    service = MarketplaceService(db)
    result = await service.search_agents(request)
    return result.agents


@router.get("/agents/{slug}", response_model=AgentDetail)
async def get_agent_detail(
    slug: str, db: Session = Depends(get_session)
) -> AgentDetail:
    """
    Get detailed information about a specific agent including
    documentation, requirements, and configuration schema.
    """
    service = MarketplaceService(db)
    return await service.get_agent_detail(slug)


@router.post("/agents/publish", response_model=dict)
async def publish_agent(
    request: PublishAgentRequest, db: Session = Depends(get_session)
) -> dict:
    """
    Publish a new version of an agent to the marketplace.

    Validates the agent manifest and creates a new published version.
    Requires proper semver versioning and valid manifest structure.
    """
    service = MarketplaceService(db)
    return await service.publish_agent(request)


@router.post("/agents/validate", response_model=AgentValidationResult)
async def validate_agent(
    manifest: Dict[str, Any] = Body(...), db: Session = Depends(get_session)
) -> AgentValidationResult:
    """
    Validate an agent manifest before publishing.

    Checks for:
    - Required fields
    - Valid category
    - Proper manifest structure
    - Security scan results
    - Performance benchmarks
    """
    service = MarketplaceService(db)
    return await service.validate_agent(manifest)


@router.post("/agents/{agent_id}/install", response_model=AgentInstallResponse)
async def install_agent(
    agent_id: str,
    request: AgentInstallRequest,
    db: Session = Depends(get_session),
    # TODO: Add user authentication and extract user_id
) -> AgentInstallResponse:
    """
    Install an agent for the current user.

    Handles:
    - Version selection (latest if not specified)
    - Dependency resolution
    - Configuration validation
    - Installation tracking
    """
    # TODO: Extract user_id from authentication
    user_id = "user_placeholder"  # Replace with actual auth

    service = MarketplaceService(db)
    return await service.install_agent(request, user_id)


@router.get("/categories", response_model=list[str])
async def list_categories() -> list[str]:
    """
    Get all available agent categories.
    """
    return [category.value for category in AgentCategory]


@router.get("/analytics", response_model=MarketplaceAnalytics)
async def get_marketplace_analytics(
    db: Session = Depends(get_session),
) -> MarketplaceAnalytics:
    """
    Get marketplace analytics including:
    - Total agents and downloads
    - Popular categories
    - Trending agents
    - Recent updates
    """
    service = MarketplaceService(db)
    return await service.get_marketplace_analytics()


@router.get("/trending", response_model=list[AgentListing])
async def get_trending_agents(
    limit: int = 10, db: Session = Depends(get_session)
) -> list[AgentListing]:
    """
    Get trending agents based on recent downloads and ratings.
    """
    # TODO: Implement proper trending algorithm
    request = MarketplaceSearchRequest(sort_by="popularity", limit=limit)
    service = MarketplaceService(db)
    result = await service.search_agents(request)
    return result.agents


@router.get("/featured", response_model=list[AgentListing])
async def get_featured_agents(db: Session = Depends(get_session)) -> list[AgentListing]:
    """
    Get featured agents curated by the marketplace team.
    """
    # TODO: Add featured flag to agent model
    request = MarketplaceSearchRequest(sort_by="rating", limit=6)
    service = MarketplaceService(db)
    result = await service.search_agents(request)
    return result.agents


# Legacy endpoints for backward compatibility
@router.get("/agents_legacy", response_model=list[dict])
def list_published_agents_legacy(db: Session = Depends(get_session)) -> list[dict]:
    """Legacy endpoint - use /search or /agents instead."""
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
