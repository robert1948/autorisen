"""Tests for agent rating service methods and usage summary enhancements."""

import uuid
from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.src.db import models
from backend.src.db.session import SessionLocal
from backend.src.modules.marketplace.models import (
    AgentStatus,
    RateAgentRequest,
)
from backend.src.modules.marketplace.service import MarketplaceService
from backend.src.modules.usage import service as usage_service


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def sample_agent(db_session: Session):
    """Public agent with a published version."""
    slug = f"rate-test-{uuid.uuid4()}"
    agent = models.Agent(
        slug=slug,
        name="Ratable Agent",
        description="An agent to rate",
        owner_id="owner-1",
        visibility="public",
    )
    db_session.add(agent)
    db_session.commit()

    version = models.AgentVersion(
        agent_id=agent.id,
        version="1.0.0",
        status=AgentStatus.PUBLISHED.value,
        manifest={
            "name": "Ratable Agent",
            "description": "An agent to rate",
            "category": "productivity",
            "entry_point": "main.py",
        },
        published_at=datetime.utcnow(),
    )
    db_session.add(version)
    db_session.commit()
    db_session.refresh(agent)
    return agent


# ------------------------------------------------------------------
# Agent rating — CRUD
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_rate_agent_creates_rating(db_session: Session, sample_agent):
    service = MarketplaceService(db_session)
    result = await service.rate_agent(
        sample_agent.id,
        "user-r1",
        RateAgentRequest(rating=4, review="Great agent!"),
    )
    assert result.rating == 4
    assert result.review == "Great agent!"
    assert result.agent_id == sample_agent.id
    assert result.user_id == "user-r1"


@pytest.mark.asyncio
async def test_rate_agent_upserts_existing(db_session: Session, sample_agent):
    service = MarketplaceService(db_session)
    await service.rate_agent(
        sample_agent.id, "user-r2", RateAgentRequest(rating=3)
    )
    updated = await service.rate_agent(
        sample_agent.id, "user-r2", RateAgentRequest(rating=5, review="Changed my mind")
    )
    assert updated.rating == 5
    assert updated.review == "Changed my mind"

    # Only one row should exist
    count = db_session.execute(
        select(models.AgentRating).where(
            models.AgentRating.agent_id == sample_agent.id,
            models.AgentRating.user_id == "user-r2",
        )
    ).scalars().all()
    assert len(count) == 1


@pytest.mark.asyncio
async def test_rate_agent_not_found(db_session: Session):
    service = MarketplaceService(db_session)
    with pytest.raises(Exception) as exc:
        await service.rate_agent(
            "nonexistent-id", "user-r3", RateAgentRequest(rating=5)
        )
    assert "not found" in str(exc.value).lower()


@pytest.mark.asyncio
async def test_delete_rating(db_session: Session, sample_agent):
    service = MarketplaceService(db_session)
    await service.rate_agent(
        sample_agent.id, "user-del", RateAgentRequest(rating=2)
    )
    assert await service.delete_agent_rating(sample_agent.id, "user-del") is True
    # Second delete should return False
    assert await service.delete_agent_rating(sample_agent.id, "user-del") is False


# ------------------------------------------------------------------
# Agent rating — aggregation
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_agent_ratings_summary(db_session: Session, sample_agent):
    service = MarketplaceService(db_session)
    await service.rate_agent(sample_agent.id, "u1", RateAgentRequest(rating=5))
    await service.rate_agent(sample_agent.id, "u2", RateAgentRequest(rating=3))
    await service.rate_agent(sample_agent.id, "u3", RateAgentRequest(rating=4))

    result = await service.get_agent_ratings(sample_agent.id)
    summary = result["summary"]
    assert summary.total_ratings == 3
    assert summary.average_rating == 4.0
    assert summary.distribution["5"] == 1
    assert summary.distribution["3"] == 1
    assert summary.distribution["4"] == 1
    assert summary.distribution["1"] == 0


@pytest.mark.asyncio
async def test_get_agent_ratings_empty(db_session: Session, sample_agent):
    service = MarketplaceService(db_session)
    result = await service.get_agent_ratings(sample_agent.id)
    assert result["summary"].total_ratings == 0
    assert result["summary"].average_rating == 0.0
    assert result["ratings"] == []


# ------------------------------------------------------------------
# Listing uses real average rating
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_listing_rating_from_user_reviews(db_session: Session, sample_agent):
    """AgentListing.rating should reflect actual user reviews, not manifest."""
    service = MarketplaceService(db_session)
    await service.rate_agent(sample_agent.id, "rev-u1", RateAgentRequest(rating=4))
    await service.rate_agent(sample_agent.id, "rev-u2", RateAgentRequest(rating=2))

    pv = next(v for v in sample_agent.versions if v.status == "published")
    listing = service._agent_to_listing(sample_agent, pv)
    assert listing.rating == 3.0  # (4+2)/2


# ------------------------------------------------------------------
# Sorting by rating
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_sort_by_rating(db_session: Session, sample_agent):
    """sort_by=rating should not raise (smoke test)."""
    from backend.src.modules.marketplace.models import MarketplaceSearchRequest

    service = MarketplaceService(db_session)
    await service.rate_agent(sample_agent.id, "sort-u", RateAgentRequest(rating=5))

    result = await service.search_agents(
        MarketplaceSearchRequest(sort_by="rating", limit=5)
    )
    # Just verify it doesn't crash and returns agent(s)
    assert result.total >= 0


# ------------------------------------------------------------------
# Usage summary — agent_count & max_agents
# ------------------------------------------------------------------


def test_usage_summary_includes_agent_fields(db_session: Session):
    """get_usage_summary should return agent_count and max_agents."""
    user_id = f"usage-user-{uuid.uuid4()}"
    period_start = datetime(2020, 1, 1)

    summary = usage_service.get_usage_summary(
        db_session, user_id=user_id, period_start=period_start, plan_id="free"
    )
    assert "agent_count" in summary
    assert "max_agents" in summary
    assert summary["max_agents"] == 3  # free plan limit
    assert summary["agent_count"] == 0


def test_usage_summary_counts_owned_agents(db_session: Session):
    """agent_count should include agents owned by the user."""
    user_id = f"owner-{uuid.uuid4()}"

    # Create two agents owned by this user
    for i in range(2):
        agent = models.Agent(
            slug=f"owned-{user_id}-{i}",
            name=f"Owned Agent {i}",
            owner_id=user_id,
            visibility="private",
        )
        db_session.add(agent)
    db_session.commit()

    summary = usage_service.get_usage_summary(
        db_session,
        user_id=user_id,
        period_start=datetime(2020, 1, 1),
        plan_id="pro",
    )
    assert summary["agent_count"] == 2
    assert summary["max_agents"] == 50  # pro plan


def test_usage_summary_counts_installed_agents(db_session: Session):
    """agent_count should include agents installed by the user."""
    user_id = f"installer-{uuid.uuid4()}"
    owner_id = f"someone-{uuid.uuid4()}"

    agent = models.Agent(
        slug=f"installable-{uuid.uuid4()}",
        name="Installable Agent",
        owner_id=owner_id,
        visibility="public",
    )
    db_session.add(agent)
    db_session.commit()

    installation = models.AgentInstallation(
        user_id=user_id,
        agent_id=agent.id,
        version="1.0.0",
        status="active",
    )
    db_session.add(installation)
    db_session.commit()

    summary = usage_service.get_usage_summary(
        db_session,
        user_id=user_id,
        period_start=datetime(2020, 1, 1),
        plan_id="enterprise",
    )
    assert summary["agent_count"] == 1
    assert summary["max_agents"] == 500  # enterprise plan
