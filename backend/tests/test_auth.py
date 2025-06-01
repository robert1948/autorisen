import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_register_user():
    response = client.post("/api/register-user", json={
        "fullName": "Test User",
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword"
    })
    assert response.status_code in (201, 400)
    assert "message" in response.json()


def test_register_developer():
    response = client.post("/api/register-developer", json={
        "fullName": "Dev User",
        "company": "DevCo",
        "email": "devuser@example.com",
        "portfolio": "https://dev.co",
        "password": "devpassword"
    })
    assert response.status_code in (201, 400)
    assert "message" in response.json()
