"""
Agent Marketplace Service

Core business logic for marketplace operations including search, publishing,
installation, analytics, and validation.
"""

import semver
from datetime import datetime
from typing import Dict, Any
from fastapi import HTTPException, status
from sqlalchemy import select, func, desc, and_, or_
from sqlalchemy.orm import Session, selectinload

from backend.src.db import models
from .models import (
    AgentCategory,
    AgentStatus,
    MarketplaceSearchRequest,
    MarketplaceSearchResponse,
    AgentListing,
    AgentDetail,
    AgentInstallRequest,
    AgentInstallResponse,
    PublishAgentRequest,
    MarketplaceAnalytics,
    AgentValidationResult,
)


class MarketplaceService:
    """Service class for marketplace operations."""

    def __init__(self, db: Session):
        self.db = db

    async def search_agents(
        self, request: MarketplaceSearchRequest
    ) -> MarketplaceSearchResponse:
        """Search for agents in the marketplace with filtering and pagination."""

        # Build base query
        query = (
            select(models.Agent)
            .join(models.AgentVersion)
            .where(models.AgentVersion.status == AgentStatus.PUBLISHED.value)
        )

        # Apply filters
        if request.query:
            search_filter = or_(
                models.Agent.name.ilike(f"%{request.query}%"),
                models.Agent.description.ilike(f"%{request.query}%"),
            )
            query = query.where(search_filter)

        # Note: Simplified filtering without JSON field access for now
        # TODO: Implement proper JSON field filtering when database structure is finalized

        # Apply sorting
        if request.sort_by == "popularity":
            # TODO: Add download count/popularity metrics
            query = query.order_by(desc(models.Agent.updated_at))
        elif request.sort_by == "rating":
            # TODO: Add rating aggregation
            query = query.order_by(desc(models.Agent.updated_at))
        elif request.sort_by == "name":
            query = query.order_by(models.Agent.name)
        elif request.sort_by == "updated":
            query = query.order_by(desc(models.Agent.updated_at))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = self.db.scalar(count_query) or 0

        # Apply pagination
        offset = (request.page - 1) * request.limit
        query = query.offset(offset).limit(request.limit)

        # Execute query
        agents = (
            self.db.scalars(query.options(selectinload(models.Agent.versions)))
            .unique()
            .all()
        )

        # Convert to listings
        listings = []
        for agent in agents:
            published_version = next(
                (v for v in agent.versions if v.status == AgentStatus.PUBLISHED.value),
                None,
            )
            if published_version and published_version.manifest:
                listing = self._agent_to_listing(agent, published_version)
                listings.append(listing)

        # Calculate pagination
        pages = (total + request.limit - 1) // request.limit

        return MarketplaceSearchResponse(
            agents=listings,
            total=total,
            page=request.page,
            pages=pages,
            filters_applied={
                "query": request.query,
                "category": request.category.value if request.category else None,
                "min_rating": request.min_rating,
                "tags": request.tags,
                "sort_by": request.sort_by,
            },
        )

    async def get_agent_detail(self, agent_slug: str) -> AgentDetail:
        """Get detailed information about a specific agent."""

        stmt = (
            select(models.Agent)
            .options(selectinload(models.Agent.versions))
            .where(models.Agent.slug == agent_slug)
        )

        agent = self.db.scalar(stmt)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent '{agent_slug}' not found",
            )

        published_version = next(
            (v for v in agent.versions if v.status == AgentStatus.PUBLISHED.value), None
        )

        if not published_version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No published version found for agent '{agent_slug}'",
            )

        return self._agent_to_detail(agent, published_version)

    async def publish_agent(self, request: PublishAgentRequest) -> Dict[str, Any]:
        """Publish a new version of an agent."""

        # Validate version format
        try:
            semver.VersionInfo.parse(request.version)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid version format: {request.version}. Must be valid semver.",
            )

        # Find existing agent
        stmt = select(models.Agent).where(models.Agent.slug == request.agent_slug)
        agent = self.db.scalar(stmt)

        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent '{request.agent_slug}' not found",
            )

        # Check if version already exists
        version_stmt = select(models.AgentVersion).where(
            and_(
                models.AgentVersion.agent_id == agent.id,
                models.AgentVersion.version == request.version,
            )
        )
        existing_version = self.db.scalar(version_stmt)

        if existing_version:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Version {request.version} already exists for agent '{request.agent_slug}'",
            )

        # Create new version
        new_version = models.AgentVersion(
            agent_id=agent.id,
            version=request.version,
            status=AgentStatus.PUBLISHED.value,
            manifest={
                **request.manifest,
                "readme": request.readme,
                "changelog": request.changelog,
                "tags": request.tags,
                "published_at": datetime.utcnow().isoformat(),
            },
            published_at=datetime.utcnow(),
        )

        self.db.add(new_version)

        # Update agent metadata
        agent.updated_at = datetime.utcnow()
        agent.description = request.manifest.get("description", agent.description)

        self.db.commit()
        self.db.refresh(new_version)

        return {
            "success": True,
            "agent_id": agent.id,
            "version": request.version,
            "published_at": new_version.published_at,
            "message": f"Agent '{agent.name}' version {request.version} published successfully",
        }

    async def install_agent(
        self, request: AgentInstallRequest, user_id: str
    ) -> AgentInstallResponse:
        """Install an agent for a user."""

        # Find agent
        stmt = (
            select(models.Agent)
            .options(selectinload(models.Agent.versions))
            .where(models.Agent.id == request.agent_id)
        )

        agent = self.db.scalar(stmt)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with ID '{request.agent_id}' not found",
            )

        # Find requested version or latest published
        if request.version:
            version = next(
                (
                    v
                    for v in agent.versions
                    if v.version == request.version
                    and v.status == AgentStatus.PUBLISHED.value
                ),
                None,
            )
        else:
            # Get latest published version
            version = max(
                (v for v in agent.versions if v.status == AgentStatus.PUBLISHED.value),
                key=lambda v: semver.VersionInfo.parse(v.version),
                default=None,
            )

        if not version:
            version_msg = f" version {request.version}" if request.version else ""
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No published version found for agent '{agent.name}'{version_msg}",
            )

        # TODO: Check if user already has this agent installed
        # TODO: Handle dependency resolution
        # TODO: Perform actual installation steps

        # Create installation record (placeholder)
        installation_id = (
            f"install_{agent.id}_{user_id}_{datetime.utcnow().timestamp()}"
        )

        # TODO: Track installation in database
        # For now, simulate successful installation

        next_steps = []
        manifest = version.manifest or {}

        if "configuration" in manifest:
            next_steps.append("Configure the agent in your settings panel")

        if "permissions" in manifest:
            next_steps.append("Review and approve required permissions")

        next_steps.append(f"Access your new agent at /agents/{agent.slug}")

        return AgentInstallResponse(
            success=True,
            agent_id=agent.id,
            version=version.version,
            installation_id=installation_id,
            message=f"Successfully installed {agent.name} v{version.version}",
            next_steps=next_steps,
        )

    async def get_marketplace_analytics(self) -> MarketplaceAnalytics:
        """Get marketplace analytics and statistics."""

        # Count total published agents
        total_agents_stmt = (
            select(func.count(models.Agent.id.distinct()))
            .join(models.AgentVersion)
            .where(models.AgentVersion.status == AgentStatus.PUBLISHED.value)
        )
        total_agents = self.db.scalar(total_agents_stmt) or 0

        # TODO: Implement proper download tracking
        total_downloads = 0  # Placeholder
        active_users = 0  # Placeholder

        # Get popular categories (simplified for now)
        # Note: JSON field access in SQLAlchemy needs careful handling
        popular_categories = [
            {"category": "automation", "count": 12},
            {"category": "analytics", "count": 8},
            {"category": "ai_assistant", "count": 6},
            {"category": "integration", "count": 4},
            {"category": "security", "count": 3},
        ]

        # Get recent updates
        recent_stmt = (
            select(models.Agent, models.AgentVersion)
            .join(models.AgentVersion)
            .where(models.AgentVersion.status == AgentStatus.PUBLISHED.value)
            .order_by(desc(models.AgentVersion.published_at))
            .limit(10)
        )

        recent_results = self.db.execute(recent_stmt).fetchall()
        recent_updates = [
            {
                "agent_name": result.Agent.name,
                "version": result.AgentVersion.version,
                "updated_at": result.AgentVersion.published_at,
            }
            for result in recent_results
        ]

        # TODO: Get trending agents based on download/usage metrics
        trending_agents = []

        return MarketplaceAnalytics(
            total_agents=total_agents,
            total_downloads=total_downloads,
            active_users=active_users,
            popular_categories=popular_categories,
            trending_agents=trending_agents,
            recent_updates=recent_updates,
        )

    async def validate_agent(self, manifest: Dict[str, Any]) -> AgentValidationResult:
        """Validate an agent before publishing."""

        errors = []
        warnings = []

        # Required fields validation
        required_fields = ["name", "description", "category", "entry_point"]
        for field in required_fields:
            if field not in manifest:
                errors.append(f"Missing required field: {field}")

        # Category validation
        if "category" in manifest:
            try:
                AgentCategory(manifest["category"])
            except ValueError:
                errors.append(f"Invalid category: {manifest['category']}")

        # Requirements validation
        if "requirements" in manifest:
            if not isinstance(manifest["requirements"], list):
                errors.append("Requirements must be a list of strings")

        # Entry point validation
        if "entry_point" in manifest:
            if not isinstance(manifest["entry_point"], str):
                errors.append("Entry point must be a string")

        # Security scan (placeholder)
        security_scan = {
            "vulnerabilities": 0,
            "safe": True,
            "scan_date": datetime.utcnow().isoformat(),
        }

        # Performance score (placeholder)
        performance_score = 8.5

        return AgentValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            security_scan=security_scan,
            performance_score=performance_score,
        )

    def _agent_to_listing(
        self, agent: models.Agent, version: models.AgentVersion
    ) -> AgentListing:
        """Convert database models to AgentListing."""

        manifest = version.manifest or {}

        return AgentListing(
            id=agent.id,
            slug=agent.slug,
            name=agent.name,
            description=agent.description,
            category=AgentCategory(manifest.get("category", "productivity")),
            author=manifest.get("author", "Unknown"),
            version=version.version,
            rating=4.5,  # TODO: Calculate from actual ratings
            downloads=manifest.get("downloads", 0),
            tags=manifest.get("tags", []),
            published_at=version.published_at or datetime.utcnow(),
            updated_at=agent.updated_at,
            thumbnail_url=manifest.get("thumbnail_url"),
        )

    def _agent_to_detail(
        self, agent: models.Agent, version: models.AgentVersion
    ) -> AgentDetail:
        """Convert database models to AgentDetail."""

        manifest = version.manifest or {}
        listing = self._agent_to_listing(agent, version)

        return AgentDetail(
            **listing.dict(),
            readme=manifest.get("readme", ""),
            changelog=manifest.get("changelog", ""),
            requirements=manifest.get("requirements", []),
            configuration=manifest.get("configuration", {}),
            permissions=manifest.get("permissions", []),
            license=manifest.get("license", "MIT"),
            repository_url=manifest.get("repository_url"),
            documentation_url=manifest.get("documentation_url"),
            support_url=manifest.get("support_url"),
        )
