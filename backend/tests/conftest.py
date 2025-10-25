# backend/tests/conftest.py
import os
from pathlib import Path
import pytest
from httpx import AsyncClient, ASGITransport
from starlette.testclient import TestClient

# ------------------------------------------------------------
# Test runtime configuration
# ------------------------------------------------------------


@pytest.fixture(scope="session", autouse=True)
def test_env():
    """Provide required env vars for the app under test."""
    defaults = {
        # Core env
        "ENV": "test",
        "TESTING": "1",
        "RUN_DB_MIGRATIONS_ON_STARTUP": "1",
        # DB (sqlite file for tests)
        "DATABASE_URL": "sqlite:////tmp/autolocal_test.db",
        # Auth/JWT secrets (harmless test values)
        "SECRET_KEY": "dev-test-secret",
        "JWT_SECRET": "dev-test-secret",
        "JWT_SECRET_KEY": "dev-test-secret",
        "JWT_ALGORITHM": "HS256",
        # Email config (dummy but structurally valid)
        "EMAIL_TOKEN_SECRET": "dev-token-secret",
        "FROM_EMAIL": "noreply@example.test",
        "SMTP_USERNAME": "user",
        "SMTP_PASSWORD": "pass",
        "SMTP_HOST": "localhost",
        "SMTP_PORT": "2525",
        "SMTP_TLS": "false",
        "SMTP_SSL": "false",
        # Test-mode toggles (if your app supports them)
        "AUTH_TEST_MODE": "1",
        "AUTH_REQUIRE_EMAIL_VERIFICATION": "0",
        "DISABLE_EMAIL_SENDING": "1",
        "DISABLE_EXTERNAL_CALLS": "1",
        "DISABLE_RECAPTCHA": "true",
        # Rate limit backend to in-memory for deterministic tests
        "RATE_LIMIT_BACKEND": "memory",
    }
    for k, v in defaults.items():
        os.environ.setdefault(k, str(v))

    db_url = os.getenv("ALEMBIC_DATABASE_URL") or os.getenv("DATABASE_URL")
    if db_url and db_url.startswith("sqlite"):
        db_path: Path | None = None
        if db_url.startswith("sqlite:////"):
            db_path = Path("/" + db_url.split("sqlite:////", 1)[1])
        elif db_url.startswith("sqlite:///"):
            candidate = db_url.split("sqlite:///", 1)[1]
            if candidate != ":memory:":
                db_path = Path(candidate)

        if db_path and db_path.name != ":memory:":
            try:
                if not db_path.is_absolute() and not db_path.parent.exists():
                    db_path.parent.mkdir(parents=True, exist_ok=True)
                if db_path.exists():
                    db_path.unlink()
            except OSError:
                # Best-effort cleanup; the Alembic runner will create the DB file
                pass


def _load_app():
    """Lazy-import the FastAPI app after env is prepared."""
    try:
        from backend.src.app import app  # import here, not at module top
    except Exception as e:
        raise RuntimeError(f"Failed to import FastAPI app: {e}")
    return app


# ------------------------------------------------------------
# anyio backend (enables async tests)
# ------------------------------------------------------------


@pytest.fixture(scope="session")
def anyio_backend():
    # Allows @pytest.mark.anyio tests to run on asyncio
    return "asyncio"


# ------------------------------------------------------------
# Sync client (for non-async tests) with a tiny adapter so
# kwargs match httpx style (allow_redirects -> follow_redirects).
# ------------------------------------------------------------


def _map_redirect_kw(kwargs):
    # Map requests-style allow_redirects -> httpx follow_redirects
    if "allow_redirects" in kwargs:
        kwargs["follow_redirects"] = kwargs.pop("allow_redirects")
    return kwargs


class SyncClientAdapter:
    """Wrap TestClient and normalize kwargs; minimal httpx-like surface."""

    def __init__(self, client: TestClient):
        self._c = client

    def get(self, url, **kwargs):
        return self._c.get(url, **_map_redirect_kw(kwargs))

    def post(self, url, **kwargs):
        return self._c.post(url, **_map_redirect_kw(kwargs))

    def put(self, url, **kwargs):
        return self._c.put(url, **_map_redirect_kw(kwargs))

    def patch(self, url, **kwargs):
        return self._c.patch(url, **_map_redirect_kw(kwargs))

    def delete(self, url, **kwargs):
        return self._c.delete(url, **_map_redirect_kw(kwargs))

    def options(self, url, **kwargs):
        return self._c.options(url, **_map_redirect_kw(kwargs))

    @property
    def cookies(self):
        return self._c.cookies

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return self._c.__exit__(*a)


@pytest.fixture(scope="session")
def client(test_env):
    app = _load_app()
    with TestClient(app) as c:
        yield SyncClientAdapter(c)


# ------------------------------------------------------------
# Async client (for async tests)
# ------------------------------------------------------------


@pytest.fixture
async def rate_async_client(test_env):
    from httpx import AsyncClient, ASGITransport
    from backend.src.app import app

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", follow_redirects=True
    ) as c:
        yield c
