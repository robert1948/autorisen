from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import delete

from backend.src.db import models
from backend.src.db.base import Base
from backend.src.db.session import SessionLocal, engine
from backend.src.modules.auth import service
from backend.src.services.security import create_jwt


@pytest.fixture(scope="module", autouse=True)
def _prepare_schema():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture
def db_session():
    with SessionLocal() as session:
        yield session
        session.execute(delete(models.User))
        session.commit()


def _issue_access_token(user: models.User, *, token_version: int | None = None, **extra):
    payload = {
        "sub": user.email,
        "user_id": user.id,
        "role": user.role,
        "purpose": service.ACCESS_TOKEN_PURPOSE,
        "jti": str(uuid.uuid4()),
        "token_version": token_version
        if token_version is not None
        else service._token_version_for(user),
    }
    payload.update(extra)
    token, _ = create_jwt(payload, expires_in=60)
    return token


def _create_user(session: SessionLocal, **overrides) -> models.User:
    now = datetime.now(timezone.utc)
    user = models.User(
        email="valid@example.com",
        first_name="Valid",
        last_name="User",
        full_name="Valid User",
        role="Customer",
        hashed_password="hashed",
        is_active=True,
        password_changed_at=now,
        token_version=overrides.get("token_version", 0),
        **{k: v for k, v in overrides.items() if k not in {"token_version"}},
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def test_current_user_accepts_valid_access_token(db_session):
    user = _create_user(db_session, token_version=2)
    token = _issue_access_token(user)

    fetched = service.current_user(db_session, token)

    assert fetched.id == user.id


def test_current_user_rejects_wrong_purpose(db_session):
    user = _create_user(db_session)
    token = _issue_access_token(user, purpose="refresh")

    with pytest.raises(ValueError):
        service.current_user(db_session, token)


def test_current_user_rejects_mismatched_token_version(db_session):
    user = _create_user(db_session, token_version=1)
    token = _issue_access_token(user, token_version=5)

    with pytest.raises(ValueError):
        service.current_user(db_session, token)


def test_current_user_rejects_mismatched_user_id(db_session):
    user = _create_user(db_session, token_version=3)
    token = _issue_access_token(user, user_id=str(uuid.uuid4()))

    with pytest.raises(ValueError):
        service.current_user(db_session, token)
