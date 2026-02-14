"""Tests for the Developer Dashboard module (/api/dev/*)."""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SEQ = 1000  # offset to avoid collision with other test files


def _unique_email(prefix: str = "devtest") -> str:
    global _SEQ
    _SEQ += 1
    return f"{prefix}_{_SEQ}@example.com"


STRONG_PASSWORD = "Str0ng!Pass#2026"


def _csrf_headers(client) -> dict:
    """Fetch a valid CSRF token from the server."""
    resp = client.get("/api/auth/csrf")
    assert resp.status_code == 200, resp.text
    token = resp.json()["csrf_token"]
    return {"X-CSRF-Token": token}


def _register_developer(client, email: str) -> str:
    """Register a developer user and return the access_token."""
    resp = client.post(
        "/api/auth/register/developer",
        json={
            "first_name": "Dev",
            "last_name": "Tester",
            "email": email,
            "password": STRONG_PASSWORD,
            "confirm_password": STRONG_PASSWORD,
            "terms_accepted": True,
            "developer_terms_accepted": True,
            "organization": "TestDevOrg",
            "use_case": "testing",
        },
        headers=_csrf_headers(client),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["access_token"]


def _register_customer(client, email: str) -> str:
    """Register a standard Customer user and return the access_token."""
    resp = client.post(
        "/api/auth/register",
        json={
            "first_name": "Cust",
            "last_name": "User",
            "email": email,
            "password": STRONG_PASSWORD,
            "confirm_password": STRONG_PASSWORD,
            "terms_accepted": True,
            "role": "Customer",
            "company_name": "CustCo",
        },
        headers=_csrf_headers(client),
    )
    assert resp.status_code == 201, resp.text
    return resp.json().get("access_token", "")


def _dev_auth_headers(client, token: str) -> dict:
    """CSRF + Bearer headers combined."""
    return {**_csrf_headers(client), "Authorization": f"Bearer {token}"}


def _verify_email(client, email: str):
    """Manually verify a user's email in the test DB."""
    from backend.src.db.session import SessionLocal
    from backend.src.db.models import User

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).one_or_none()
        if user:
            user.is_email_verified = True
            db.add(user)
            db.commit()
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Developer Profile Tests
# ---------------------------------------------------------------------------


class TestDeveloperProfile:
    """GET/PATCH /api/dev/profile"""

    def test_get_profile_success(self, client):
        email = _unique_email("devprofile")
        token = _register_developer(client, email)
        headers = _dev_auth_headers(client, token)

        # Verify email so require_roles("developer") passes (get_verified_user)
        _verify_email(client, email)

        resp = client.get("/api/dev/profile", headers=headers)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["email"] == email
        assert data["organization"] == "TestDevOrg"
        assert data["use_case"] == "testing"

    def test_get_profile_requires_developer_role(self, client):
        """Customer users cannot access developer profile."""
        email = _unique_email("custprofile")
        token = _register_customer(client, email)
        _verify_email(client, email)

        headers = _dev_auth_headers(client, token)
        resp = client.get("/api/dev/profile", headers=headers)
        assert resp.status_code == 403

    def test_update_profile(self, client):
        email = _unique_email("devupdate")
        token = _register_developer(client, email)
        _verify_email(client, email)

        headers = _dev_auth_headers(client, token)
        resp = client.patch(
            "/api/dev/profile",
            json={"organization": "UpdatedOrg", "use_case": "production"},
            headers=headers,
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["organization"] == "UpdatedOrg"
        assert data["use_case"] == "production"


# ---------------------------------------------------------------------------
# API Credentials Tests
# ---------------------------------------------------------------------------


class TestApiCredentials:
    """GET/POST/DELETE /api/dev/api-keys"""

    def test_list_api_keys_empty(self, client):
        email = _unique_email("devkeys_empty")
        token = _register_developer(client, email)
        _verify_email(client, email)

        headers = _dev_auth_headers(client, token)
        resp = client.get("/api/dev/api-keys", headers=headers)
        assert resp.status_code == 200, resp.text
        assert resp.json() == []

    def test_create_api_key(self, client):
        email = _unique_email("devkeys_create")
        token = _register_developer(client, email)
        _verify_email(client, email)

        headers = _dev_auth_headers(client, token)
        resp = client.post(
            "/api/dev/api-keys",
            json={"label": "My Test Key"},
            headers=headers,
        )
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert "client_id" in data
        assert "client_secret" in data
        assert data["client_id"].startswith("cc_")
        assert data["label"] == "My Test Key"
        assert "Store the client_secret" in data["message"]

    def test_create_api_key_requires_email_verification(self, client):
        """Unverified developers cannot provision API keys."""
        email = _unique_email("devkeys_unverified")
        token = _register_developer(client, email)
        # Do NOT verify email

        headers = _dev_auth_headers(client, token)
        resp = client.post(
            "/api/dev/api-keys",
            json={"label": "Should Fail"},
            headers=headers,
        )
        # get_verified_user raises 403 before we even reach the handler
        assert resp.status_code == 403

    def test_create_and_list_api_key(self, client):
        email = _unique_email("devkeys_list")
        token = _register_developer(client, email)
        _verify_email(client, email)

        headers = _dev_auth_headers(client, token)

        # Create
        client.post(
            "/api/dev/api-keys",
            json={"label": "Key One"},
            headers=headers,
        )

        # List
        resp = client.get("/api/dev/api-keys", headers=headers)
        assert resp.status_code == 200
        keys = resp.json()
        assert len(keys) >= 1
        assert keys[0]["label"] == "Key One"
        assert keys[0]["is_active"] is True
        # Secret should NOT appear in list response
        assert "client_secret" not in keys[0]

    def test_revoke_api_key(self, client):
        email = _unique_email("devkeys_revoke")
        token = _register_developer(client, email)
        _verify_email(client, email)

        headers = _dev_auth_headers(client, token)

        # Create
        create_resp = client.post(
            "/api/dev/api-keys",
            json={"label": "Revokable"},
            headers=headers,
        )
        assert create_resp.status_code == 201
        cred_id = create_resp.json()["id"]

        # Revoke
        revoke_resp = client.delete(
            f"/api/dev/api-keys/{cred_id}",
            headers=headers,
        )
        assert revoke_resp.status_code == 200
        assert "revoked" in revoke_resp.json()["message"].lower()

        # Verify it shows as revoked in list
        list_resp = client.get("/api/dev/api-keys", headers=headers)
        keys = list_resp.json()
        revoked_key = [k for k in keys if k["id"] == cred_id][0]
        assert revoked_key["is_active"] is False
        assert revoked_key["revoked_at"] is not None

    def test_revoke_nonexistent_key(self, client):
        email = _unique_email("devkeys_bad_revoke")
        token = _register_developer(client, email)
        _verify_email(client, email)

        headers = _dev_auth_headers(client, token)
        resp = client.delete(
            "/api/dev/api-keys/fake-id-does-not-exist",
            headers=headers,
        )
        assert resp.status_code == 400

    def test_customer_cannot_access_api_keys(self, client):
        email = _unique_email("cust_apikeys")
        token = _register_customer(client, email)
        _verify_email(client, email)

        headers = _dev_auth_headers(client, token)
        resp = client.get("/api/dev/api-keys", headers=headers)
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Usage / Stats Tests
# ---------------------------------------------------------------------------


class TestDeveloperUsage:
    """GET /api/dev/usage"""

    def test_usage_stats(self, client):
        email = _unique_email("devusage")
        token = _register_developer(client, email)
        _verify_email(client, email)

        headers = _dev_auth_headers(client, token)

        # Create one key
        client.post(
            "/api/dev/api-keys",
            json={"label": "Stats Key"},
            headers=headers,
        )

        resp = client.get("/api/dev/usage", headers=headers)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["total_api_keys"] >= 1
        assert data["active_api_keys"] >= 1
        assert data["revoked_api_keys"] == 0
        assert data["email_verified"] is True

    def test_usage_requires_developer_role(self, client):
        email = _unique_email("custusage")
        token = _register_customer(client, email)
        _verify_email(client, email)

        headers = _dev_auth_headers(client, token)
        resp = client.get("/api/dev/usage", headers=headers)
        assert resp.status_code == 403
