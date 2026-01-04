"""Pytest fixtures shared across backend test modules."""

from __future__ import annotations

import inspect
import os
import pathlib
import sys
from typing import Any, Dict

import anyio
import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from starlette.testclient import TestClient

# ------------------------------------------------------------------
# Stable test environment configuration
# ------------------------------------------------------------------

TEST_DB_FILE = pathlib.Path("/tmp/autolocal_test.db")
TEST_DB_URL = f"sqlite:////{TEST_DB_FILE}"

os.environ.setdefault("ENV", "test")
os.environ.setdefault("DATABASE_URL", TEST_DB_URL)
os.environ.setdefault("ALEMBIC_DATABASE_URL", TEST_DB_URL)
os.environ.setdefault("DISABLE_RECAPTCHA", "true")
os.environ.setdefault("RUN_DB_MIGRATIONS_ON_STARTUP", "0")
os.environ.setdefault("RATE_LIMIT_BACKEND", "memory")
os.environ.setdefault("DISABLE_RATE_LIMIT", "1")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("JWT_SECRET", "test-secret-key")
os.environ.setdefault("EMAIL_TOKEN_SECRET", "test-email-token")
os.environ.setdefault("FROM_EMAIL", "CapeControl Test <no-reply@test.local>")
os.environ.setdefault("SMTP_HOST", "localhost")
os.environ.setdefault("SMTP_USERNAME", "tester")
os.environ.setdefault("SMTP_PASSWORD", "tester")
os.environ.setdefault("SMTP_USE_TLS", "0")
os.environ.setdefault("SMTP_USE_SSL", "0")

# Ensure repository root is importable when running `pytest` from any CWD.
REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Import after env is set
from backend.src.app import app as _app  # type: ignore  # noqa: E402
from backend.src.db import models as db_models  # noqa: E402
from backend.src.db.session import engine  # noqa: E402


def _ensure_fastapi_app(candidate: Any) -> FastAPI:
    """
    Accept either:
      - a FastAPI instance, or
      - a factory function returning FastAPI (sync or async).
    Resolve to a FastAPI instance.
    """
    if isinstance(candidate, FastAPI):
        return candidate

    if callable(candidate):
        if inspect.iscoroutinefunction(candidate):
            return anyio.run(candidate)  # async factory
        # sync factory
        maybe_app = candidate()
        if isinstance(maybe_app, FastAPI):
            return maybe_app

    raise RuntimeError(
        "backend.src.app.app must be a FastAPI instance or a factory (sync/async) "
        "returning FastAPI."
    )


def _map_redirect_kw(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Translate requests-style kwargs into httpx equivalents."""
    if "allow_redirects" in kwargs:
        kwargs["follow_redirects"] = kwargs.pop("allow_redirects")
    return kwargs


class SyncClientAdapter:
    """Expose a requests-like interface backed by Starlette TestClient."""

    def __init__(self, test_client: TestClient):
        self._c = test_client

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

    @property
    def cookies(self):
        return self._c.cookies


# ------------------------------------------------------------------
# DB helpers
# ------------------------------------------------------------------


def _reset_sqlite_db_file() -> None:
    """Drop and recreate the SQLite file for a clean schema."""
    engine.dispose()
    if TEST_DB_FILE.exists():
        TEST_DB_FILE.unlink()
    TEST_DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    db_models.Base.metadata.create_all(engine)


# ------------------------------------------------------------------
# Session-scoped bootstrapping
# ------------------------------------------------------------------


@pytest.fixture(scope="session", autouse=True)
def _prepare_test_db():
    """Ensure the SQLite test database starts from a clean slate."""
    _reset_sqlite_db_file()
    yield
    # No teardown required for disposable SQLite file


@pytest.fixture(scope="session", name="app")
def _app_fixture() -> FastAPI:
    """Expose a FastAPI app instance, resolving factory patterns if needed."""
    return _ensure_fastapi_app(_app)


# ------------------------------------------------------------------
# Client fixtures
# ------------------------------------------------------------------


@pytest.fixture(name="client")
def _client_fixture(app: FastAPI):
    """Synchronous client used by the majority of tests (requests-like API)."""
    with TestClient(app) as tc:
        yield SyncClientAdapter(tc)


@pytest.fixture(name="rate_async_client")
async def _rate_async_client_fixture(app: FastAPI):
    """Async httpx client with consistent settings for anyio/async tests."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        follow_redirects=True,
    ) as ac:
        yield ac


@pytest.fixture(name="async_client")
async def _async_client_fixture(rate_async_client: AsyncClient):
    """Alias to maintain backwards compatibility in individual tests."""
    yield rate_async_client


# ------------------------------------------------------------------
# Email capture (test sink)
# ------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _email_sink(monkeypatch, app):
    """
    Capture all outgoing email during tests, without touching real SMTP.
    Works for any code path that uses smtplib.SMTP.

    Exposes the captured messages via:
        app.state.test_emails
        app.state.mailbox
        app.state.outbox
    Each item is a dict: {"from": str, "to": list[str], "msg": str}
    """
    import smtplib

    sent: list[dict[str, Any]] = []

    class _DummySMTP:
        def __init__(self, *a, **kw):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def starttls(self, *_args, **_kwargs):
            pass

        def login(self, *_args, **_kwargs):
            pass

        # smtplib may call either .sendmail or .send_message
        def sendmail(self, from_addr, to_addrs, msg, *_args, **_kwargs):
            # normalize to a list for convenience
            if isinstance(to_addrs, str):
                to_list = [to_addrs]
            else:
                to_list = list(to_addrs)
            sent.append({"from": from_addr, "to": to_list, "msg": msg})

        def send_message(self, msg, *args, **kwargs):
            # Fallback if library uses EmailMessage
            # Extract from/to from args/kwargs to mimic smtplib signature
            # send_message(msg, from_addr=None, to_addrs=None, ...)

            from_addr = kwargs.get("from_addr")
            if from_addr is None and len(args) > 0:
                from_addr = args[0]

            to_addrs = kwargs.get("to_addrs")
            if to_addrs is None and len(args) > 1:
                to_addrs = args[1]

            from_addr = from_addr or msg.get("From", "")
            to_field = to_addrs or msg.get_all("To", []) or []
            if isinstance(to_field, str):
                to_list = [to_field]
            else:
                to_list = list(to_field)
            sent.append({"from": from_addr, "to": to_list, "msg": msg.as_string()})
            return {}

    # Patch smtplib.SMTP to our dummy
    monkeypatch.setattr(smtplib, "SMTP", _DummySMTP, raising=True)

    # Make it discoverable to tests in several conventional places
    app.state.test_emails = sent
    app.state.mailbox = sent
    app.state.outbox = sent

    # Encourage code paths to “send” email in tests
    os.environ.setdefault("EMAILS_ENABLED", "1")

    yield

    # (no teardown needed)
