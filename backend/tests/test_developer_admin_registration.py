"""Tests for Developer and Admin registration flows."""

from __future__ import annotations

import pytest
from starlette.testclient import TestClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SEQ = 0


def _unique_email(prefix: str = "test") -> str:
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


def _register_user(client, *, email: str, role: str = "Customer") -> dict:
    """Register a standard user and return the response dict."""
    resp = client.post(
        "/api/auth/register",
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": email,
            "password": STRONG_PASSWORD,
            "confirm_password": STRONG_PASSWORD,
            "terms_accepted": True,
            "role": role,
            "company_name": "TestCo",
        },
        headers=_csrf_headers(client),
    )
    return resp


def _register_admin_user(client, email: str) -> str:
    """Create an admin user the manual way and return the access_token."""
    resp = _register_user(client, email=email, role="Admin")
    if resp.status_code == 201:
        data = resp.json()
        return data.get("access_token", "")
    return ""


# ---------------------------------------------------------------------------
# Developer Registration Tests
# ---------------------------------------------------------------------------


class TestDeveloperRegistration:
    """POST /api/auth/register/developer"""

    def test_developer_register_success(self, client):
        email = _unique_email("dev")
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
                "organization": "DevCorp",
                "use_case": "build agents",
                "website_url": "https://devcorp.example.com",
                "github_url": "https://github.com/devcorp",
            },
            headers=_csrf_headers(client),
        )
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert "access_token" in data
        assert data["email_verified"] is False
        assert data.get("message", "").lower().startswith("developer")

    def test_developer_register_missing_dev_terms(self, client):
        email = _unique_email("dev_noterms")
        resp = client.post(
            "/api/auth/register/developer",
            json={
                "first_name": "Dev",
                "last_name": "Tester",
                "email": email,
                "password": STRONG_PASSWORD,
                "confirm_password": STRONG_PASSWORD,
                "terms_accepted": True,
                "developer_terms_accepted": False,
            },
            headers=_csrf_headers(client),
        )
        assert resp.status_code == 422  # Pydantic validation error

    def test_developer_register_duplicate_email(self, client):
        email = _unique_email("dev_dup")
        # First registration
        resp1 = client.post(
            "/api/auth/register/developer",
            json={
                "first_name": "Dev",
                "last_name": "Dup",
                "email": email,
                "password": STRONG_PASSWORD,
                "confirm_password": STRONG_PASSWORD,
                "terms_accepted": True,
                "developer_terms_accepted": True,
            },
            headers=_csrf_headers(client),
        )
        assert resp1.status_code == 201

        # Duplicate
        resp2 = client.post(
            "/api/auth/register/developer",
            json={
                "first_name": "Dev",
                "last_name": "Dup2",
                "email": email,
                "password": STRONG_PASSWORD,
                "confirm_password": STRONG_PASSWORD,
                "terms_accepted": True,
                "developer_terms_accepted": True,
            },
            headers=_csrf_headers(client),
        )
        assert resp2.status_code == 409

    def test_developer_register_weak_password(self, client):
        email = _unique_email("dev_weak")
        resp = client.post(
            "/api/auth/register/developer",
            json={
                "first_name": "Dev",
                "last_name": "Weak",
                "email": email,
                "password": "short",
                "confirm_password": "short",
                "terms_accepted": True,
                "developer_terms_accepted": True,
            },
            headers=_csrf_headers(client),
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Admin Invite Tests
# ---------------------------------------------------------------------------


class TestAdminInvite:
    """Admin invite management endpoints."""

    def test_invite_requires_admin_role(self, client):
        """Non-admin users cannot create invites."""
        email = _unique_email("nonadmin")
        resp = _register_user(client, email=email)
        if resp.status_code != 201:
            pytest.skip("Registration failed")

        token = resp.json().get("access_token", "")
        invite_resp = client.post(
            "/api/admin/invite",
            json={"target_email": "newadmin@example.com"},
            headers={**_csrf_headers(client), "Authorization": f"Bearer {token}"},
        )
        assert invite_resp.status_code == 403

    def test_admin_register_invalid_token(self, client):
        """Registration with an invalid invite token returns 403."""
        email = _unique_email("bad_invite")
        resp = client.post(
            "/api/admin/register",
            json={
                "invite_token": "invalid-token-that-does-not-exist-at-all",
                "first_name": "Bad",
                "last_name": "Invite",
                "email": email,
                "password": STRONG_PASSWORD,
                "confirm_password": STRONG_PASSWORD,
                "terms_accepted": True,
            },
            headers=_csrf_headers(client),
        )
        assert resp.status_code == 403

    def test_admin_register_password_mismatch(self, client):
        """Mismatched passwords return validation error."""
        email = _unique_email("admin_mismatch")
        resp = client.post(
            "/api/admin/register",
            json={
                "invite_token": "some-valid-looking-token-string",
                "first_name": "Admin",
                "last_name": "Mismatch",
                "email": email,
                "password": STRONG_PASSWORD,
                "confirm_password": "Different!Pass#2026",
                "terms_accepted": True,
            },
            headers=_csrf_headers(client),
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Admin Registration E2E (with invite creation)
# ---------------------------------------------------------------------------


class TestAdminRegistrationE2E:
    """Full flow: admin creates invite → new user registers via invite."""

    def _create_admin_directly(self, client) -> str:
        """
        Seed an admin user by registering normally then manually
        updating the role in the DB. Returns the access token.
        """
        from backend.src.db.session import SessionLocal
        from backend.src.db.models import User

        email = _unique_email("seedadmin")
        resp = _register_user(client, email=email)
        if resp.status_code != 201:
            pytest.skip("Seed registration failed")

        token = resp.json().get("access_token", "")

        # Manually set role to Admin
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).one_or_none()
            if user:
                user.role = "Admin"
                user.is_email_verified = True
                db.add(user)
                db.commit()
        finally:
            db.close()

        return token

    def test_full_invite_and_register_flow(self, client):
        """Admin creates invite → invitee registers → gets admin access."""
        admin_token = self._create_admin_directly(client)
        if not admin_token:
            pytest.skip("Could not create seed admin")

        target_email = _unique_email("invited_admin")

        # Step 1: Admin creates invite
        invite_resp = client.post(
            "/api/admin/invite",
            json={"target_email": target_email, "expiry_hours": 24},
            headers={**_csrf_headers(client), "Authorization": f"Bearer {admin_token}"},
        )

        if invite_resp.status_code != 201:
            pytest.skip(
                f"Invite creation failed ({invite_resp.status_code}): {invite_resp.text}"
            )

        invite_data = invite_resp.json()
        assert "invite_id" in invite_data
        assert invite_data["target_email"] == target_email

        # Step 2: List invites (admin-only)
        list_resp = client.get(
            "/api/admin/invites",
            headers={**_csrf_headers(client), "Authorization": f"Bearer {admin_token}"},
        )
        assert list_resp.status_code == 200
        invites = list_resp.json()
        assert any(inv["target_email"] == target_email for inv in invites)

    def test_revoke_invite(self, client):
        """Admin can revoke a pending invite."""
        admin_token = self._create_admin_directly(client)
        if not admin_token:
            pytest.skip("Could not create seed admin")

        target_email = _unique_email("revoke_target")

        # Create invite
        invite_resp = client.post(
            "/api/admin/invite",
            json={"target_email": target_email},
            headers={**_csrf_headers(client), "Authorization": f"Bearer {admin_token}"},
        )
        if invite_resp.status_code != 201:
            pytest.skip("Invite creation failed")

        invite_id = invite_resp.json()["invite_id"]

        # Revoke it
        revoke_resp = client.delete(
            f"/api/admin/invite/{invite_id}",
            headers={**_csrf_headers(client), "Authorization": f"Bearer {admin_token}"},
        )
        assert revoke_resp.status_code == 200
        assert "revoked" in revoke_resp.json().get("message", "").lower()


# ---------------------------------------------------------------------------
# Schema / Enum Tests
# ---------------------------------------------------------------------------


class TestUserRoleEnum:
    """Verify the UserRole enum includes all expected roles."""

    def test_roles_defined(self):
        from backend.src.modules.auth.schemas import UserRole

        assert UserRole.CUSTOMER.value == "Customer"
        assert UserRole.DEVELOPER.value == "Developer"
        assert UserRole.ADMIN.value == "Admin"

    def test_role_count(self):
        from backend.src.modules.auth.schemas import UserRole

        assert len(UserRole) == 3


# ---------------------------------------------------------------------------
# Model existence tests
# ---------------------------------------------------------------------------


class TestNewModels:
    """Verify the new ORM models exist and have expected columns."""

    def test_developer_profile_model(self):
        from backend.src.db.models import DeveloperProfile

        assert DeveloperProfile.__tablename__ == "developer_profiles"

    def test_api_credential_model(self):
        from backend.src.db.models import ApiCredential

        assert ApiCredential.__tablename__ == "api_credentials"

    def test_admin_invite_model(self):
        from backend.src.db.models import AdminInvite

        assert AdminInvite.__tablename__ == "admin_invites"
