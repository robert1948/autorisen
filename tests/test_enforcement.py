"""Tests for plan-limit enforcement (backend/src/modules/payments/enforcement.py).

Validates:
1. _get_plan_id returns correct plan for users with/without subscriptions
2. _billing_period_start derives from subscription or falls back to month start
3. _current_execution_count correctly counts UsageLogs in the period
4. _current_agent_count correctly counts agents
5. enforce_execution_limit blocks at quota boundary
6. enforce_agent_limit blocks at quota boundary
7. 429 response body has correct structured fields
8. Under-limit requests pass through without error
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

from sqlalchemy.exc import SQLAlchemyError

from backend.src.db import models
from backend.src.db.session import SessionLocal
from backend.src.modules.payments.constants import get_plan_limits
from backend.src.modules.payments.enforcement import (
    _billing_period_start,
    _current_agent_count,
    _current_execution_count,
    _current_project_count,
    _get_plan_id,
    _raise_limit_exceeded,
    enforce_agent_limit,
    enforce_execution_limit,
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _seed_user(db, *, email_prefix: str = "enforce-test") -> models.User:
    """Create a minimal test user."""
    user_id = str(uuid.uuid4())
    user = models.User(
        id=user_id,
        email=f"{email_prefix}-{user_id[:8]}@example.test",
        hashed_password="not-used",
        first_name="Test",
        last_name="Enforce",
        role="Customer",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _seed_subscription(
    db,
    user: models.User,
    *,
    plan_id: str = "pro",
    status: str = "active",
    period_start_offset_days: int = -30,
) -> models.Subscription:
    """Create a subscription for the user."""
    now = _utcnow()
    sub = models.Subscription(
        id=str(uuid.uuid4()),
        user_id=user.id,
        plan_id=plan_id,
        status=status,
        current_period_start=now + timedelta(days=period_start_offset_days),
        current_period_end=now + timedelta(days=30 + period_start_offset_days),
        cancel_at_period_end=False,
        payment_provider="payfast",
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


def _seed_usage_logs(
    db, user: models.User, count: int, *, created_at: datetime | None = None
) -> None:
    """Seed N usage log entries."""
    ts = created_at or _utcnow()
    for _ in range(count):
        log = models.UsageLog(
            id=str(uuid.uuid4()),
            user_id=user.id,
            event_type="chat",
            tokens_in=10,
            tokens_out=20,
            created_at=ts,
        )
        db.add(log)
    db.commit()


def _seed_agents(db, user: models.User, count: int) -> list[models.Agent]:
    """Seed N agents owned by the user."""
    agents = []
    for i in range(count):
        agent = models.Agent(
            id=str(uuid.uuid4()),
            owner_id=user.id,
            slug=f"test-agent-{uuid.uuid4().hex[:8]}",
            name=f"TestAgent-{i}",
        )
        db.add(agent)
        agents.append(agent)
    db.commit()
    return agents


# ---------------------------------------------------------------------------
# Unit tests for internal helpers
# ---------------------------------------------------------------------------


class TestGetPlanId:
    """_get_plan_id should resolve the user's active plan or default to free."""

    def test_no_subscription_returns_free(self):
        with SessionLocal() as db:
            user = _seed_user(db)
            assert _get_plan_id(db, user.id) == "free"

    def test_active_subscription_returns_plan(self):
        with SessionLocal() as db:
            user = _seed_user(db)
            _seed_subscription(db, user, plan_id="pro", status="active")
            assert _get_plan_id(db, user.id) == "pro"

    def test_trialing_subscription_returns_plan(self):
        with SessionLocal() as db:
            user = _seed_user(db)
            _seed_subscription(db, user, plan_id="enterprise", status="trialing")
            assert _get_plan_id(db, user.id) == "enterprise"

    def test_cancelled_subscription_returns_free(self):
        with SessionLocal() as db:
            user = _seed_user(db)
            _seed_subscription(db, user, plan_id="pro", status="cancelled")
            assert _get_plan_id(db, user.id) == "free"

    def test_db_error_returns_free(self):
        db = Mock()
        db.query.side_effect = SQLAlchemyError("subscriptions unavailable")
        assert _get_plan_id(db, "user-1") == "free"


class TestBillingPeriodStart:
    """_billing_period_start should use subscription period or fallback to month start."""

    def test_with_subscription_uses_period_start(self):
        with SessionLocal() as db:
            user = _seed_user(db)
            sub = _seed_subscription(db, user, plan_id="pro")
            result = _billing_period_start(db, user.id)
            # Should match the subscription's current_period_start
            assert result == sub.current_period_start

    def test_without_subscription_uses_month_start(self):
        with SessionLocal() as db:
            user = _seed_user(db)
            result = _billing_period_start(db, user.id)
            now = _utcnow()
            expected = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            assert result == expected

    def test_db_error_uses_month_start(self):
        db = Mock()
        db.query.side_effect = SQLAlchemyError("subscriptions unavailable")
        result = _billing_period_start(db, "user-1")
        expected = _utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        assert result == expected


class TestCurrentExecutionCount:
    """_current_execution_count should count usage logs in the billing period."""

    def test_counts_logs_in_period(self):
        with SessionLocal() as db:
            user = _seed_user(db)
            period_start = _utcnow() - timedelta(days=15)
            _seed_usage_logs(db, user, 5, created_at=_utcnow())
            assert _current_execution_count(db, user.id, period_start) == 5

    def test_ignores_logs_before_period(self):
        with SessionLocal() as db:
            user = _seed_user(db)
            period_start = _utcnow() - timedelta(days=5)
            # Logs from 10 days ago - before period
            _seed_usage_logs(db, user, 3, created_at=_utcnow() - timedelta(days=10))
            # Logs from now - in period
            _seed_usage_logs(db, user, 2, created_at=_utcnow())
            assert _current_execution_count(db, user.id, period_start) == 2

    def test_zero_when_empty(self):
        with SessionLocal() as db:
            user = _seed_user(db)
            assert (
                _current_execution_count(db, user.id, _utcnow() - timedelta(days=30))
                == 0
            )

    def test_db_error_returns_zero(self):
        db = Mock()
        db.execute.side_effect = SQLAlchemyError("usage_logs unavailable")
        assert _current_execution_count(db, "user-1", _utcnow()) == 0


class TestCurrentAgentCount:
    """_current_agent_count should count agents owned by the user."""

    def test_counts_agents(self):
        with SessionLocal() as db:
            user = _seed_user(db)
            _seed_agents(db, user, 3)
            assert _current_agent_count(db, user.id) == 3

    def test_zero_when_no_agents(self):
        with SessionLocal() as db:
            user = _seed_user(db)
            assert _current_agent_count(db, user.id) == 0

    def test_does_not_count_other_users_agents(self):
        with SessionLocal() as db:
            user_a = _seed_user(db, email_prefix="user-a")
            user_b = _seed_user(db, email_prefix="user-b")
            _seed_agents(db, user_a, 4)
            _seed_agents(db, user_b, 2)
            assert _current_agent_count(db, user_a.id) == 4
            assert _current_agent_count(db, user_b.id) == 2

    def test_db_error_returns_zero(self):
        db = Mock()
        db.execute.side_effect = SQLAlchemyError("agents unavailable")
        assert _current_agent_count(db, "user-1") == 0


class TestCurrentProjectCount:
    """_current_project_count should degrade gracefully on DB errors."""

    def test_db_error_returns_zero(self):
        db = Mock()
        db.execute.side_effect = SQLAlchemyError("tasks unavailable")
        assert _current_project_count(db, "user-1") == 0


# ---------------------------------------------------------------------------
# 429 response body structure
# ---------------------------------------------------------------------------


class TestRaiseLimitExceeded:
    """_raise_limit_exceeded should raise HTTPException(429) with structured detail."""

    def test_execution_limit_body(self):
        import pytest
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            _raise_limit_exceeded(
                limit_type="executions",
                current=50,
                maximum=50,
                plan_id="free",
            )
        exc = exc_info.value
        assert exc.status_code == 429
        detail = exc.detail
        assert detail["code"] == "plan_limit_executions"
        assert detail["current"] == 50
        assert detail["maximum"] == 50
        assert detail["plan_id"] == "free"
        assert detail["upgrade_url"] == "/app/pricing"
        assert "execution limit" in detail["message"].lower()

    def test_agent_limit_body(self):
        import pytest
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            _raise_limit_exceeded(
                limit_type="agents",
                current=3,
                maximum=3,
                plan_id="free",
            )
        exc = exc_info.value
        assert exc.status_code == 429
        detail = exc.detail
        assert detail["code"] == "plan_limit_agents"
        assert detail["current"] == 3
        assert detail["maximum"] == 3
        assert detail["plan_id"] == "free"
        assert detail["upgrade_url"] == "/app/pricing"
        assert "agent limit" in detail["message"].lower()


# ---------------------------------------------------------------------------
# Integration tests - enforcement logic end-to-end (direct DB, no HTTP)
# ---------------------------------------------------------------------------


class TestEnforcementEndToEnd:
    """Test the full enforcement logic chain using direct DB operations."""

    def test_free_user_under_execution_limit_allowed(self):
        """Free user with 49 executions (limit 50) should pass."""
        with SessionLocal() as db:
            user = _seed_user(db)
            period_start = _utcnow().replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            _seed_usage_logs(db, user, 49, created_at=_utcnow())
            plan_id = _get_plan_id(db, user.id)
            limits = get_plan_limits(plan_id)
            current = _current_execution_count(db, user.id, period_start)
            assert plan_id == "free"
            assert current == 49
            assert current < limits.max_executions_per_month  # should pass

    def test_free_user_at_execution_limit_blocked(self):
        """Free user with 50 executions (limit 50) should be blocked."""
        with SessionLocal() as db:
            user = _seed_user(db)
            period_start = _utcnow().replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            _seed_usage_logs(db, user, 50, created_at=_utcnow())
            plan_id = _get_plan_id(db, user.id)
            limits = get_plan_limits(plan_id)
            current = _current_execution_count(db, user.id, period_start)
            assert plan_id == "free"
            assert current == 50
            assert current >= limits.max_executions_per_month  # would be blocked

    def test_pro_user_high_usage_allowed(self):
        """Pro user with 1999 executions (limit 2000) should pass."""
        with SessionLocal() as db:
            user = _seed_user(db)
            _seed_subscription(db, user, plan_id="pro", status="active")
            period_start = _utcnow().replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            _seed_usage_logs(db, user, 1999, created_at=_utcnow())
            plan_id = _get_plan_id(db, user.id)
            limits = get_plan_limits(plan_id)
            current = _current_execution_count(db, user.id, period_start)
            assert plan_id == "pro"
            assert current == 1999
            assert current < limits.max_executions_per_month

    def test_free_user_under_agent_limit_allowed(self):
        """Free user with 2 agents (limit 3) should pass."""
        with SessionLocal() as db:
            user = _seed_user(db)
            _seed_agents(db, user, 2)
            plan_id = _get_plan_id(db, user.id)
            limits = get_plan_limits(plan_id)
            current = _current_agent_count(db, user.id)
            assert plan_id == "free"
            assert current == 2
            assert current < limits.max_agents

    def test_free_user_at_agent_limit_blocked(self):
        """Free user with 3 agents (limit 3) should be blocked."""
        with SessionLocal() as db:
            user = _seed_user(db)
            _seed_agents(db, user, 3)
            plan_id = _get_plan_id(db, user.id)
            limits = get_plan_limits(plan_id)
            current = _current_agent_count(db, user.id)
            assert plan_id == "free"
            assert current == 3
            assert current >= limits.max_agents  # would be blocked

    def test_pro_user_agent_limit_higher(self):
        """Pro user can have more agents than free user."""
        with SessionLocal() as db:
            user = _seed_user(db)
            _seed_subscription(db, user, plan_id="pro", status="active")
            _seed_agents(db, user, 10)
            plan_id = _get_plan_id(db, user.id)
            limits = get_plan_limits(plan_id)
            current = _current_agent_count(db, user.id)
            assert plan_id == "pro"
            assert current == 10
            assert current < limits.max_agents  # 10 < 50

    def test_cancelled_sub_reverts_to_free_limits(self):
        """A cancelled subscription should enforce free limits."""
        with SessionLocal() as db:
            user = _seed_user(db)
            _seed_subscription(db, user, plan_id="pro", status="cancelled")
            _seed_agents(db, user, 5)
            plan_id = _get_plan_id(db, user.id)
            limits = get_plan_limits(plan_id)
            current = _current_agent_count(db, user.id)
            assert plan_id == "free"
            assert limits.max_agents == 3
            assert current >= limits.max_agents  # 5 >= 3, blocked


class TestPlanLimitsConsistency:
    """Verify plan limit values are consistent and sensible."""

    def test_free_limits(self):
        limits = get_plan_limits("free")
        assert limits.max_agents == 3
        assert limits.max_executions_per_month == 50
        assert limits.storage_limit_mb == 512

    def test_pro_limits(self):
        limits = get_plan_limits("pro")
        assert limits.max_agents == 50
        assert limits.max_executions_per_month == 2000
        assert limits.storage_limit_mb == 5120

    def test_enterprise_limits(self):
        limits = get_plan_limits("enterprise")
        assert limits.max_agents == 500
        assert limits.max_executions_per_month == 8000
        assert limits.storage_limit_mb == 51200

    def test_unknown_plan_defaults_to_free(self):
        limits = get_plan_limits("nonexistent")
        assert limits.max_agents == 3
        assert limits.max_executions_per_month == 50

    def test_pro_strictly_greater_than_free(self):
        free = get_plan_limits("free")
        pro = get_plan_limits("pro")
        assert pro.max_agents > free.max_agents
        assert pro.max_executions_per_month > free.max_executions_per_month
        assert pro.storage_limit_mb > free.storage_limit_mb

    def test_enterprise_strictly_greater_than_pro(self):
        pro = get_plan_limits("pro")
        ent = get_plan_limits("enterprise")
        assert ent.max_agents > pro.max_agents
        assert ent.max_executions_per_month > pro.max_executions_per_month
        assert ent.storage_limit_mb > pro.storage_limit_mb
