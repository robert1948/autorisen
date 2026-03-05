import uuid
from datetime import datetime

import pytest
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.src.db import models
from backend.src.db.session import SessionLocal
from backend.src.modules.marketplace.models import AgentInstallRequest, AgentStatus
from backend.src.modules.marketplace.service import MarketplaceService


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def sample_agent(db_session: Session):
    # Create a test agent with unique slug
    unique_slug = f"test-agent-{uuid.uuid4()}"
    agent = models.Agent(
        slug=unique_slug,
        name="Test Agent",
        description="A test agent",
        owner_id="test-owner",
        visibility="public",
    )
    db_session.add(agent)
    db_session.commit()

    # Create a published version
    version = models.AgentVersion(
        agent_id=agent.id,
        version="1.0.0",
        status=AgentStatus.PUBLISHED.value,
        manifest={
            "name": "Test Agent",
            "description": "A test agent",
            "category": "productivity",
            "entry_point": "main.py",
            "permissions": ["read_files"],
        },
        published_at=datetime.utcnow(),
    )
    db_session.add(version)
    db_session.commit()
    db_session.refresh(agent)
    return agent


@pytest.mark.asyncio
async def test_install_agent_success(db_session: Session, sample_agent):
    service = MarketplaceService(db_session)
    request = AgentInstallRequest(agent_id=sample_agent.id)
    user_id = "test-user-123"

    response = await service.install_agent(request, user_id)

    assert response.success is True
    assert response.agent_id == sample_agent.id
    assert response.version == "1.0.0"
    assert response.installation_id is not None

    # Verify installation record in DB
    stmt = select(models.AgentInstallation).where(
        models.AgentInstallation.id == response.installation_id
    )
    installation = db_session.scalar(stmt)
    assert installation is not None
    assert installation.user_id == user_id
    assert installation.agent_id == sample_agent.id
    assert installation.version == "1.0.0"

    # Verify audit event
    audit_stmt = select(models.AuditEvent).where(
        models.AuditEvent.event_type == "agent_install",
        models.AuditEvent.user_id == user_id,
        models.AuditEvent.agent_id == sample_agent.id,
    )
    audit_event = db_session.scalar(audit_stmt)
    assert audit_event is not None
    assert audit_event.event_data["version"] == "1.0.0"
    assert audit_event.event_data["installation_id"] == installation.id


@pytest.mark.asyncio
async def test_install_agent_version_not_found(db_session: Session, sample_agent):
    service = MarketplaceService(db_session)
    request = AgentInstallRequest(agent_id=sample_agent.id, version="9.9.9")
    user_id = "test-user-123"

    with pytest.raises(Exception) as excinfo:
        await service.install_agent(request, user_id)

    assert "No published version found" in str(excinfo.value)


@pytest.mark.asyncio
async def test_install_agent_already_installed(db_session: Session, sample_agent):
    service = MarketplaceService(db_session)
    request = AgentInstallRequest(agent_id=sample_agent.id)
    user_id = "test-user-duplicate"

    # First install
    await service.install_agent(request, user_id)

    # Second install should fail
    with pytest.raises(HTTPException) as excinfo:
        await service.install_agent(request, user_id)
    assert "already installed" in str(excinfo.value)


# ------------------------------------------------------------------
# Download count & trending tests
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_download_count_reflects_installations(db_session: Session, sample_agent):
    """After installing, the listing download count should equal 1."""
    service = MarketplaceService(db_session)

    # Before install – count should be 0
    count_before = service._get_download_count(sample_agent.id)
    assert count_before == 0

    # Install
    request = AgentInstallRequest(agent_id=sample_agent.id)
    await service.install_agent(request, "dl-user-1")

    count_after = service._get_download_count(sample_agent.id)
    assert count_after == 1


@pytest.mark.asyncio
async def test_listing_downloads_from_installations(db_session: Session, sample_agent):
    """AgentListing.downloads should use real installation count."""
    service = MarketplaceService(db_session)

    # Install twice with different users
    await service.install_agent(AgentInstallRequest(agent_id=sample_agent.id), "u1")
    await service.install_agent(AgentInstallRequest(agent_id=sample_agent.id), "u2")

    pv = next(v for v in sample_agent.versions if v.status == "published")
    listing = service._agent_to_listing(sample_agent, pv)
    assert listing.downloads == 2


@pytest.mark.asyncio
async def test_trending_returns_recently_installed(db_session: Session, sample_agent):
    """Trending endpoint should return agents with recent installs."""
    service = MarketplaceService(db_session)
    await service.install_agent(
        AgentInstallRequest(agent_id=sample_agent.id), "trend-user"
    )

    trending = await service.get_trending_agents(limit=5)
    slugs = [a.slug for a in trending]
    assert sample_agent.slug in slugs


@pytest.mark.asyncio
async def test_trending_respects_limit(db_session: Session, sample_agent):
    """Trending should respect the limit parameter."""
    service = MarketplaceService(db_session)
    await service.install_agent(
        AgentInstallRequest(agent_id=sample_agent.id), "limit-user"
    )
    trending = await service.get_trending_agents(limit=1)
    assert len(trending) <= 1


# ------------------------------------------------------------------
# Featured agents tests
# ------------------------------------------------------------------


@pytest.fixture
def featured_agent(db_session: Session):
    """Create a public, featured agent with a published version."""
    unique_slug = f"featured-agent-{uuid.uuid4()}"
    agent = models.Agent(
        slug=unique_slug,
        name="Featured Agent",
        description="A curated agent",
        owner_id="test-owner",
        visibility="public",
        is_featured=True,
    )
    db_session.add(agent)
    db_session.commit()

    version = models.AgentVersion(
        agent_id=agent.id,
        version="1.0.0",
        status=AgentStatus.PUBLISHED.value,
        manifest={
            "name": "Featured Agent",
            "description": "A curated agent",
            "category": "productivity",
            "entry_point": "main.py",
        },
        published_at=datetime.utcnow(),
    )
    db_session.add(version)
    db_session.commit()
    db_session.refresh(agent)
    return agent


@pytest.mark.asyncio
async def test_featured_returns_flagged_agents(db_session: Session, featured_agent):
    """get_featured_agents should include agents with is_featured=True."""
    service = MarketplaceService(db_session)
    featured = await service.get_featured_agents(limit=10)
    slugs = [a.slug for a in featured]
    assert featured_agent.slug in slugs


@pytest.mark.asyncio
async def test_featured_excludes_non_featured(db_session: Session, sample_agent):
    """Regular (non-featured) agents should NOT appear in the featured list."""
    service = MarketplaceService(db_session)
    featured = await service.get_featured_agents(limit=10)
    slugs = [a.slug for a in featured]
    assert sample_agent.slug not in slugs


@pytest.mark.asyncio
async def test_listing_includes_is_featured_field(db_session: Session, featured_agent):
    """AgentListing.is_featured should be True for featured agents."""
    service = MarketplaceService(db_session)
    pv = next(v for v in featured_agent.versions if v.status == "published")
    listing = service._agent_to_listing(featured_agent, pv)
    assert listing.is_featured is True
