# OpenClaw on Amazon Bedrock Integration Spec

- Status: Proposed
- Owner: Engineering (TBD)
- Related RFC: docs/OpenClaw_Internal_Evaluation_RFC.md
- Last updated: 2026-03-22

## 1. Objective

Define the production integration pattern for OpenClaw on Amazon Bedrock, including API contracts, trust controls, approval workflow, telemetry, and staged rollout.

## 2. Scope

In scope:

- Backend Bedrock gateway and model routing contract.
- Policy enforcement and human approval gate.
- Evidence packaging requirements for responses.
- Audit/telemetry event schema and storage expectations.
- Integration path for Slack-first workflow.

Out of scope:

- Multi-tenant billing implementation details.
- Full external customer rollout design.
- Non-Bedrock model providers in initial implementation.

## 3. Target System Flow

1. Client sends task request to CapeControl backend.
2. Backend resolves identity, tenant, and access scope.
3. Policy engine classifies requested action risk and determines whether approval is required.
4. Context builder retrieves approved context and metadata.
5. Bedrock gateway executes model call with request envelope.
6. Post-processor validates response format and attaches evidence metadata.
7. If action required and approved, tool execution runs through allowlist.
8. Audit and usage events are emitted for each stage.
9. Response is returned with trace ID and evidence block.

## 4. Service Boundaries

- Module: backend/src/modules/agents/ (or dedicated backend/src/modules/openclaw/)
- Suggested components:
  - bedrock_gateway.py: provider-specific request/response adapter.
  - policy_engine.py: pre-call and post-call policy checks.
  - approval_service.py: queue, approve, reject, expire requests.
  - evidence_service.py: citations/source tracing/timestamps packaging.
  - telemetry.py: normalized event emission.

## 5. API Contracts

### 5.1 Create task request

- Method: POST
- Path: /api/openclaw/tasks
- Auth: required

Request body:

```json
{
  "workflow": "support_triage",
  "input": {
    "text": "customer asks for invoice correction",
    "channel": "slack"
  },
  "context_refs": ["doc:playbook-support-v2"],
  "mode": "assisted",
  "idempotency_key": "a2ec-..."
}
```

Response:

```json
{
  "task_id": "tsk_01...",
  "status": "queued",
  "requires_approval": false,
  "trace_id": "trc_01..."
}
```

### 5.2 Get task result

- Method: GET
- Path: /api/openclaw/tasks/{task_id}
- Auth: required

Response:

```json
{
  "task_id": "tsk_01...",
  "status": "completed",
  "output": {
    "summary": "Draft response prepared",
    "actions": []
  },
  "evidence": {
    "citations": [
      {
        "source_id": "doc:playbook-support-v2",
        "excerpt": "Invoice disputes must include account ID",
        "timestamp": "2026-03-22T13:04:11Z"
      }
    ]
  },
  "trace_id": "trc_01...",
  "cost": {
    "input_tokens": 1200,
    "output_tokens": 450,
    "estimated_usd": 0.0182
  }
}
```

### 5.3 Approval actions

- Method: POST
- Paths:
  - /api/openclaw/approvals/{approval_id}/approve
  - /api/openclaw/approvals/{approval_id}/reject

Request body:

```json
{
  "comment": "Approved for support follow-up",
  "ttl_minutes": 30
}
```

Response:

```json
{
  "approval_id": "apr_01...",
  "status": "approved",
  "actor": "user_123",
  "timestamp": "2026-03-22T13:05:44Z"
}
```

## 6. Risk and Approval Logic

Approval required when any of the following is true:

- Action category is write, send, delete, external_call, or permission_change.
- Data class is not non-sensitive/sanitized.
- Confidence score is below policy threshold.
- Prompt or output triggers guardrail policy.

Policy outcomes:

- allow: execute directly.
- require_approval: queue and wait for explicit approval.
- deny: block and return policy reason.

## 7. Evidence Requirements

Every completed response must include:

- trace_id
- source citation list
- generation timestamp
- actor identity (requesting user/service)
- model metadata (provider, model_id, region)
- approval metadata if applicable

## 8. Telemetry and Audit Events

Required event types:

- openclaw.task.created
- openclaw.policy.evaluated
- openclaw.model.invoked
- openclaw.approval.requested
- openclaw.approval.decided
- openclaw.tool.executed
- openclaw.task.completed
- openclaw.task.failed

Event schema (minimum):

```json
{
  "event_type": "openclaw.model.invoked",
  "timestamp": "2026-03-22T13:04:00Z",
  "trace_id": "trc_01...",
  "task_id": "tsk_01...",
  "tenant_id": "ten_01...",
  "actor_id": "usr_01...",
  "workflow": "support_triage",
  "model": {
    "provider": "aws-bedrock",
    "model_id": "anthropic.claude-sonnet-4-5",
    "region": "eu-north-1"
  },
  "metrics": {
    "latency_ms": 842,
    "input_tokens": 1200,
    "output_tokens": 450,
    "estimated_usd": 0.0182
  },
  "policy": {
    "result": "allow",
    "rules_triggered": []
  }
}
```

## 9. Security Controls

- IAM least-privilege role for Bedrock invocation.
- No direct client-side Bedrock calls.
- Secrets from environment/secret manager only.
- Deny-by-default tool execution with explicit allowlist.
- Redaction of sensitive fields in logs and traces.
- Region pinning and model allowlist by environment.

## 10. Rollout Plan

Phase 1: Internal assisted mode

- Slack triage workflow only.
- Human approval for any outbound action.
- Full event tracing and daily review.

Phase 2: Internal expansion

- Add project status brief workflow.
- Tune policy thresholds from pilot telemetry.

Phase 3: Controlled external beta

- Opt-in customer cohort.
- Workflow and connector scope remains narrow.
- Weekly security and quality reviews.

## 11. Acceptance Criteria

- API contracts implemented and documented.
- Approval queue operational with audit trail.
- Evidence block present on all responses.
- Required event types emitted and queryable.
- Pilot KPIs in RFC are measurable from telemetry.

## 12. Open Decisions

- Final module placement: modules/agents vs modules/openclaw.
- Queue backend for approval workflow.
- Event sink destination and retention policy.
- Confidence threshold values by workflow.
