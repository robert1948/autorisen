"""OpenClaw task orchestration service with DB-backed task state."""

from __future__ import annotations

import json
import logging
import os
import time as wall_time
from datetime import datetime, time, timedelta, timezone
from decimal import Decimal
from threading import Lock
from uuid import uuid4

from backend.src.db import models
from backend.src.modules.usage.service import record_usage
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import (
    OpenClawAggregationResponse,
    OpenClawApprovalDecisionRequest,
    OpenClawApprovalDecisionResponse,
    OpenClawCitation,
    OpenClawCost,
    OpenClawDailyRollup,
    OpenClawEvent,
    OpenClawEventMetrics,
    OpenClawEventPolicy,
    OpenClawEvidence,
    OpenClawModelMetadata,
    OpenClawRetentionResponse,
    OpenClawStatsResponse,
    OpenClawTaskCreateRequest,
    OpenClawTaskCreateResponse,
    OpenClawTaskOutput,
    OpenClawTaskResponse,
)


class OpenClawTaskNotFoundError(Exception):
    """Raised when a task_id cannot be found."""


class OpenClawApprovalNotFoundError(Exception):
    """Raised when an approval_id cannot be found."""


class OpenClawService:
    """Service for OpenClaw task lifecycle orchestration.

    Task state is persisted in the shared Task table so API state survives process restarts.
    """

    TASK_ID_PREFIX = "tsk_"
    APPROVAL_ID_PREFIX = "apr_"
    APPROVAL_MARKER_PREFIX = "approval:"
    AGENT_SLUG = "openclaw"

    def __init__(self) -> None:
        self._log = logging.getLogger(__name__)
        self._lock = Lock()
        self._tasks: dict[str, OpenClawTaskResponse] = {}
        self._task_workflow: dict[str, str] = {}
        self._approvals_to_tasks: dict[str, str] = {}
        self._idempotency: dict[tuple[str, str], str] = {}
        self._events: list[OpenClawEvent] = []

    @staticmethod
    def _default_model() -> OpenClawModelMetadata:
        return OpenClawModelMetadata(
            provider="aws-bedrock",
            model_id=os.getenv(
                "OPENCLAW_BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0"
            ),
            region=os.getenv("OPENCLAW_BEDROCK_REGION", "eu-north-1"),
        )

    @classmethod
    def _format_task_id(cls, db_task_id: int) -> str:
        return f"{cls.TASK_ID_PREFIX}{db_task_id}"

    @classmethod
    def _parse_task_id(cls, task_id: str) -> int | None:
        if task_id.startswith(cls.TASK_ID_PREFIX):
            raw = task_id[len(cls.TASK_ID_PREFIX) :]
            return int(raw) if raw.isdigit() else None
        return int(task_id) if task_id.isdigit() else None

    @classmethod
    def _approval_marker(cls, approval_id: str) -> str:
        return f"{cls.APPROVAL_MARKER_PREFIX}{approval_id}"

    @staticmethod
    def _as_utc(dt: datetime | None) -> datetime:
        if dt is None:
            return datetime.now(timezone.utc)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    def _ensure_openclaw_agent(self, db: Session) -> models.Agent:
        agent = (
            db.query(models.Agent).filter(models.Agent.slug == self.AGENT_SLUG).first()
        )
        if agent:
            return agent

        agent = models.Agent(
            slug=self.AGENT_SLUG,
            name="OpenClaw",
            description="OpenClaw orchestration agent",
            visibility="private",
        )
        db.add(agent)
        db.flush()
        return agent

    @staticmethod
    def _normalize_metadata(metadata: dict[str, str] | None) -> dict[str, str]:
        if not metadata:
            return {}
        return {str(k): str(v) for k, v in metadata.items()}

    @staticmethod
    def _serialize_task(task: OpenClawTaskResponse, workflow: str) -> dict:
        return {
            "trace_id": task.trace_id,
            "workflow": workflow,
            "requires_approval": task.requires_approval,
            "approval_id": task.approval_id,
            "policy_reason": task.policy_reason,
            "output": task.output.model_dump() if task.output else None,
            "evidence": (
                task.evidence.model_dump(mode="json") if task.evidence else None
            ),
            "cost": task.cost.model_dump() if task.cost else None,
        }

    @classmethod
    def _task_from_record(cls, record: models.Task) -> OpenClawTaskResponse:
        payload = record.output_data if isinstance(record.output_data, dict) else {}

        output = payload.get("output")
        evidence = payload.get("evidence")
        cost = payload.get("cost")

        return OpenClawTaskResponse(
            task_id=cls._format_task_id(record.id),
            status=str(record.status),
            output=(
                OpenClawTaskOutput.model_validate(output)
                if isinstance(output, dict)
                else None
            ),
            evidence=(
                OpenClawEvidence.model_validate(evidence)
                if isinstance(evidence, dict)
                else None
            ),
            trace_id=str(payload.get("trace_id", "")),
            cost=OpenClawCost.model_validate(cost) if isinstance(cost, dict) else None,
            requires_approval=bool(payload.get("requires_approval", False)),
            approval_id=(
                payload.get("approval_id")
                if isinstance(payload.get("approval_id"), str)
                else None
            ),
            policy_reason=(
                payload.get("policy_reason")
                if isinstance(payload.get("policy_reason"), str)
                else None
            ),
        )

    @staticmethod
    def _normalized_idempotency_key(raw_key: str | None) -> str | None:
        if raw_key is None:
            return None
        value = raw_key.strip()
        return value or None

    @classmethod
    def _extract_idempotency_key(cls, record: models.Task) -> str | None:
        if not isinstance(record.input_data, dict):
            return None
        raw = record.input_data.get("idempotency_key")
        if not isinstance(raw, str):
            return None
        return cls._normalized_idempotency_key(raw)

    def _find_task_by_idempotency(
        self,
        *,
        db: Session,
        actor_id: str,
        idempotency_key: str,
    ) -> models.Task | None:
        candidate_records = (
            db.query(models.Task)
            .filter(
                models.Task.user_id == actor_id,
                models.Task.agent_id.isnot(None),
            )
            .order_by(models.Task.id.desc())
            .limit(200)
            .all()
        )

        for record in candidate_records:
            if self._extract_idempotency_key(record) == idempotency_key:
                return record
        return None

    def _invoke_bedrock(
        self,
        request: OpenClawTaskCreateRequest,
    ) -> tuple[OpenClawTaskOutput, OpenClawEvidence, OpenClawCost, int]:
        model = self._default_model()
        started = wall_time.perf_counter()

        if os.getenv("OPENCLAW_BEDROCK_ENABLED", "0").lower() not in {
            "1",
            "true",
            "yes",
        }:
            task = self._build_completed_payload("local", "local", request)
            assert task.output is not None
            assert task.evidence is not None
            assert task.cost is not None
            latency_ms = int((wall_time.perf_counter() - started) * 1000)
            return task.output, task.evidence, task.cost, max(latency_ms, 1)

        try:
            import boto3  # type: ignore

            client = boto3.client("bedrock-runtime", region_name=model.region)
            max_tokens = int(os.getenv("OPENCLAW_BEDROCK_MAX_TOKENS", "700"))
            temperature = float(os.getenv("OPENCLAW_BEDROCK_TEMPERATURE", "0.2"))

            payload = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": request.input.text,
                            }
                        ],
                    }
                ],
            }

            response = client.invoke_model(
                modelId=model.model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(payload),
            )

            raw_body = response.get("body")
            body_bytes = raw_body.read() if hasattr(raw_body, "read") else raw_body
            data = json.loads(
                body_bytes.decode("utf-8")
                if isinstance(body_bytes, bytes)
                else str(body_bytes)
            )

            segments = data.get("content", []) if isinstance(data, dict) else []
            text_parts = [
                str(seg.get("text", ""))
                for seg in segments
                if isinstance(seg, dict) and seg.get("type") == "text"
            ]
            summary = "\n".join(part for part in text_parts if part).strip()
            if not summary:
                summary = (
                    f"OpenClaw processed workflow '{request.workflow}' via Bedrock."
                )

            usage = data.get("usage", {}) if isinstance(data, dict) else {}
            input_tokens = int(usage.get("input_tokens", 0) or 0)
            output_tokens = int(usage.get("output_tokens", 0) or 0)

            input_cost_per_1k = float(
                os.getenv("OPENCLAW_COST_PER_1K_INPUT_USD", "0.003")
            )
            output_cost_per_1k = float(
                os.getenv("OPENCLAW_COST_PER_1K_OUTPUT_USD", "0.015")
            )
            estimated_usd = ((input_tokens / 1000.0) * input_cost_per_1k) + (
                (output_tokens / 1000.0) * output_cost_per_1k
            )

            citation = OpenClawCitation(
                source_id=f"model:{model.model_id}",
                excerpt=summary[:300],
                timestamp=datetime.now(timezone.utc),
            )
            latency_ms = int((wall_time.perf_counter() - started) * 1000)

            return (
                OpenClawTaskOutput(summary=summary, actions=[]),
                OpenClawEvidence(citations=[citation]),
                OpenClawCost(
                    input_tokens=max(input_tokens, 0),
                    output_tokens=max(output_tokens, 0),
                    estimated_usd=max(estimated_usd, 0.0),
                ),
                max(latency_ms, 1),
            )
        except Exception:
            self._log.warning(
                "Bedrock invoke failed; using local fallback result", exc_info=True
            )
            task = self._build_completed_payload("fallback", "fallback", request)
            assert task.output is not None
            assert task.evidence is not None
            assert task.cost is not None
            latency_ms = int((wall_time.perf_counter() - started) * 1000)
            return task.output, task.evidence, task.cost, max(latency_ms, 1)

    def _emit_event(
        self,
        *,
        event_type: str,
        task_id: str,
        trace_id: str,
        actor_id: str,
        workflow: str,
        policy_result: str,
        db: Session | None = None,
        rules_triggered: list[str] | None = None,
        metrics: OpenClawEventMetrics | None = None,
        metadata: dict[str, str] | None = None,
    ) -> None:
        normalized_metadata = self._normalize_metadata(metadata)
        event = OpenClawEvent(
            event_type=event_type,
            timestamp=datetime.now(timezone.utc),
            trace_id=trace_id,
            task_id=task_id,
            actor_id=actor_id,
            workflow=workflow,
            model=self._default_model(),
            metrics=metrics
            or OpenClawEventMetrics(
                latency_ms=0,
                input_tokens=0,
                output_tokens=0,
                estimated_usd=0.0,
            ),
            policy=OpenClawEventPolicy(
                result=policy_result,
                rules_triggered=rules_triggered or [],
            ),
            metadata=normalized_metadata,
        )
        self._events.append(event)

        if db is not None:
            self._persist_event(db, event)

    def _persist_event(self, db: Session, event: OpenClawEvent) -> None:
        """Best-effort persistence to platform audit and usage stores."""
        try:
            event_payload = {
                "trace_id": event.trace_id,
                "task_id": event.task_id,
                "workflow": event.workflow,
                "model": event.model.model_dump(),
                "metrics": event.metrics.model_dump(),
                "policy": event.policy.model_dump(),
                "metadata": event.metadata,
            }
            db.add(
                models.AuditEvent(
                    user_id=event.actor_id,
                    event_type=event.event_type,
                    event_data=event_payload,
                )
            )
            record_usage(
                db,
                user_id=event.actor_id,
                event_type=event.event_type,
                model=event.model.model_id,
                tokens_in=event.metrics.input_tokens,
                tokens_out=event.metrics.output_tokens,
                cost_usd=Decimal(str(event.metrics.estimated_usd)),
                thread_id=event.task_id,
                detail={
                    "trace_id": event.trace_id,
                    "workflow": event.workflow,
                    "policy": event.policy.result,
                },
            )
        except Exception:
            self._log.warning(
                "Failed to persist OpenClaw telemetry event (%s)",
                event.event_type,
                exc_info=True,
            )

    @staticmethod
    def _requires_approval(
        request: OpenClawTaskCreateRequest,
    ) -> tuple[bool, str | None]:
        risky_tokens = ("delete", "send", "write", "external", "permission")
        text = request.input.text.lower()
        if request.mode == "autonomous":
            return True, "autonomous_mode"
        if any(token in text for token in risky_tokens):
            return True, "policy_keyword_match"
        return False, None

    @staticmethod
    def _build_completed_payload(
        task_id: str,
        trace_id: str,
        request: OpenClawTaskCreateRequest,
    ) -> OpenClawTaskResponse:
        citation = OpenClawCitation(
            source_id=(
                request.context_refs[0]
                if request.context_refs
                else "source:unspecified"
            ),
            excerpt="Response generated from approved workflow context.",
            timestamp=datetime.now(timezone.utc),
        )
        return OpenClawTaskResponse(
            task_id=task_id,
            status="completed",
            output=OpenClawTaskOutput(
                summary=f"OpenClaw processed workflow '{request.workflow}' in assisted mode.",
                actions=[],
            ),
            evidence=OpenClawEvidence(citations=[citation]),
            trace_id=trace_id,
            cost=OpenClawCost(input_tokens=120, output_tokens=90, estimated_usd=0.0018),
            requires_approval=False,
        )

    def create_task(
        self,
        request: OpenClawTaskCreateRequest,
        actor_id: str,
        db: Session | None = None,
    ) -> OpenClawTaskCreateResponse:
        if db is not None:
            return self._create_task_persistent(request, actor_id=actor_id, db=db)

        with self._lock:
            if request.idempotency_key:
                key = (actor_id, request.idempotency_key)
                existing_task_id = self._idempotency.get(key)
                if existing_task_id:
                    existing = self._tasks[existing_task_id]
                    return OpenClawTaskCreateResponse(
                        task_id=existing.task_id,
                        status=existing.status,
                        requires_approval=existing.requires_approval,
                        trace_id=existing.trace_id,
                    )

            task_id = f"tsk_{uuid4().hex[:12]}"
            trace_id = f"trc_{uuid4().hex[:12]}"
            requires_approval, policy_reason = self._requires_approval(request)
            self._task_workflow[task_id] = request.workflow

            self._emit_event(
                event_type="openclaw.task.created",
                task_id=task_id,
                trace_id=trace_id,
                actor_id=actor_id,
                workflow=request.workflow,
                policy_result="allow",
                db=db,
                metadata={"mode": request.mode},
            )

            policy_result = "require_approval" if requires_approval else "allow"
            rules = [policy_reason] if policy_reason else []
            self._emit_event(
                event_type="openclaw.policy.evaluated",
                task_id=task_id,
                trace_id=trace_id,
                actor_id=actor_id,
                workflow=request.workflow,
                policy_result=policy_result,
                db=db,
                rules_triggered=rules,
            )

            if requires_approval:
                approval_id = f"apr_{uuid4().hex[:12]}"
                task = OpenClawTaskResponse(
                    task_id=task_id,
                    status="requires_approval",
                    trace_id=trace_id,
                    requires_approval=True,
                    approval_id=approval_id,
                    policy_reason=policy_reason,
                )
                self._approvals_to_tasks[approval_id] = task_id
                self._emit_event(
                    event_type="openclaw.approval.requested",
                    task_id=task_id,
                    trace_id=trace_id,
                    actor_id=actor_id,
                    workflow=request.workflow,
                    policy_result="require_approval",
                    db=db,
                    rules_triggered=rules,
                    metadata={"approval_id": approval_id},
                )
            else:
                task = self._build_completed_payload(task_id, trace_id, request)
                assert task.cost is not None
                self._emit_event(
                    event_type="openclaw.model.invoked",
                    task_id=task_id,
                    trace_id=trace_id,
                    actor_id=actor_id,
                    workflow=request.workflow,
                    policy_result="allow",
                    db=db,
                    metrics=OpenClawEventMetrics(
                        latency_ms=820,
                        input_tokens=task.cost.input_tokens,
                        output_tokens=task.cost.output_tokens,
                        estimated_usd=task.cost.estimated_usd,
                    ),
                )
                self._emit_event(
                    event_type="openclaw.task.completed",
                    task_id=task_id,
                    trace_id=trace_id,
                    actor_id=actor_id,
                    workflow=request.workflow,
                    policy_result="allow",
                    db=db,
                    metrics=OpenClawEventMetrics(
                        latency_ms=860,
                        input_tokens=task.cost.input_tokens,
                        output_tokens=task.cost.output_tokens,
                        estimated_usd=task.cost.estimated_usd,
                    ),
                )

            self._tasks[task_id] = task

            if db is not None:
                try:
                    db.commit()
                except Exception:
                    self._log.warning(
                        "Failed to commit OpenClaw task events for %s",
                        task_id,
                        exc_info=True,
                    )
                    db.rollback()

            if request.idempotency_key:
                self._idempotency[(actor_id, request.idempotency_key)] = task_id

            return OpenClawTaskCreateResponse(
                task_id=task.task_id,
                status=task.status,
                requires_approval=task.requires_approval,
                trace_id=task.trace_id,
            )

    def _create_task_persistent(
        self,
        request: OpenClawTaskCreateRequest,
        *,
        actor_id: str,
        db: Session,
    ) -> OpenClawTaskCreateResponse:
        idempotency_key = self._normalized_idempotency_key(request.idempotency_key)
        if idempotency_key is not None:
            existing = self._find_task_by_idempotency(
                db=db,
                actor_id=actor_id,
                idempotency_key=idempotency_key,
            )
            if existing is not None:
                existing_task = self._task_from_record(existing)
                return OpenClawTaskCreateResponse(
                    task_id=existing_task.task_id,
                    status=existing_task.status,
                    requires_approval=existing_task.requires_approval,
                    trace_id=existing_task.trace_id,
                )

        agent = self._ensure_openclaw_agent(db)
        trace_id = f"trc_{uuid4().hex[:12]}"
        requires_approval, policy_reason = self._requires_approval(request)

        task_record = models.Task(
            title=request.workflow,
            description=request.input.text,
            user_id=actor_id,
            agent_id=str(agent.id),
            status="requires_approval" if requires_approval else "completed",
            input_data={
                "workflow": request.workflow,
                "input": request.input.model_dump(),
                "context_refs": request.context_refs,
                "mode": request.mode,
                "idempotency_key": idempotency_key,
            },
            started_at=datetime.now(timezone.utc),
        )
        db.add(task_record)
        db.flush()

        task_id = self._format_task_id(task_record.id)
        workflow = request.workflow

        self._emit_event(
            event_type="openclaw.task.created",
            task_id=task_id,
            trace_id=trace_id,
            actor_id=actor_id,
            workflow=workflow,
            policy_result="allow",
            db=db,
            metadata={"mode": request.mode},
        )

        policy_result = "require_approval" if requires_approval else "allow"
        rules = [policy_reason] if policy_reason else []
        self._emit_event(
            event_type="openclaw.policy.evaluated",
            task_id=task_id,
            trace_id=trace_id,
            actor_id=actor_id,
            workflow=workflow,
            policy_result=policy_result,
            db=db,
            rules_triggered=rules,
        )

        if requires_approval:
            approval_id = f"{self.APPROVAL_ID_PREFIX}{uuid4().hex[:12]}"
            task = OpenClawTaskResponse(
                task_id=task_id,
                status="requires_approval",
                trace_id=trace_id,
                requires_approval=True,
                approval_id=approval_id,
                policy_reason=policy_reason,
            )
            task_record.error_message = self._approval_marker(approval_id)
            self._emit_event(
                event_type="openclaw.approval.requested",
                task_id=task_id,
                trace_id=trace_id,
                actor_id=actor_id,
                workflow=workflow,
                policy_result="require_approval",
                db=db,
                rules_triggered=rules,
                metadata={"approval_id": approval_id},
            )
        else:
            output, evidence, cost, latency_ms = self._invoke_bedrock(request)
            task = OpenClawTaskResponse(
                task_id=task_id,
                status="completed",
                output=output,
                evidence=evidence,
                trace_id=trace_id,
                cost=cost,
                requires_approval=False,
            )
            task_record.completed_at = datetime.now(timezone.utc)
            self._emit_event(
                event_type="openclaw.model.invoked",
                task_id=task_id,
                trace_id=trace_id,
                actor_id=actor_id,
                workflow=workflow,
                policy_result="allow",
                db=db,
                metrics=OpenClawEventMetrics(
                    latency_ms=latency_ms,
                    input_tokens=cost.input_tokens,
                    output_tokens=cost.output_tokens,
                    estimated_usd=cost.estimated_usd,
                ),
            )
            self._emit_event(
                event_type="openclaw.task.completed",
                task_id=task_id,
                trace_id=trace_id,
                actor_id=actor_id,
                workflow=workflow,
                policy_result="allow",
                db=db,
                metrics=OpenClawEventMetrics(
                    latency_ms=latency_ms,
                    input_tokens=cost.input_tokens,
                    output_tokens=cost.output_tokens,
                    estimated_usd=cost.estimated_usd,
                ),
            )

        task_record.output_data = self._serialize_task(task, workflow)

        try:
            db.commit()
        except Exception:
            self._log.warning(
                "Failed to commit OpenClaw task events for %s",
                task_id,
                exc_info=True,
            )
            db.rollback()
            raise

        return OpenClawTaskCreateResponse(
            task_id=task.task_id,
            status=task.status,
            requires_approval=task.requires_approval,
            trace_id=task.trace_id,
        )

    def get_task(self, task_id: str, db: Session | None = None) -> OpenClawTaskResponse:
        if db is not None:
            db_task_id = self._parse_task_id(task_id)
            if db_task_id is None:
                raise OpenClawTaskNotFoundError(task_id)
            record = db.query(models.Task).filter(models.Task.id == db_task_id).first()
            if record is None:
                raise OpenClawTaskNotFoundError(task_id)
            return self._task_from_record(record)

        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                raise OpenClawTaskNotFoundError(task_id)
            return task

    def decide_approval(
        self,
        approval_id: str,
        actor_id: str,
        request: OpenClawApprovalDecisionRequest,
        approved: bool,
        db: Session | None = None,
    ) -> OpenClawApprovalDecisionResponse:
        if db is not None:
            return self._decide_approval_persistent(
                approval_id=approval_id,
                actor_id=actor_id,
                request=request,
                approved=approved,
                db=db,
            )

        with self._lock:
            task_id = self._approvals_to_tasks.get(approval_id)
            if task_id is None:
                raise OpenClawApprovalNotFoundError(approval_id)
            task = self._tasks.get(task_id)
            if task is None:
                raise OpenClawTaskNotFoundError(task_id)
            workflow = self._task_workflow.get(task_id, "unknown")

            now = datetime.now(timezone.utc)
            self._emit_event(
                event_type="openclaw.approval.decided",
                task_id=task_id,
                trace_id=task.trace_id,
                actor_id=actor_id,
                workflow=workflow,
                policy_result="allow" if approved else "deny",
                db=db,
                metadata={
                    "approval_id": approval_id,
                    "decision": "approved" if approved else "rejected",
                },
            )

            if approved:
                task.status = "completed"
                task.output = OpenClawTaskOutput(
                    summary="Approval granted. Task completed through controlled execution.",
                    actions=["approved_action"],
                )
                task.evidence = OpenClawEvidence(
                    citations=[
                        OpenClawCitation(
                            source_id="approval:manual",
                            excerpt="Action executed after explicit human approval.",
                            timestamp=now,
                        )
                    ]
                )
                task.cost = OpenClawCost(
                    input_tokens=140,
                    output_tokens=110,
                    estimated_usd=0.0023,
                )
                self._emit_event(
                    event_type="openclaw.tool.executed",
                    task_id=task_id,
                    trace_id=task.trace_id,
                    actor_id=actor_id,
                    workflow=workflow,
                    policy_result="allow",
                    db=db,
                    metrics=OpenClawEventMetrics(
                        latency_ms=120,
                        input_tokens=0,
                        output_tokens=0,
                        estimated_usd=0.0,
                    ),
                    metadata={"action": "approved_action"},
                )
                self._emit_event(
                    event_type="openclaw.task.completed",
                    task_id=task_id,
                    trace_id=task.trace_id,
                    actor_id=actor_id,
                    workflow=workflow,
                    policy_result="allow",
                    db=db,
                    metrics=OpenClawEventMetrics(
                        latency_ms=920,
                        input_tokens=task.cost.input_tokens,
                        output_tokens=task.cost.output_tokens,
                        estimated_usd=task.cost.estimated_usd,
                    ),
                )
                status = "approved"
            else:
                task.status = "rejected"
                task.policy_reason = "approval_rejected"
                self._emit_event(
                    event_type="openclaw.task.failed",
                    task_id=task_id,
                    trace_id=task.trace_id,
                    actor_id=actor_id,
                    workflow=workflow,
                    policy_result="deny",
                    db=db,
                    rules_triggered=["approval_rejected"],
                )
                status = "rejected"

            if db is not None:
                try:
                    db.commit()
                except Exception:
                    self._log.warning(
                        "Failed to commit OpenClaw approval events for %s",
                        approval_id,
                        exc_info=True,
                    )
                    db.rollback()

            return OpenClawApprovalDecisionResponse(
                approval_id=approval_id,
                status=status,
                actor=actor_id,
                timestamp=now,
                comment=request.comment,
            )

    def _decide_approval_persistent(
        self,
        *,
        approval_id: str,
        actor_id: str,
        request: OpenClawApprovalDecisionRequest,
        approved: bool,
        db: Session,
    ) -> OpenClawApprovalDecisionResponse:
        agent = self._ensure_openclaw_agent(db)
        record = (
            db.query(models.Task)
            .filter(
                models.Task.agent_id == str(agent.id),
                models.Task.error_message == self._approval_marker(approval_id),
            )
            .first()
        )
        if record is None:
            raise OpenClawApprovalNotFoundError(approval_id)

        payload = record.output_data if isinstance(record.output_data, dict) else {}
        trace_id = str(payload.get("trace_id", ""))
        workflow = str(payload.get("workflow", record.title or "unknown"))
        task_id = self._format_task_id(record.id)
        now = datetime.now(timezone.utc)

        self._emit_event(
            event_type="openclaw.approval.decided",
            task_id=task_id,
            trace_id=trace_id,
            actor_id=actor_id,
            workflow=workflow,
            policy_result="allow" if approved else "deny",
            db=db,
            metadata={
                "approval_id": approval_id,
                "decision": "approved" if approved else "rejected",
            },
        )

        if approved:
            completed_task = OpenClawTaskResponse(
                task_id=task_id,
                status="completed",
                output=OpenClawTaskOutput(
                    summary="Approval granted. Task completed through controlled execution.",
                    actions=["approved_action"],
                ),
                evidence=OpenClawEvidence(
                    citations=[
                        OpenClawCitation(
                            source_id="approval:manual",
                            excerpt="Action executed after explicit human approval.",
                            timestamp=now,
                        )
                    ]
                ),
                trace_id=trace_id,
                cost=OpenClawCost(
                    input_tokens=140,
                    output_tokens=110,
                    estimated_usd=0.0023,
                ),
                requires_approval=False,
                approval_id=approval_id,
            )
            record.status = "completed"
            record.error_message = None
            record.completed_at = now
            record.output_data = self._serialize_task(completed_task, workflow)

            self._emit_event(
                event_type="openclaw.tool.executed",
                task_id=task_id,
                trace_id=trace_id,
                actor_id=actor_id,
                workflow=workflow,
                policy_result="allow",
                db=db,
                metrics=OpenClawEventMetrics(
                    latency_ms=120,
                    input_tokens=0,
                    output_tokens=0,
                    estimated_usd=0.0,
                ),
                metadata={"action": "approved_action"},
            )
            self._emit_event(
                event_type="openclaw.task.completed",
                task_id=task_id,
                trace_id=trace_id,
                actor_id=actor_id,
                workflow=workflow,
                policy_result="allow",
                db=db,
                metrics=OpenClawEventMetrics(
                    latency_ms=920,
                    input_tokens=completed_task.cost.input_tokens,
                    output_tokens=completed_task.cost.output_tokens,
                    estimated_usd=completed_task.cost.estimated_usd,
                ),
            )
            status = "approved"
        else:
            rejected_task = OpenClawTaskResponse(
                task_id=task_id,
                status="rejected",
                trace_id=trace_id,
                requires_approval=False,
                approval_id=approval_id,
                policy_reason="approval_rejected",
            )
            record.status = "rejected"
            record.error_message = "approval_rejected"
            record.completed_at = now
            record.output_data = self._serialize_task(rejected_task, workflow)
            self._emit_event(
                event_type="openclaw.task.failed",
                task_id=task_id,
                trace_id=trace_id,
                actor_id=actor_id,
                workflow=workflow,
                policy_result="deny",
                db=db,
                rules_triggered=["approval_rejected"],
            )
            status = "rejected"

        try:
            db.commit()
        except Exception:
            self._log.warning(
                "Failed to commit OpenClaw approval events for %s",
                approval_id,
                exc_info=True,
            )
            db.rollback()
            raise

        return OpenClawApprovalDecisionResponse(
            approval_id=approval_id,
            status=status,
            actor=actor_id,
            timestamp=now,
            comment=request.comment,
        )

    def list_events(self, db: Session | None = None) -> list[OpenClawEvent]:
        if db is not None:
            rows = (
                db.query(models.AuditEvent)
                .filter(models.AuditEvent.event_type.like("openclaw.%"))
                .order_by(models.AuditEvent.created_at.desc())
                .limit(500)
                .all()
            )
            events: list[OpenClawEvent] = []
            for row in rows:
                payload = row.event_data if isinstance(row.event_data, dict) else {}
                model_payload = (
                    payload.get("model")
                    if isinstance(payload.get("model"), dict)
                    else {}
                )
                metrics_payload = (
                    payload.get("metrics")
                    if isinstance(payload.get("metrics"), dict)
                    else {}
                )
                policy_payload = (
                    payload.get("policy")
                    if isinstance(payload.get("policy"), dict)
                    else {}
                )
                metadata_payload = (
                    payload.get("metadata")
                    if isinstance(payload.get("metadata"), dict)
                    else {}
                )

                try:
                    events.append(
                        OpenClawEvent(
                            event_type=str(row.event_type),
                            timestamp=self._as_utc(row.created_at),
                            trace_id=str(payload.get("trace_id", "")),
                            task_id=str(payload.get("task_id", "")),
                            actor_id=str(row.user_id or "unknown"),
                            workflow=str(payload.get("workflow", "unknown")),
                            model=OpenClawModelMetadata.model_validate(
                                model_payload or self._default_model().model_dump()
                            ),
                            metrics=OpenClawEventMetrics.model_validate(
                                metrics_payload
                                or {
                                    "latency_ms": 0,
                                    "input_tokens": 0,
                                    "output_tokens": 0,
                                    "estimated_usd": 0.0,
                                }
                            ),
                            policy=OpenClawEventPolicy.model_validate(
                                policy_payload
                                or {
                                    "result": "allow",
                                    "rules_triggered": [],
                                }
                            ),
                            metadata=self._normalize_metadata(metadata_payload),
                        )
                    )
                except Exception:
                    self._log.debug(
                        "Skipping malformed OpenClaw event row id=%s",
                        row.id,
                        exc_info=True,
                    )
            events.reverse()
            return events

        with self._lock:
            return list(self._events)

    def list_task_events(
        self, task_id: str, db: Session | None = None
    ) -> list[OpenClawEvent]:
        if db is not None:
            _ = self.get_task(task_id, db=db)
            return [
                event for event in self.list_events(db=db) if event.task_id == task_id
            ]

        with self._lock:
            if task_id not in self._tasks:
                raise OpenClawTaskNotFoundError(task_id)
            return [event for event in self._events if event.task_id == task_id]

    def get_stats(
        self,
        db: Session,
        *,
        actor_id: str,
        is_admin: bool,
        window_days: int,
    ) -> OpenClawStatsResponse:
        since = datetime.now(timezone.utc) - timedelta(days=window_days)

        audit_filter = [
            models.AuditEvent.event_type.like("openclaw.%"),
            models.AuditEvent.created_at >= since,
        ]
        usage_filter = [
            models.UsageLog.event_type.like("openclaw.%"),
            models.UsageLog.created_at >= since,
        ]
        if not is_admin:
            audit_filter.append(models.AuditEvent.user_id == actor_id)
            usage_filter.append(models.UsageLog.user_id == actor_id)

        total_events = (
            db.scalar(select(func.count(models.AuditEvent.id)).where(*audit_filter))
            or 0
        )

        type_rows = db.execute(
            select(models.AuditEvent.event_type, func.count(models.AuditEvent.id))
            .where(*audit_filter)
            .group_by(models.AuditEvent.event_type)
        ).all()
        event_breakdown = {str(row[0]): int(row[1]) for row in type_rows}

        usage_row = db.execute(
            select(
                func.coalesce(func.sum(models.UsageLog.tokens_in), 0),
                func.coalesce(func.sum(models.UsageLog.tokens_out), 0),
                func.coalesce(func.sum(models.UsageLog.cost_usd), 0),
            ).where(*usage_filter)
        ).one()

        approval_rows = db.execute(
            select(models.AuditEvent.event_data).where(
                *audit_filter,
                models.AuditEvent.event_type == "openclaw.approval.decided",
            )
        ).all()
        approval_approved = 0
        approval_rejected = 0
        for row in approval_rows:
            payload = row[0] if isinstance(row[0], dict) else {}
            metadata = payload.get("metadata", {}) if isinstance(payload, dict) else {}
            decision = metadata.get("decision") if isinstance(metadata, dict) else None
            if decision == "approved":
                approval_approved += 1
            elif decision == "rejected":
                approval_rejected += 1

        return OpenClawStatsResponse(
            window_days=window_days,
            since=since,
            total_events=int(total_events),
            event_breakdown=event_breakdown,
            approval_requested=event_breakdown.get("openclaw.approval.requested", 0),
            approval_approved=approval_approved,
            approval_rejected=approval_rejected,
            task_completed=event_breakdown.get("openclaw.task.completed", 0),
            task_failed=event_breakdown.get("openclaw.task.failed", 0),
            total_tokens_in=int(usage_row[0] or 0),
            total_tokens_out=int(usage_row[1] or 0),
            total_cost_usd=float(usage_row[2] or 0),
        )

    def run_retention(
        self,
        db: Session,
        *,
        retention_days: int,
        dry_run: bool,
    ) -> OpenClawRetentionResponse:
        cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)

        audit_query = db.query(models.AuditEvent).filter(
            models.AuditEvent.event_type.like("openclaw.%"),
            models.AuditEvent.created_at < cutoff,
        )
        usage_query = db.query(models.UsageLog).filter(
            models.UsageLog.event_type.like("openclaw.%"),
            models.UsageLog.created_at < cutoff,
        )

        audit_count = int(audit_query.count())
        usage_count = int(usage_query.count())

        if not dry_run:
            audit_query.delete(synchronize_session=False)
            usage_query.delete(synchronize_session=False)
            db.commit()

        return OpenClawRetentionResponse(
            retention_days=retention_days,
            cutoff=cutoff,
            dry_run=dry_run,
            audit_events_affected=audit_count,
            usage_logs_affected=usage_count,
        )

    def run_daily_aggregation(
        self,
        db: Session,
        *,
        actor_id: str | None,
        days_back: int,
        dry_run: bool,
    ) -> OpenClawAggregationResponse:
        now = datetime.now(timezone.utc)
        rollups: list[OpenClawDailyRollup] = []

        for offset in range(days_back):
            day = (now - timedelta(days=offset)).date()
            day_start = datetime.combine(day, time.min).replace(tzinfo=timezone.utc)
            day_end = day_start + timedelta(days=1)

            audit_filter = [
                models.AuditEvent.event_type.like("openclaw.%"),
                models.AuditEvent.event_type != "openclaw.aggregation.daily",
                models.AuditEvent.created_at >= day_start,
                models.AuditEvent.created_at < day_end,
            ]
            usage_filter = [
                models.UsageLog.event_type.like("openclaw.%"),
                models.UsageLog.created_at >= day_start,
                models.UsageLog.created_at < day_end,
            ]

            total_events = (
                db.scalar(select(func.count(models.AuditEvent.id)).where(*audit_filter))
                or 0
            )

            type_rows = db.execute(
                select(models.AuditEvent.event_type, func.count(models.AuditEvent.id))
                .where(*audit_filter)
                .group_by(models.AuditEvent.event_type)
            ).all()
            breakdown = {str(row[0]): int(row[1]) for row in type_rows}

            usage_row = db.execute(
                select(
                    func.coalesce(func.sum(models.UsageLog.tokens_in), 0),
                    func.coalesce(func.sum(models.UsageLog.tokens_out), 0),
                    func.coalesce(func.sum(models.UsageLog.cost_usd), 0),
                ).where(*usage_filter)
            ).one()

            approval_rows = db.execute(
                select(models.AuditEvent.event_data).where(
                    *audit_filter,
                    models.AuditEvent.event_type == "openclaw.approval.decided",
                )
            ).all()
            approval_approved = 0
            approval_rejected = 0
            for row in approval_rows:
                payload = row[0] if isinstance(row[0], dict) else {}
                metadata = (
                    payload.get("metadata", {}) if isinstance(payload, dict) else {}
                )
                decision = (
                    metadata.get("decision") if isinstance(metadata, dict) else None
                )
                if decision == "approved":
                    approval_approved += 1
                elif decision == "rejected":
                    approval_rejected += 1

            rollup = OpenClawDailyRollup(
                rollup_date=day.isoformat(),
                total_events=int(total_events),
                task_completed=breakdown.get("openclaw.task.completed", 0),
                task_failed=breakdown.get("openclaw.task.failed", 0),
                approval_requested=breakdown.get("openclaw.approval.requested", 0),
                approval_approved=approval_approved,
                approval_rejected=approval_rejected,
                total_tokens_in=int(usage_row[0] or 0),
                total_tokens_out=int(usage_row[1] or 0),
                total_cost_usd=float(usage_row[2] or 0),
            )
            rollups.append(rollup)

            if not dry_run:
                db.add(
                    models.AuditEvent(
                        user_id=actor_id,
                        event_type="openclaw.aggregation.daily",
                        event_data={
                            "rollup_date": rollup.rollup_date,
                            "summary": rollup.model_dump(),
                        },
                    )
                )

        if not dry_run:
            db.commit()

        rollups.sort(key=lambda item: item.rollup_date)
        return OpenClawAggregationResponse(
            days_back=days_back,
            dry_run=dry_run,
            generated_at=now,
            rollups=rollups,
        )
