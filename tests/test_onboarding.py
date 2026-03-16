"""Tests for onboarding API flow."""

from backend.src.modules.auth.schemas import LoginResponse


def _register_user(client, email: str):
    register_payload = {
        "first_name": "Onboard",
        "last_name": "Tester",
        "email": email,
        "password": "Password123!@#",
        "confirm_password": "Password123!@#",
        "terms_accepted": True,
        "role": "Customer",
        "company_name": "CapeControl",
        "recaptcha_token": "dummy",
    }
    csrf_resp = client.get("/api/auth/csrf")
    assert csrf_resp.status_code == 200
    csrf_token = csrf_resp.json()["token"]
    headers = {"X-CSRF-Token": csrf_token}

    reg_resp = client.post("/api/auth/register", json=register_payload, headers=headers)
    assert reg_resp.status_code == 201
    data = reg_resp.json()
    model = LoginResponse(**data)
    return model.access_token, headers


def _register_user_unverified(client, email: str):
    payload_step1 = {
        "first_name": "Onboard",
        "last_name": "Tester",
        "email": email,
        "password": "Password123!@#",
        "confirm_password": "Password123!@#",
        "terms_accepted": True,
        "role": "Customer",
        "recaptcha_token": "dummy",
    }
    csrf_resp = client.get("/api/auth/csrf")
    assert csrf_resp.status_code == 200
    csrf_token = csrf_resp.json()["token"]
    csrf_headers = {"X-CSRF-Token": csrf_token}

    step1_resp = client.post(
        "/api/auth/register/step1", json=payload_step1, headers=csrf_headers
    )
    assert step1_resp.status_code == 201
    temp_token = step1_resp.json()["temp_token"]

    step2_payload = {"company_name": "CapeControl", "profile": {}}
    step2_headers = {**csrf_headers, "Authorization": f"Bearer {temp_token}"}
    step2_resp = client.post(
        "/api/auth/register/step2", json=step2_payload, headers=step2_headers
    )
    assert step2_resp.status_code == 200
    access_token = step2_resp.json()["access_token"]
    return access_token


def test_onboarding_status_empty(client):
    token, _headers = _register_user(client, "onboard-status@example.com")
    auth_headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/api/onboarding/status", headers=auth_headers)
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["session"] is None
    assert payload["steps"] == []
    assert payload["progress"] == 0


def test_onboarding_start_and_complete_step(client):
    token, csrf_headers = _register_user(client, "onboard-start@example.com")
    headers = {
        **csrf_headers,
        "Authorization": f"Bearer {token}",
    }

    start_resp = client.post("/api/onboarding/start", headers=headers)
    assert start_resp.status_code == 200
    start_payload = start_resp.json()
    assert start_payload["session"] is not None
    assert start_payload["steps"]

    step_resp = client.post("/api/onboarding/steps/welcome/complete", headers=headers)
    assert step_resp.status_code == 200
    step_payload = step_resp.json()
    assert step_payload["step"]["step_key"] == "welcome"
    assert step_payload["step"]["state"]["status"] == "completed"


def test_onboarding_profile_update(client):
    token, csrf_headers = _register_user(client, "onboard-profile@example.com")
    headers = {
        **csrf_headers,
        "Authorization": f"Bearer {token}",
    }

    payload = {
        "first_name": "Sky",
        "last_name": "Harbor",
        "company_name": "CapeControl",
        "role": "Customer",
    }
    resp = client.patch("/api/onboarding/profile", json=payload, headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["profile"]["first_name"] == "Sky"


def test_onboarding_complete_requires_verified_email(client):
    token = _register_user_unverified(client, "onboard-unverified@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/api/onboarding/complete", headers=headers)
    assert resp.status_code == 403
    assert "Email verification is required" in resp.json()["detail"]
