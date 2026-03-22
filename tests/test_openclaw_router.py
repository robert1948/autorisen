"""Router-level tests for OpenClaw endpoint behavior and service wiring."""

from __future__ import annotations

import importlib
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from backend.src.modules.openclaw.models import (
    OpenClawAggregationResponse,
    OpenClawApprovalDecisionRequest,
    OpenClawApprovalDecisionResponse,
    OpenClawEvent,
    OpenClawEventMetrics,
    OpenClawEventPolicy,
    OpenClawInput,
    OpenClawModelMetadata,
    OpenClawStatsResponse,
    OpenClawTaskCreateRequest,
    OpenClawTaskCreateResponse,
    OpenClawTaskResponse,
)
from backend.src.modules.openclaw.service import (
    OpenClawApprovalNotFoundError,
    OpenClawTaskNotFoundError,
)


def _router_module():
    return importlib.import_module("backend.src.modules.openclaw.router")


class _FakeService:
    def __init__(self):
        self.calls = []

    def create_task(self, payload, actor_id, db):
        self.calls.append(("create_task", payload, actor_id, db))
        return OpenClawTaskCreateResponse(
            task_id="tsk_1",
            status="completed",
            requires_approval=False,
            trace_id="trc_1",
        )

    def get_task(self, task_id, db=None):
        self.calls.append(("get_task", task_id, db))
        if task_id == "missing":
            raise OpenClawTaskNotFoundError(task_id)
        return OpenClawTaskResponse(
            task_id=task_id,
            status="completed",
            trace_id="trc_1",
        )

    def list_events(self, db=None):
        self.calls.append(("list_events", db))
        return [
            OpenClawEvent(
                event_type="openclaw.task.created",
                timestamp=datetime.now(timezone.utc),
                trace_id="trc_1",
                task_id="tsk_1",
                actor_id="user_1",
                workflow="wf",
                model=OpenClawModelMetadata(
                    provider="aws-bedrock",
                    model_id="m1",
                    region="eu-north-1",
                ),
                metrics=OpenClawEventMetrics(
                    latency_ms=1,
                    input_tokens=0,
                    output_tokens=0,
                    estimated_usd=0.0,
                ),
                policy=OpenClawEventPolicy(result="allow", rules_triggered=[]),
                metadata={},
            )
        ]

    def list_task_events(self, task_id, db=None):
        self.calls.append(("list_task_events", task_id, db))
        if task_id == "missing":
            raise OpenClawTaskNotFoundError(task_id)
        return self.list_events(db=db)

    def get_stats(self, db, *, actor_id, is_admin, window_days):
        self.calls.append(("get_stats", db, actor_id, is_admin, window_days))
        return OpenClawStatsResponse(
            window_days=window_days,
            since=datetime.now(timezone.utc),
            total_events=1,
            event_breakdown={"openclaw.task.completed": 1},
            approval_requested=0,
            approval_approved=0,
            approval_rejected=0,
            task_completed=1,
            task_failed=0,
            total_tokens_in=0,
            total_tokens_out=0,
            total_cost_usd=0.0,
        )

    def run_daily_aggregation(self, db, *, actor_id, days_back, dry_run):
        self.calls.append(("run_daily_aggregation", db, actor_id, days_back, dry_run))
        return OpenClawAggregationResponse(
            days_back=days_back,
            dry_run=dry_run,
            generated_at=datetime.now(timezone.utc),
            rollups=[],
        )

    def run_retention(self, db, *, retention_days, dry_run):
        self.calls.append(("run_retention", db, retention_days, dry_run))
        from backend.src.modules.openclaw.models import OpenClawRetentionResponse

        return OpenClawRetentionResponse(
            retention_days=retention_days,
            cutoff=datetime.now(timezone.utc),
            dry_run=dry_run,
            audit_events_affected=0,
            usage_logs_affected=0,
        )

    def decide_approval(self, approval_id, actor_id, request, approved, db=None):
        self.calls.append(
            ("decide_approval", approval_id, actor_id, request, approved, db)
        )
        if approval_id == "missing":
            raise OpenClawApprovalNotFoundError(approval_id)
        return OpenClawApprovalDecisionResponse(
            approval_id=approval_id,
            status="approved" if approved else "rejected",
            actor=actor_id,
            timestamp=datetime.now(timezone.utc),
            comment=request.comment,
        )


@pytest.fixture
def fake_service(monkeypatch):
    service = _FakeService()
    router_module = _router_module()
    monkeypatch.setattr(router_module, "_service", service)
    return service, router_module


def test_create_task_passes_actor_and_db(fake_service):
    fake_service, router_module = fake_service
    user = SimpleNamespace(id="u1")
    db = object()
    payload = OpenClawTaskCreateRequest(
        workflow="wf",
        input=OpenClawInput(text="hello"),
    )

    response = router_module.create_task(
        payload=payload,
        current_user=user,
        db=db,
    )

    assert response.task_id == "tsk_1"
    assert fake_service.calls[-1][0] == "create_task"
    assert fake_service.calls[-1][2] == "u1"
    assert fake_service.calls[-1][3] is db


def test_get_task_maps_not_found_to_404(fake_service):
    _, router_module = fake_service
    with pytest.raises(HTTPException) as exc:
        router_module.get_task(
            task_id="missing",
            current_user=object(),
            db=object(),
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "openclaw task not found"


def test_list_task_events_maps_not_found_to_404(fake_service):
    _, router_module = fake_service
    with pytest.raises(HTTPException) as exc:
        router_module.list_task_events(
            task_id="missing",
            current_user=object(),
            db=object(),
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "openclaw task not found"


def test_approve_task_maps_not_found_to_404(fake_service):
    _, router_module = fake_service
    with pytest.raises(HTTPException) as exc:
        router_module.approve_task(
            approval_id="missing",
            payload=OpenClawApprovalDecisionRequest(comment="x", ttl_minutes=10),
            current_user=SimpleNamespace(id="u1"),
            db=object(),
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "openclaw approval not found"


def test_openclaw_stats_sets_admin_flag(fake_service):
    fake_service, router_module = fake_service
    db = object()
    user = SimpleNamespace(id="u_admin", role="admin")

    response = router_module.openclaw_stats(days=7, current_user=user, db=db)

    assert response.window_days == 7
    assert fake_service.calls[-1][0] == "get_stats"
    assert fake_service.calls[-1][3] is True


def test_run_aggregation_uses_actor_id(fake_service):
    fake_service, router_module = fake_service
    db = object()
    user = SimpleNamespace(id="u2", role="admin")

    response = router_module.run_aggregation(
        days_back=5,
        dry_run=True,
        current_user=user,
        db=db,
    )

    assert response.days_back == 5
    assert fake_service.calls[-1][0] == "run_daily_aggregation"
    assert fake_service.calls[-1][2] == "u2"
