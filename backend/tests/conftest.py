"""
Shared test fixtures and configuration
"""
import pytest
from unittest.mock import Mock, patch
import os

@pytest.fixture
def mock_ai_providers():
    """Mock all AI providers"""
    with patch.dict('sys.modules', {
        'openai': Mock(),
        'anthropic': Mock(),
        'google.generativeai': Mock(),
        'redis': Mock()
    }):
        yield

@pytest.fixture
def mock_database():
    """Mock database connections"""
    with patch('app.database.engine') as mock_engine:
        mock_engine.connect.return_value = Mock()
        yield mock_engine

@pytest.fixture
def test_env():
    """Set up test environment variables"""
    test_vars = {
        'DATABASE_URL': 'postgresql://test:test@localhost:5432/test',
        'SECRET_KEY': 'test-secret-key',
        'OPENAI_API_KEY': 'test-openai-key'
    }
    with patch.dict(os.environ, test_vars):
        yield test_vars
