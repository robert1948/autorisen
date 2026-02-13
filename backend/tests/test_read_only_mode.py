from __future__ import annotations

import os


def test_read_only_blocks_writes(client, monkeypatch):
    monkeypatch.setenv("READ_ONLY_MODE", "1")

    # Non-exempt POST paths should be blocked
    response = client.post("/api/flows/create", json={"name": "test"})

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Read-only mode: write operations are disabled."
    }

    monkeypatch.setenv("READ_ONLY_MODE", "0")
    response = client.get("/api/health")
    assert response.status_code == 200


def test_read_only_allows_auth(client, monkeypatch):
    """Auth endpoints must work even in read-only mode so users can log in."""
    monkeypatch.setenv("READ_ONLY_MODE", "1")

    response = client.post(
        "/api/auth/login", json={"email": "ro@example.com", "password": "x"}
    )

    # Should NOT get 403 — auth is exempt from read-only block
    assert response.status_code != 403
