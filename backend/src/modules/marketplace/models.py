"""
CapeControl Agent Marketplace Models

Pydantic schemas for marketplace operations including discovery, publishing,
ratings, analytics, and installation management.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class AgentCategory(str, Enum):
    """Agent category classifications."""

    AUTOMATION = "automation"
    ANALYTICS = "analytics"
    INTEGRATION = "integration"
    SECURITY = "security"
    PRODUCTIVITY = "productivity"
    AI_ASSISTANT = "ai_assistant"
    WORKFLOW = "workflow"
    MONITORING = "monitoring"
    COMMUNICATION = "communication"
    DEVELOPMENT = "development"


class AgentStatus(str, Enum):
    """Agent publication status."""

    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class MarketplaceSearchRequest(BaseModel):
    """Search request for marketplace agents."""

    query: Optional[str] = Field(None, description="Search query text")
    category: Optional[AgentCategory] = Field(None, description="Agent category filter")
    min_rating: Optional[float] = Field(
        None, description="Minimum rating filter", ge=0.0, le=5.0
    )
    tags: Optional[List[str]] = Field(default_factory=list, description="Tag filters")
    sort_by: Optional[str] = Field(
        "popularity", description="Sort order: popularity, rating, name, updated"
    )
    page: int = Field(1, description="Page number", ge=1)
    limit: int = Field(20, description="Results per page", ge=1, le=100)


class AgentListing(BaseModel):
    """Agent listing for marketplace display."""

    id: str = Field(..., description="Agent unique identifier")
    slug: str = Field(..., description="URL-friendly agent name")
    name: str = Field(..., description="Agent display name")
    description: str = Field(..., description="Agent description")
    category: AgentCategory = Field(..., description="Agent category")
    author: str = Field(..., description="Agent author/publisher")
    version: str = Field(..., description="Current published version")
    rating: float = Field(..., description="Average user rating", ge=0.0, le=5.0)
    downloads: int = Field(..., description="Total download count")
    tags: List[str] = Field(default_factory=list, description="Agent tags")
    published_at: datetime = Field(..., description="Publication date")
    updated_at: datetime = Field(..., description="Last update date")
    thumbnail_url: Optional[str] = Field(None, description="Agent thumbnail image")


class AgentDetail(AgentListing):
    """Detailed agent information including full metadata."""

    readme: str = Field(..., description="Agent documentation markdown")
    changelog: str = Field(..., description="Version changelog")
    requirements: List[str] = Field(
        default_factory=list, description="Agent dependencies"
    )
    configuration: Dict[str, Any] = Field(
        default_factory=dict, description="Configuration schema"
    )
    permissions: List[str] = Field(
        default_factory=list, description="Required permissions"
    )
    license: str = Field("MIT", description="License type")
    repository_url: Optional[str] = Field(None, description="Source repository URL")
    documentation_url: Optional[str] = Field(None, description="Documentation URL")
    support_url: Optional[str] = Field(None, description="Support/issues URL")


class AgentRating(BaseModel):
    """User rating and review for an agent."""

    agent_id: str = Field(..., description="Agent identifier")
    user_id: str = Field(..., description="User identifier")
    rating: int = Field(..., description="Rating score", ge=1, le=5)
    review: Optional[str] = Field(None, description="Review text", max_length=1000)
    created_at: datetime = Field(..., description="Review creation date")
    helpful_votes: int = Field(0, description="Helpful vote count")


class AgentInstallRequest(BaseModel):
    """Request to install an agent."""

    agent_id: str = Field(..., description="Agent to install")
    version: Optional[str] = Field(
        None, description="Specific version (latest if not specified)"
    )
    configuration: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Installation configuration"
    )


class AgentInstallResponse(BaseModel):
    """Response from agent installation."""

    success: bool = Field(..., description="Installation success status")
    agent_id: str = Field(..., description="Installed agent ID")
    version: str = Field(..., description="Installed version")
    installation_id: str = Field(..., description="Installation tracking ID")
    message: str = Field(..., description="Installation status message")
    next_steps: Optional[List[str]] = Field(
        default_factory=list, description="Post-installation steps"
    )


class PublishAgentRequest(BaseModel):
    """Request to publish a new agent version."""

    agent_slug: str = Field(..., description="Agent slug identifier")
    version: str = Field(..., description="Version number (semver)")
    manifest: Dict[str, Any] = Field(..., description="Agent manifest")
    readme: str = Field(..., description="Documentation markdown")
    changelog: str = Field(..., description="Version changelog")
    tags: List[str] = Field(default_factory=list, description="Agent tags")


class MarketplaceAnalytics(BaseModel):
    """Marketplace analytics and statistics."""

    total_agents: int = Field(..., description="Total published agents")
    total_downloads: int = Field(..., description="Total downloads across all agents")
    active_users: int = Field(..., description="Active users in last 30 days")
    popular_categories: List[Dict[str, Any]] = Field(
        default_factory=list, description="Popular categories"
    )
    trending_agents: List[AgentListing] = Field(
        default_factory=list, description="Trending agents"
    )
    recent_updates: List[Dict[str, Any]] = Field(
        default_factory=list, description="Recent agent updates"
    )


class MarketplaceSearchResponse(BaseModel):
    """Search results from marketplace."""

    agents: List[AgentListing] = Field(default_factory=list, description="Found agents")
    total: int = Field(..., description="Total matching agents")
    page: int = Field(..., description="Current page")
    pages: int = Field(..., description="Total pages")
    filters_applied: Dict[str, Any] = Field(
        default_factory=dict, description="Applied filters"
    )


class AgentValidationResult(BaseModel):
    """Result of agent validation for publishing."""

    valid: bool = Field(..., description="Validation success status")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    security_scan: Dict[str, Any] = Field(
        default_factory=dict, description="Security scan results"
    )
    performance_score: Optional[float] = Field(
        None, description="Performance benchmark score"
    )
