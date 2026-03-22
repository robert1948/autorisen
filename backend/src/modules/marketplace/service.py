"""
Agent Marketplace Service

Core business logic for marketplace operations including search, publishing,
installation, analytics, and validation.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import semver
from backend.src.db import models
from fastapi import HTTPException, status
from sqlalchemy import and_, desc, func, inspect, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from .models import (
    AgentCategory,
    AgentDetail,
    AgentInstallRequest,
    AgentInstallResponse,
    AgentListing,
    AgentRatingSummary,
    AgentStatus,
    AgentValidationResult,
    MarketplaceAnalytics,
    MarketplaceSearchRequest,
    MarketplaceSearchResponse,
    PublishAgentRequest,
    RateAgentRequest,
)
from .models import AgentRating as AgentRatingSchema

log = logging.getLogger(__name__)


class MarketplaceService:
    """Service class for marketplace operations."""

    def __init__(self, db: Session):
        self.db = db
        self._agent_installations_available: Optional[bool] = None
        self._agent_ratings_available: Optional[bool] = None

    def _has_agent_installations_table(self) -> bool:
        if self._agent_installations_available is not None:
            return self._agent_installations_available
        try:
            inspector = inspect(self.db.bind)
            self._agent_installations_available = inspector.has_table(
                "agent_installations"
            )
        except Exception:
            self._agent_installations_available = False
        return self._agent_installations_available

    def _has_agent_ratings_table(self) -> bool:
        if self._agent_ratings_available is not None:
            return self._agent_ratings_available
        try:
            inspector = inspect(self.db.bind)
            self._agent_ratings_available = inspector.has_table("agent_ratings")
        except Exception:
            self._agent_ratings_available = False
        return self._agent_ratings_available

    async def search_agents(
        self, request: MarketplaceSearchRequest
    ) -> MarketplaceSearchResponse:
        """Search for agents in the marketplace with filtering and pagination."""

        # Build base query – only public agents with a published version
        query = (
            select(models.Agent)
            .join(models.AgentVersion)
            .where(
                and_(
                    models.AgentVersion.status == AgentStatus.PUBLISHED.value,
                    models.Agent.visibility == "public",
                )
            )
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
        if request.sort_by == "popularity" and self._has_agent_installations_table():
            # Sub-select: count installations per agent
            dl_sub = (
                select(
                    models.AgentInstallation.agent_id,
                    func.count(models.AgentInstallation.id).label("dl_count"),
                )
                .group_by(models.AgentInstallation.agent_id)
                .subquery()
            )
            query = query.outerjoin(
                dl_sub, models.Agent.id == dl_sub.c.agent_id
            ).order_by(desc(func.coalesce(dl_sub.c.dl_count, 0)))
        elif request.sort_by == "popularity":
            # Compatibility fallback when legacy DB does not yet have installations.
            query = query.order_by(desc(models.Agent.updated_at))
        elif request.sort_by == "rating" and self._has_agent_ratings_table():
            # Sub-select: average rating per agent from user reviews
            rating_sub = (
                select(
                    models.AgentRating.agent_id,
                    func.avg(models.AgentRating.rating).label("avg_rating"),
                )
                .group_by(models.AgentRating.agent_id)
                .subquery()
            )
            query = query.outerjoin(
                rating_sub, models.Agent.id == rating_sub.c.agent_id
            ).order_by(desc(func.coalesce(rating_sub.c.avg_rating, 0)))
        elif request.sort_by == "rating":
            # Compatibility fallback when legacy DB does not yet have ratings.
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

        # Compute download counts for the result set
        agent_ids = [a.id for a in agents]
        download_map = self._get_download_counts(agent_ids)

        # Convert to listings
        listings = []
        for agent in agents:
            published_version = next(
                (v for v in agent.versions if v.status == AgentStatus.PUBLISHED.value),
                None,
            )
            if published_version and published_version.manifest:
                listing = self._agent_to_listing(
                    agent,
                    published_version,
                    download_count=download_map.get(agent.id, 0),
                )
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
            .where(
                and_(
                    models.Agent.slug == agent_slug,
                    models.Agent.visibility == "public",
                )
            )
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
        self,
        request: AgentInstallRequest,
        user_id: str,
        ip_address: str = None,
        user_agent: str = None,
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

        # Check if already installed
        if not self._has_agent_installations_table():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Agent installations are temporarily unavailable.",
            )

        install_stmt = select(models.AgentInstallation).where(
            and_(
                models.AgentInstallation.user_id == user_id,
                models.AgentInstallation.agent_id == agent.id,
            )
        )
        existing_install = self.db.scalar(install_stmt)

        if existing_install:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Agent '{agent.name}' is already installed",
            )

        # Create installation record
        installation = models.AgentInstallation(
            user_id=user_id,
            agent_id=agent.id,
            version=version.version,
            configuration=request.configuration or {},
            status="active",
            installed_at=datetime.utcnow(),
        )
        self.db.add(installation)
        self.db.flush()  # Ensure ID is generated

        # Create audit event
        audit_event = models.AuditEvent(
            agent_id=agent.id,
            user_id=user_id,
            event_type="agent_install",
            event_data={
                "version": version.version,
                "installation_id": installation.id,
                "configuration": request.configuration,
            },
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(audit_event)

        self.db.commit()
        self.db.refresh(installation)

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
            installation_id=installation.id,
            message=f"Successfully installed {agent.name} v{version.version}",
            next_steps=next_steps,
        )

    async def get_marketplace_analytics(self) -> MarketplaceAnalytics:
        """Get marketplace analytics and statistics."""

        # Count total published agents (public only)
        total_agents_stmt = (
            select(func.count(models.Agent.id.distinct()))
            .join(models.AgentVersion)
            .where(
                and_(
                    models.AgentVersion.status == AgentStatus.PUBLISHED.value,
                    models.Agent.visibility == "public",
                )
            )
        )
        total_agents = self.db.scalar(total_agents_stmt) or 0

        # Real download count = total installations
        if self._has_agent_installations_table():
            total_downloads = (
                self.db.scalar(select(func.count(models.AgentInstallation.id))) or 0
            )
            # Active users = distinct users with an active installation
            active_users = (
                self.db.scalar(
                    select(
                        func.count(models.AgentInstallation.user_id.distinct())
                    ).where(models.AgentInstallation.status == "active")
                )
                or 0
            )
        else:
            total_downloads = 0
            active_users = 0

        # Real category counts from published public agents
        popular_categories = []
        published_agents_stmt = (
            select(models.Agent, models.AgentVersion.manifest)
            .join(models.AgentVersion)
            .where(
                and_(
                    models.AgentVersion.status == AgentStatus.PUBLISHED.value,
                    models.Agent.visibility == "public",
                )
            )
        )
        cat_counts: Dict[str, int] = {}
        for row in self.db.execute(published_agents_stmt).fetchall():
            manifest = row.manifest or {}
            cat = manifest.get("category", "productivity")
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
        for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
            popular_categories.append({"category": cat, "count": count})

        # Get recent updates (public agents only)
        recent_stmt = (
            select(models.Agent, models.AgentVersion)
            .join(models.AgentVersion)
            .where(
                and_(
                    models.AgentVersion.status == AgentStatus.PUBLISHED.value,
                    models.Agent.visibility == "public",
                )
            )
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

        # Trending: agents with most installs in the last 30 days
        trending_agents = await self.get_trending_agents(limit=5)

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

    # ------------------------------------------------------------------
    # Agent ratings
    # ------------------------------------------------------------------

    async def rate_agent(
        self, agent_id: str, user_id: str, request: RateAgentRequest
    ) -> AgentRatingSchema:
        """Create or update a user's rating for an agent."""
        # Verify agent exists
        agent = self.db.scalar(select(models.Agent).where(models.Agent.id == agent_id))
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent '{agent_id}' not found",
            )

        # Upsert: check for existing rating by this user
        existing = self.db.scalar(
            select(models.AgentRating).where(
                and_(
                    models.AgentRating.user_id == user_id,
                    models.AgentRating.agent_id == agent_id,
                )
            )
        )

        if existing:
            existing.rating = request.rating
            existing.review = request.review
            self.db.commit()
            self.db.refresh(existing)
            row = existing
        else:
            row = models.AgentRating(
                user_id=user_id,
                agent_id=agent_id,
                rating=request.rating,
                review=request.review,
            )
            self.db.add(row)
            self.db.commit()
            self.db.refresh(row)

        return AgentRatingSchema(
            agent_id=row.agent_id,
            user_id=row.user_id,
            rating=row.rating,
            review=row.review,
            created_at=row.created_at,
            helpful_votes=row.helpful_votes,
        )

    async def get_agent_ratings(
        self, agent_id: str, page: int = 1, limit: int = 20
    ) -> dict:
        """Return paginated ratings for an agent with summary stats."""
        # Summary
        summary_row = self.db.execute(
            select(
                func.count(models.AgentRating.id).label("total"),
                func.coalesce(func.avg(models.AgentRating.rating), 0).label("avg"),
            ).where(models.AgentRating.agent_id == agent_id)
        ).one()

        total = summary_row.total
        avg_rating = round(float(summary_row.avg), 2)

        # Distribution
        dist_rows = self.db.execute(
            select(
                models.AgentRating.rating,
                func.count(models.AgentRating.id).label("cnt"),
            )
            .where(models.AgentRating.agent_id == agent_id)
            .group_by(models.AgentRating.rating)
        ).all()
        distribution = {str(i): 0 for i in range(1, 6)}
        for dr in dist_rows:
            distribution[str(dr.rating)] = dr.cnt

        # Paginated reviews
        offset = (page - 1) * limit
        rows = self.db.scalars(
            select(models.AgentRating)
            .where(models.AgentRating.agent_id == agent_id)
            .order_by(desc(models.AgentRating.created_at))
            .offset(offset)
            .limit(limit)
        ).all()

        ratings = [
            AgentRatingSchema(
                agent_id=r.agent_id,
                user_id=r.user_id,
                rating=r.rating,
                review=r.review,
                created_at=r.created_at,
                helpful_votes=r.helpful_votes,
            )
            for r in rows
        ]

        return {
            "summary": AgentRatingSummary(
                agent_id=agent_id,
                average_rating=avg_rating,
                total_ratings=total,
                distribution=distribution,
            ),
            "ratings": ratings,
            "page": page,
            "pages": (total + limit - 1) // limit if total > 0 else 1,
        }

    async def delete_agent_rating(self, agent_id: str, user_id: str) -> bool:
        """Delete a user's rating for an agent. Returns True if deleted."""
        row = self.db.scalar(
            select(models.AgentRating).where(
                and_(
                    models.AgentRating.user_id == user_id,
                    models.AgentRating.agent_id == agent_id,
                )
            )
        )
        if not row:
            return False
        self.db.delete(row)
        self.db.commit()
        return True

    def _get_average_rating(self, agent_id: str) -> Optional[float]:
        """Return the average user rating for an agent, or None."""
        if not self._has_agent_ratings_table():
            return None
        try:
            result = self.db.scalar(
                select(func.avg(models.AgentRating.rating)).where(
                    models.AgentRating.agent_id == agent_id
                )
            )
            return round(float(result), 2) if result else None
        except SQLAlchemyError:
            log.warning("Average rating query failed; returning None", exc_info=True)
            return None

    # ------------------------------------------------------------------
    # Download-count helpers
    # ------------------------------------------------------------------

    def _get_download_counts(self, agent_ids: List[str]) -> Dict[str, int]:
        """Return {agent_id: install_count} for the given IDs."""
        if not agent_ids:
            return {}
        if not self._has_agent_installations_table():
            return {}
        try:
            rows = self.db.execute(
                select(
                    models.AgentInstallation.agent_id,
                    func.count(models.AgentInstallation.id).label("cnt"),
                )
                .where(models.AgentInstallation.agent_id.in_(agent_ids))
                .group_by(models.AgentInstallation.agent_id)
            ).fetchall()
            return {r.agent_id: r.cnt for r in rows}
        except SQLAlchemyError:
            log.warning("Download-count query failed; returning zeros", exc_info=True)
            return {}

    def _get_download_count(self, agent_id: str) -> int:
        """Return the total installation count for a single agent."""
        if not self._has_agent_installations_table():
            return 0
        try:
            return (
                self.db.scalar(
                    select(func.count(models.AgentInstallation.id)).where(
                        models.AgentInstallation.agent_id == agent_id
                    )
                )
                or 0
            )
        except SQLAlchemyError:
            log.warning(
                "Single download-count query failed; returning 0", exc_info=True
            )
            return 0

    # ------------------------------------------------------------------
    # Featured
    # ------------------------------------------------------------------

    async def get_featured_agents(self, limit: int = 6) -> List[AgentListing]:
        """Return agents marked as featured by the marketplace team."""
        stmt = (
            select(models.Agent)
            .join(models.AgentVersion)
            .where(
                and_(
                    models.Agent.is_featured == True,  # noqa: E712
                    models.AgentVersion.status == AgentStatus.PUBLISHED.value,
                    models.Agent.visibility == "public",
                )
            )
            .order_by(desc(models.Agent.updated_at))
            .limit(limit)
        )

        agents = (
            self.db.scalars(stmt.options(selectinload(models.Agent.versions)))
            .unique()
            .all()
        )

        agent_ids = [a.id for a in agents]
        download_map = self._get_download_counts(agent_ids)

        listings: List[AgentListing] = []
        for agent in agents:
            pv = next(
                (v for v in agent.versions if v.status == AgentStatus.PUBLISHED.value),
                None,
            )
            if pv and pv.manifest:
                listings.append(
                    self._agent_to_listing(
                        agent, pv, download_count=download_map.get(agent.id, 0)
                    )
                )
        return listings

    # ------------------------------------------------------------------
    # Trending
    # ------------------------------------------------------------------

    async def get_trending_agents(
        self, limit: int = 10, days: int = 30
    ) -> List[AgentListing]:
        """Return agents ranked by installation count in the last *days* days."""
        if not self._has_agent_installations_table():
            # Compatibility fallback: without installations table we cannot rank by downloads.
            return []

        cutoff = datetime.utcnow() - timedelta(days=days)

        # Sub-select: installations since cutoff
        recent_dl = (
            select(
                models.AgentInstallation.agent_id,
                func.count(models.AgentInstallation.id).label("recent_count"),
            )
            .where(models.AgentInstallation.installed_at >= cutoff)
            .group_by(models.AgentInstallation.agent_id)
            .subquery()
        )

        stmt = (
            select(models.Agent)
            .join(models.AgentVersion)
            .join(recent_dl, models.Agent.id == recent_dl.c.agent_id)
            .where(
                and_(
                    models.AgentVersion.status == AgentStatus.PUBLISHED.value,
                    models.Agent.visibility == "public",
                )
            )
            .order_by(desc(recent_dl.c.recent_count))
            .limit(limit)
        )

        agents = (
            self.db.scalars(stmt.options(selectinload(models.Agent.versions)))
            .unique()
            .all()
        )

        agent_ids = [a.id for a in agents]
        download_map = self._get_download_counts(agent_ids)

        listings: List[AgentListing] = []
        for agent in agents:
            pv = next(
                (v for v in agent.versions if v.status == AgentStatus.PUBLISHED.value),
                None,
            )
            if pv and pv.manifest:
                listings.append(
                    self._agent_to_listing(
                        agent, pv, download_count=download_map.get(agent.id, 0)
                    )
                )
        return listings

    # ------------------------------------------------------------------
    # Conversion helpers
    # ------------------------------------------------------------------

    def _agent_to_listing(
        self,
        agent: models.Agent,
        version: models.AgentVersion,
        *,
        download_count: Optional[int] = None,
    ) -> AgentListing:
        """Convert database models to AgentListing."""

        manifest = version.manifest or {}

        # Use supplied count, fall back to a single-agent query
        if download_count is None:
            download_count = self._get_download_count(agent.id)

        return AgentListing(
            id=agent.id,
            slug=agent.slug,
            name=agent.name,
            description=agent.description,
            category=AgentCategory(manifest.get("category", "productivity")),
            author=manifest.get("author", "Unknown"),
            version=version.version,
            rating=self._get_average_rating(agent.id),
            downloads=download_count,
            tags=manifest.get("tags", []),
            published_at=version.published_at or datetime.utcnow(),
            updated_at=agent.updated_at,
            thumbnail_url=manifest.get("thumbnail_url"),
            is_featured=bool(agent.is_featured),
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
