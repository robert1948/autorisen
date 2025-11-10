"""Flow orchestration API tests (project task CHAT-003)."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_flows_api.db")
os.environ.setdefault("CHATKIT_APP_ID", "chatkit-test-app")
os.environ.setdefault("CHATKIT_SIGNING_KEY", "chatkit-test-signing-key")

from backend.src.db import models  # noqa: E402
from backend.src.db.base import Base  # noqa: E402
from backend.src.db.session import SessionLocal, engine, get_session  # noqa: E402
from backend.src.modules.auth.deps import get_verified_user  # noqa: E402
from backend.src.modules.flows.router import router as flows_router  # noqa: E402

TestingSessionLocal = sessionmaker(
    bind=engine, autocommit=False, autoflush=False, expire_on_commit=False
)


def _override_session() -> Generator[Session, None, None]:
    session: Session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def _build_app(user: models.User) -> FastAPI:
    app = FastAPI()
    app.include_router(flows_router, prefix="/api")
    app.dependency_overrides[get_session] = _override_session

    async def _user_override() -> models.User:
        return user

    app.dependency_overrides[get_verified_user] = _user_override
    return app


def _create_user() -> models.User:
    session = SessionLocal()
    try:
        user = models.User(
            email="flows@test.example.com",
            first_name="Flow",
            last_name="Runner",
            hashed_password="hash",
            company_name="CapeControl",
            role="Customer",
            is_email_verified=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        session.expunge(user)
        return user
    finally:
        session.close()


def _query_all(model) -> list:
    session = SessionLocal()
    try:
        return session.query(model).all()
    finally:
        session.close()


@pytest.fixture(autouse=True)
def reset_schema() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def test_run_flow_executes_tools_and_records_run():
    user = _create_user()
    app = _build_app(user)

    payload = {
        "placement": "onboarding",
        "tool_calls": [
            {
                "name": "onboarding.plan",
                "payload": {"goals": ["fast-launch"]},
            }
        ],
    }

    with TestClient(app) as client:
        resp = client.post("/api/flows/run", json=payload)
        list_resp = client.get("/api/flows/runs", params={"placement": "onboarding"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["placement"] == "onboarding"
    assert data["steps"]
    assert data["thread_id"]
    assert data["run_id"]
    assert list_resp.status_code == 200
    runs = list_resp.json()
    assert runs and runs[0]["id"] == data["run_id"]

    db_runs = _query_all(models.FlowRun)
    assert len(db_runs) == 1
    assert db_runs[0].steps and db_runs[0].thread_id == data["thread_id"]


def test_run_flow_requires_tool_calls():
    user = _create_user()
    app = _build_app(user)

    with TestClient(app) as client:
        resp = client.post(
            "/api/flows/run",
            json={"placement": "support", "tool_calls": []},
        )

    assert resp.status_code == 400
    assert "tool_calls" in resp.json()["detail"]
