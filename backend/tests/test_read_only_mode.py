from __future__ import annotations

import os


def test_read_only_blocks_writes(client, monkeypatch):
    monkeypatch.setenv("READ_ONLY_MODE", "1")

    response = client.post("/api/auth/login", json={"email": "ro@example.com", "password": "x"})

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Read-only mode: write operations are disabled."
    }

    monkeypatch.setenv("READ_ONLY_MODE", "0")
    response = client.get("/api/health")
    assert response.status_code == 200
