"""
Validation tests for the Agent registry schema (CHAT-002).

These tests exercise the SQLAlchemy models that back the agent registry to ensure
that uniqueness constraints, relationships, and cascading behaviour match the
expected production contract.
"""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.src.db.base import Base  # noqa: E402
from backend.src.db import models  # noqa: E402

# In-memory database dedicated to this suite.
engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
TestingSession = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True
)


@pytest.fixture(scope="module", autouse=True)
def _setup_schema() -> None:
    """Create the full model schema once for this module."""

    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session() -> Session:
    """Yield a clean session per test."""

    session: Session = TestingSession()
    try:
        yield session
        session.rollback()
    finally:
        session.close()


def _create_user(session: Session) -> models.User:
    """Helper to insert a minimal user record."""

    user = models.User(
        email=f"agent-{uuid.uuid4()}@example.com",
        hashed_password="test-hash",
        first_name="Test",
        last_name="User",
    )
    session.add(user)
    session.commit()
    return user


def test_agent_slug_is_unique(db_session: Session) -> None:
    """Agents enforce a globally unique slug for marketplace lookups."""

    owner = _create_user(db_session)

    first = models.Agent(
        owner_id=owner.id,
        slug="demo-agent",
        name="Demo Agent",
        visibility="private",
    )
    db_session.add(first)
    db_session.commit()

    duplicate = models.Agent(
        owner_id=owner.id,
        slug="demo-agent",
        name="Duplicate Agent",
        visibility="private",
    )
    db_session.add(duplicate)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_agent_versions_enforce_uniqueness_and_cascade(db_session: Session) -> None:
    """Agent versions must be unique per agent and cascade delete with parent."""

    owner = _create_user(db_session)
    agent = models.Agent(
        owner_id=owner.id,
        slug=f"agent-{uuid.uuid4().hex[:6]}",
        name="Versioned Agent",
        visibility="private",
    )
    db_session.add(agent)
    db_session.commit()

    version = models.AgentVersion(
        agent_id=agent.id,
        version="v1.0.0",
        manifest={"tools": ["demo"]},
        status="draft",
    )
    db_session.add(version)
    db_session.commit()

    # Attempt duplicate version string for same agent.
    dup_version = models.AgentVersion(
        agent_id=agent.id,
        version="v1.0.0",
        manifest={"tools": []},
        status="draft",
    )
    db_session.add(dup_version)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # Delete parent agent and ensure versions disappear.
    db_session.delete(agent)
    db_session.commit()

    remaining_versions = db_session.scalars(
        select(models.AgentVersion).where(models.AgentVersion.agent_id == agent.id)
    ).all()
    assert remaining_versions == []
