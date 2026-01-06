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
    assert audit_event.payload["version"] == "1.0.0"
    assert audit_event.payload["installation_id"] == installation.id


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
