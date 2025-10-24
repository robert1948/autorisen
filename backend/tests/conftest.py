# backend/tests/conftest.py
import os
import asyncio
from pathlib import Path
from typing import Any, Optional, Type

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.engine import make_url

try:
    from asgi_lifespan import LifespanManager  # type: ignore[import]
except ImportError:

    class LifespanManager:
        """Minimal lifespan manager similar to asgi_lifespan."""

        def __init__(self, app):
            self._app = app
            self._context: Optional[Any] = None

        async def __aenter__(self):
            lifespan_context = self._app.router.lifespan_context(self._app)
            self._context = lifespan_context
            await lifespan_context.__aenter__()
            return self._app

        async def __aexit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc: Optional[BaseException],
            tb,
        ) -> None:
            if self._context is not None:
                await self._context.__aexit__(exc_type, exc, tb)


# ---- Test environment flags (set BEFORE importing app) ----
os.environ.setdefault("ENV", "test")
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")  # disable limiter in tests
os.environ.setdefault("RATE_LIMIT_BACKEND", "memory")  # force in-memory limiter
os.environ.setdefault("CSRF_ENABLED", "true")
os.environ.setdefault("DISABLE_RECAPTCHA", "true")
os.environ.setdefault("EMAIL_TOKEN_SECRET", "unit-test-secret")
os.environ.setdefault("FROM_EMAIL", "noreply@example.com")
os.environ.setdefault("SMTP_HOST", "localhost")
os.environ.setdefault("SMTP_USERNAME", "test-user")
os.environ.setdefault("SMTP_PASSWORD", "test-pass")
os.environ.setdefault("DATABASE_URL", "sqlite:////tmp/autolocal_test.db")

from backend.src.app import app  # noqa: E402  (import after env is set)


def _reset_sqlite_db_file() -> None:
    """Remove the on-disk sqlite file before test session starts."""
    db_url = os.getenv("DATABASE_URL", "")
    if not db_url:
        return
    try:
        url = make_url(db_url)
    except Exception:
        return
    if url.get_backend_name() != "sqlite":
        return
    database = url.database
    if not database or database == ":memory:":
        return
    db_path = Path(database)
    if not db_path.is_absolute():
        project_root = Path(__file__).resolve().parents[2]
        db_path = (project_root / database).resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()


# ---- Pytest / AnyIO plumbing ----


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def started_app():
    # Reset DB ONCE, then run full startup/shutdown exactly once for the session
    _reset_sqlite_db_file()
    async with LifespanManager(app):
        yield app


# ---- Primary client for async tests ----


@pytest.fixture()
async def client(started_app):
    """
    Async HTTPX client bound to the ASGI app (no network).
    Single lifespan (from started_app); no DB reset here to avoid file locks.
    """
    transport = ASGITransport(app=started_app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        follow_redirects=True,
        trust_env=False,  # ignore proxies; prevents odd hangs
        timeout=30.0,  # hard cap to avoid indefinite stalls
    ) as ac:
        yield ac


# ---- Helpers / convenience ----


@pytest.fixture()
async def csrf_token(client: AsyncClient) -> str:
    """Fetch CSRF token if your app exposes an endpoint for it."""
    r = await client.get("/api/auth/csrf")
    data = (
        r.json()
        if r.headers.get("content-type", "").startswith("application/json")
        else {}
    )
    return data.get("csrf_token") or data.get("token") or ""


# Optional: provide a synchronous client without conflicting with 'client'
# (use sparingly; it manages its own lifespan to avoid double-start with session app)
@pytest.fixture()
def sync_client():
    from fastapi.testclient import TestClient

    # NOTE: do NOT call _reset_sqlite_db_file() here; DB is already in use.
    with TestClient(app, base_url="http://test") as tc:
        yield tc
