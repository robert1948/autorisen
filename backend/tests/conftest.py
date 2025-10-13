import os
import warnings
import pytest
from fastapi.testclient import TestClient
from backend.src.app import app

# Silence third-party deprecation noise during test runs (e.g. passlib->crypt)
warnings.filterwarnings("ignore", category=DeprecationWarning, module="passlib")

@pytest.fixture(scope="session", autouse=True)
def _env():
    os.environ.setdefault("ENV", "test")
    os.environ.setdefault("DATABASE_URL", "postgresql+psycopg2://devuser:devpass@localhost:5433/devdb")
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")

@pytest.fixture(scope="session")
def client():
    return TestClient(app)
