import os

import sqlalchemy as sa

from backend.src.app import record_build_if_new
from backend.src.db.models import AppBuild
from backend.src.db.session import SessionLocal


def _clear_app_builds() -> None:
    with SessionLocal() as session:
        session.execute(sa.delete(AppBuild))
        session.commit()


def test_api_version_env_fallback_when_db_empty(client, monkeypatch):
    _clear_app_builds()
    monkeypatch.setenv("GIT_SHA", "envsha")
    monkeypatch.setenv("BUILD_EPOCH", "")
    monkeypatch.setenv("APP_BUILD_VERSION", "488")

    response = client.get("/api/version")
    assert response.status_code == 200
    payload = response.json()

    assert payload.get("source") == "env"
    assert payload.get("versionLabel") == "Build 488"
    assert payload.get("gitSha") == "envsha"


def test_api_version_prefers_db_record(client, monkeypatch):
    _clear_app_builds()
    monkeypatch.setenv("GIT_SHA", "")
    monkeypatch.setenv("BUILD_EPOCH", "")
    monkeypatch.setenv("APP_BUILD_VERSION", "")

    with SessionLocal() as session:
        session.add(
            AppBuild(
                app_name="autorisen",
                version_label="Build 999",
                build_number=999,
                git_sha="dbsha",
                build_epoch=999,
            )
        )
        session.commit()

    response = client.get("/api/version")
    assert response.status_code == 200
    payload = response.json()

    assert payload.get("source") == "db"
    assert payload.get("versionLabel") == "Build 999"
    assert payload.get("gitSha") == "dbsha"


def test_record_build_if_new_idempotent(monkeypatch):
    _clear_app_builds()
    monkeypatch.setenv("GIT_SHA", "idempotent")
    monkeypatch.setenv("BUILD_EPOCH", "123")
    monkeypatch.setenv("APP_BUILD_VERSION", "488")

    record_build_if_new()
    record_build_if_new()

    with SessionLocal() as session:
        rows = (
            session.query(AppBuild)
            .filter(AppBuild.git_sha == "idempotent", AppBuild.build_epoch == 123)
            .all()
        )

    assert len(rows) == 1
    assert rows[0].build_number == 1


def test_record_build_if_new_auto_increment(monkeypatch):
    _clear_app_builds()

    with SessionLocal() as session:
        session.add(
            AppBuild(
                app_name="autorisen",
                version_label="Build 488",
                build_number=488,
                git_sha="oldsha",
                build_epoch=111,
            )
        )
        session.commit()

    monkeypatch.setenv("GIT_SHA", "newsha")
    monkeypatch.setenv("BUILD_EPOCH", "222")
    monkeypatch.setenv("APP_BUILD_VERSION", "488")

    record_build_if_new()

    with SessionLocal() as session:
        record = (
            session.query(AppBuild)
            .filter(AppBuild.git_sha == "newsha", AppBuild.build_epoch == 222)
            .one()
        )

    assert record.build_number == 489
    assert record.version_label == "Build 489"
