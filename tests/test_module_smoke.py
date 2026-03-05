"""Smoke tests for previously untested modules.

Each test verifies that the module's router is mounted and its key
endpoints respond with sensible HTTP status codes.  Auth-guarded
endpoints MUST reject unauthenticated requests (401/403).  Open
endpoints MUST return a non-5xx response.

Covers: account, audit, capsules, chat, ops, rag, support, usage, user.
"""

import pytest


# ------------------------------------------------------------------
# Unauthenticated (open) endpoints — expect 2xx
# ------------------------------------------------------------------


class TestCapsulesSmokeOpen:
    """capsules module – no auth required on list/get."""

    def test_list_capsules(self, client):
        resp = client.get("/api/capsules/")
        assert resp.status_code in (200, 404), f"Unexpected {resp.status_code}"

    def test_get_capsule_not_found(self, client):
        resp = client.get("/api/capsules/nonexistent-id")
        assert resp.status_code in (404, 422), f"Unexpected {resp.status_code}"


class TestOpsSmokeOpen:
    """ops module – status / smoke endpoints are unauthenticated."""

    def test_mcp_status(self, client):
        resp = client.get("/api/ops/mcp/status")
        assert resp.status_code == 200

    def test_mcp_smoke(self, client):
        resp = client.get("/api/ops/mcp/smoke")
        assert resp.status_code == 200


class TestRagSmokeOpen:
    """rag module – health endpoint is unauthenticated."""

    def test_rag_health(self, client):
        resp = client.get("/api/rag/health")
        assert resp.status_code == 200


# ------------------------------------------------------------------
# Authenticated endpoints — expect 401 or 403 without credentials
# ------------------------------------------------------------------

_AUTH_REJECT = {401, 403}


class TestAccountSmokeAuth:
    """account module – all endpoints require verified user."""

    def test_get_me_requires_auth(self, client):
        resp = client.get("/api/account/me")
        assert resp.status_code in _AUTH_REJECT

    def test_get_profile_requires_auth(self, client):
        resp = client.get("/api/profile/me")
        assert resp.status_code in _AUTH_REJECT

    def test_get_projects_requires_auth(self, client):
        resp = client.get("/api/projects/mine")
        assert resp.status_code in _AUTH_REJECT


class TestAuditSmokeAuth:
    """audit module – all endpoints require verified user."""

    def test_events_requires_auth(self, client):
        resp = client.get("/api/audit/events")
        assert resp.status_code in _AUTH_REJECT

    def test_stats_requires_auth(self, client):
        resp = client.get("/api/audit/stats")
        assert resp.status_code in _AUTH_REJECT


class TestChatSmokeAuth:
    """chat module – threads require authentication."""

    def test_threads_requires_auth(self, client):
        resp = client.get("/api/chat/threads")
        assert resp.status_code in _AUTH_REJECT


class TestSupportSmokeAuth:
    """support module – FAQ & tickets require verified user."""

    def test_faqs_requires_auth(self, client):
        resp = client.get("/api/support/faqs")
        assert resp.status_code in _AUTH_REJECT

    def test_tickets_requires_auth(self, client):
        resp = client.get("/api/support/tickets")
        assert resp.status_code in _AUTH_REJECT


class TestUsageSmokeAuth:
    """usage module – summary requires verified user."""

    def test_summary_requires_auth(self, client):
        resp = client.get("/api/usage/summary")
        assert resp.status_code in _AUTH_REJECT


class TestUserSmokeAuth:
    """user module – profile / dashboard require verified user."""

    def test_profile_requires_auth(self, client):
        resp = client.get("/api/user/profile")
        assert resp.status_code in _AUTH_REJECT

    def test_dashboard_stats_requires_auth(self, client):
        resp = client.get("/api/user/dashboard/stats")
        assert resp.status_code in _AUTH_REJECT
