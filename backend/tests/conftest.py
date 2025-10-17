import os
import warnings

import pytest

# Ensure test-specific environment before importing application modules.
os.environ.setdefault("ENV", "test")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("JWT_SECRET", "test-secret-key")

from fastapi.testclient import TestClient

from backend.src.app import app
from backend.src.db.base import Base
from backend.src.db.session import engine

# Ensure SQLite schema exists for integration tests.
if os.environ["DATABASE_URL"].startswith("sqlite"):
    Base.metadata.create_all(bind=engine)

# Silence third-party deprecation noise during test runs (e.g. passlib->crypt)
warnings.filterwarnings("ignore", category=DeprecationWarning, module="passlib")

@pytest.fixture(scope="session")
def client():
    return TestClient(app)
