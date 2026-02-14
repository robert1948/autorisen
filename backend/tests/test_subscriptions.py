"""Tests for the Subscription module (/api/subscriptions/*)."""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SEQ = 2000  # offset to avoid collision with other test files

STRONG_PASSWORD = "Str0ng!Pass#2026"


def _unique_email(prefix: str = "subtest") -> str:
    global _SEQ
    _SEQ += 1
    return f"{prefix}_{_SEQ}@example.com"


def _csrf_headers(client) -> dict:
    resp = client.get("/api/auth/csrf")
    assert resp.status_code == 200, resp.text
    token = resp.json()["csrf_token"]
    return {"X-CSRF-Token": token}


def _register_user(client, email: str) -> str:
    """Register a Customer user and return the access token."""
    resp = client.post(
        "/api/auth/register",
        json={
            "first_name": "Sub",
            "last_name": "Tester",
            "email": email,
            "password": STRONG_PASSWORD,
            "confirm_password": STRONG_PASSWORD,
            "terms_accepted": True,
            "role": "Customer",
            "company_name": "SubCo",
        },
        headers=_csrf_headers(client),
    )
    assert resp.status_code == 201, resp.text
    return resp.json().get("access_token", "")


def _auth_headers(client, token: str) -> dict:
    return {**_csrf_headers(client), "Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Plan listing (public)
# ---------------------------------------------------------------------------


class TestListPlans:
    """GET /api/subscriptions/plans"""

    def test_list_plans_returns_three_tiers(self, client):
        resp = client.get(
            "/api/subscriptions/plans", headers=_csrf_headers(client)
        )
        assert resp.status_code == 200
        plans = resp.json()
        assert len(plans) == 3

        ids = [p["id"] for p in plans]
        assert "starter" in ids
        assert "growth" in ids
        assert "enterprise" in ids

    def test_starter_is_free(self, client):
        resp = client.get(
            "/api/subscriptions/plans", headers=_csrf_headers(client)
        )
        plans = {p["id"]: p for p in resp.json()}
        starter = plans["starter"]
        assert starter["display_price"] == "$0"
        assert starter["name"] == "Starter"
        assert float(starter["amount"]) == 0.0

    def test_growth_price(self, client):
        resp = client.get(
            "/api/subscriptions/plans", headers=_csrf_headers(client)
        )
        plans = {p["id"]: p for p in resp.json()}
        growth = plans["growth"]
        assert growth["display_price"] == "$249/mo"
        assert float(growth["amount"]) == 249.0
        assert growth["interval"] == "month"

    def test_enterprise_has_no_amount(self, client):
        resp = client.get(
            "/api/subscriptions/plans", headers=_csrf_headers(client)
        )
        plans = {p["id"]: p for p in resp.json()}
        ent = plans["enterprise"]
        assert ent["amount"] is None
        assert ent["display_price"] == "Let's talk"


# ---------------------------------------------------------------------------
# Current subscription
# ---------------------------------------------------------------------------


class TestCurrentSubscription:
    """GET /api/subscriptions/current"""

    def test_auto_creates_starter(self, client):
        """First call should auto-create a Starter subscription."""
        email = _unique_email("autocreate")
        token = _register_user(client, email)
        headers = _auth_headers(client, token)

        resp = client.get("/api/subscriptions/current", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["plan_id"] == "starter"
        assert data["plan_name"] == "Starter"
        assert data["status"] == "active"

    def test_unauthenticated_returns_401(self, client):
        resp = client.get(
            "/api/subscriptions/current", headers=_csrf_headers(client)
        )
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# Subscribe / change plan
# ---------------------------------------------------------------------------


class TestSubscribe:
    """POST /api/subscriptions/subscribe"""

    def test_subscribe_starter_is_immediate(self, client):
        email = _unique_email("sub_starter")
        token = _register_user(client, email)
        headers = _auth_headers(client, token)

        resp = client.post(
            "/api/subscriptions/subscribe",
            json={"plan_id": "starter"},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["subscription"]["plan_id"] == "starter"
        assert data["subscription"]["status"] == "active"
        assert data["checkout_url"] is None

    def test_subscribe_growth_returns_checkout(self, client):
        email = _unique_email("sub_growth")
        token = _register_user(client, email)
        headers = _auth_headers(client, token)

        resp = client.post(
            "/api/subscriptions/subscribe",
            json={"plan_id": "growth"},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["subscription"]["plan_id"] == "growth"
        assert data["subscription"]["status"] == "pending"
        assert data["checkout_url"] is not None

    def test_subscribe_enterprise_rejected(self, client):
        email = _unique_email("sub_ent")
        token = _register_user(client, email)
        headers = _auth_headers(client, token)

        resp = client.post(
            "/api/subscriptions/subscribe",
            json={"plan_id": "enterprise"},
            headers=headers,
        )
        assert resp.status_code == 400
        assert "inquiry" in resp.json()["detail"].lower()

    def test_subscribe_invalid_plan(self, client):
        email = _unique_email("sub_bad")
        token = _register_user(client, email)
        headers = _auth_headers(client, token)

        resp = client.post(
            "/api/subscriptions/subscribe",
            json={"plan_id": "diamond"},
            headers=headers,
        )
        assert resp.status_code == 422  # pydantic regex validation

    def test_already_on_plan(self, client):
        email = _unique_email("sub_dup")
        token = _register_user(client, email)
        headers = _auth_headers(client, token)

        # Subscribe to starter (auto-created)
        client.post(
            "/api/subscriptions/subscribe",
            json={"plan_id": "starter"},
            headers=headers,
        )
        # Again
        resp = client.post(
            "/api/subscriptions/subscribe",
            json={"plan_id": "starter"},
            headers=headers,
        )
        assert resp.status_code == 200
        assert "already" in resp.json()["message"].lower()


# ---------------------------------------------------------------------------
# Cancel
# ---------------------------------------------------------------------------


class TestCancel:
    """POST /api/subscriptions/cancel"""

    def test_cancel_starter_rejected(self, client):
        email = _unique_email("can_free")
        token = _register_user(client, email)
        headers = _auth_headers(client, token)

        # Ensure starter exists
        client.get("/api/subscriptions/current", headers=headers)

        resp = client.post(
            "/api/subscriptions/cancel",
            json={"immediate": False},
            headers=headers,
        )
        assert resp.status_code == 400
        assert "starter" in resp.json()["detail"].lower()

    def test_cancel_growth_at_period_end(self, client):
        email = _unique_email("can_growth")
        token = _register_user(client, email)
        headers = _auth_headers(client, token)

        # Subscribe to Growth
        client.post(
            "/api/subscriptions/subscribe",
            json={"plan_id": "growth"},
            headers=headers,
        )

        resp = client.post(
            "/api/subscriptions/cancel",
            json={"immediate": False, "reason": "testing"},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["subscription"]["cancel_at_period_end"] is True
        assert "end of the current billing period" in data["message"]

    def test_cancel_growth_immediate(self, client):
        email = _unique_email("can_imm")
        token = _register_user(client, email)
        headers = _auth_headers(client, token)

        # Subscribe to Growth
        client.post(
            "/api/subscriptions/subscribe",
            json={"plan_id": "growth"},
            headers=headers,
        )

        resp = client.post(
            "/api/subscriptions/cancel",
            json={"immediate": True},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        # Immediately downgraded to Starter
        assert data["subscription"]["plan_id"] == "starter"
        assert "starter" in data["message"].lower()


# ---------------------------------------------------------------------------
# Enterprise inquiry
# ---------------------------------------------------------------------------


class TestEnterpriseInquiry:
    """POST /api/subscriptions/enterprise-inquiry"""

    def test_submit_inquiry(self, client):
        email = _unique_email("ent_inq")
        token = _register_user(client, email)
        headers = _auth_headers(client, token)

        resp = client.post(
            "/api/subscriptions/enterprise-inquiry",
            json={
                "company_name": "BigCorp",
                "contact_name": "Jane Doe",
                "contact_email": email,
                "message": "We need enterprise features.",
            },
            headers=headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "new"
        assert "team will be in touch" in data["message"]

    def test_inquiry_requires_auth(self, client):
        resp = client.post(
            "/api/subscriptions/enterprise-inquiry",
            json={
                "company_name": "X",
                "contact_name": "Y",
                "contact_email": "y@test.com",
            },
            headers=_csrf_headers(client),
        )
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# Invoices / billing history
# ---------------------------------------------------------------------------


class TestInvoices:
    """GET /api/subscriptions/invoices"""

    def test_empty_invoices(self, client):
        email = _unique_email("inv_empty")
        token = _register_user(client, email)
        headers = _auth_headers(client, token)

        resp = client.get("/api/subscriptions/invoices", headers=headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_invoices_requires_auth(self, client):
        resp = client.get(
            "/api/subscriptions/invoices", headers=_csrf_headers(client)
        )
        assert resp.status_code in (401, 403)
