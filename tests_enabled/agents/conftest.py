"""
Test configuration and fixtures for CapeControl agent system.

Provides shared fixtures for database, API client, and mock services
across all agent test suites.
"""

import pytest
import asyncio
import os
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test_agents.db"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    return engine


@pytest.fixture
def test_db(test_engine) -> Generator[Session, None, None]:
    """Create test database session with cleanup."""
    # Import here to avoid circular imports during test discovery
    from backend.src.db.models import Base

    # Create tables
    Base.metadata.create_all(bind=test_engine)

    # Create session
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestSessionLocal()

    try:
        yield session
    finally:
        session.close()
        # Clean up tables
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(test_db):
    """FastAPI test client with database dependency override."""
    from backend.src.app import create_app
    from backend.src.core.database import get_db

    def override_get_db():
        return test_db

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db

    return TestClient(app)


@pytest.fixture
def mock_openai():
    """Mock OpenAI API responses for testing."""
    mock_client = AsyncMock()

    # Mock chat completion response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = (
        "This is a test response from the AI assistant."
    )

    mock_client.chat.completions.create.return_value = mock_response

    return mock_client


@pytest.fixture
def sample_agent_data():
    """Sample data for agent testing."""
    return {
        "agent": {
            "id": "test-agent",
            "slug": "test-agent",
            "name": "Test Agent",
            "description": "Test agent for automated testing",
            "visibility": "public",
        },
        "task_input": {
            "query": "How do I test automated workflows?",
            "context": {
                "current_page": "/dashboard/workflows",
                "user_role": "admin",
                "features_used": ["basic_workflows"],
            },
            "user_level": "intermediate",
            "preferred_format": "steps",
        },
        "expected_response": {
            "response": "To test automated workflows...",
            "suggestions": ["Learn about workflow testing", "Set up test environments"],
            "confidence_score": 0.85,
            "resources": [
                {
                    "title": "Workflow Testing Guide",
                    "url": "/docs/testing/workflows",
                    "type": "doc",
                }
            ],
        },
    }


@pytest.fixture
def sample_task_data():
    """Sample task execution data."""
    return {
        "id": 1,
        "title": "Test Task Execution",
        "description": "Testing task execution workflow",
        "agent_id": "test-agent",
        "user_id": "test-user",
        "status": "pending",
        "input_data": {"query": "test query"},
        "output_data": None,
        "error_message": None,
    }


@pytest.fixture
def mock_knowledge_base():
    """Mock knowledge base with test documents."""
    mock_kb = MagicMock()

    # Mock search results
    mock_kb.search.return_value = [
        {
            "id": "test-doc-1",
            "title": "Test Documentation",
            "content": "This is test documentation content.",
            "url": "/docs/test",
            "type": "doc",
            "keywords": ["test", "documentation"],
            "search_score": 0.9,
        }
    ]

    return mock_kb


@pytest.fixture
def auth_headers():
    """Authentication headers for API testing."""
    return {"Authorization": "Bearer test-token", "X-CSRF-Token": "test-csrf-token"}


# Utility functions for tests
class TestUtils:
    """Utility functions for agent testing."""

    @staticmethod
    def create_test_user(db: Session, user_id: str = "test-user"):
        """Create a test user in database."""
        # This would create a test user - implementation depends on User model
        pass

    @staticmethod
    def create_test_agent(db: Session, agent_data: dict):
        """Create a test agent in database."""
        # This would create a test agent - implementation depends on Agent model
        pass

    @staticmethod
    def create_test_task(db: Session, task_data: dict):
        """Create a test task in database."""
        # This would create a test task - implementation depends on Task model
        pass
