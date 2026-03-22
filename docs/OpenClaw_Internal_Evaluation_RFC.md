# RFC: OpenClaw Internal Evaluation Pilot

- Status: Proposed
- Owner: Product (TBD)
- Team: CapeControl Product + Engineering
- Reviewers: Security Lead (TBD), Compliance/Legal (TBD), Product Lead (TBD), Engineering Lead (TBD), Ops Lead (TBD)
- Created: 2026-03-22
- Target Decision Date: 2026-04-05
- Pilot Window: 2 weeks

## Pilot Calendar

- Kickoff and owner lock: 2026-03-22
- Baseline complete: 2026-03-26
- Live pilot start: 2026-03-29
- Week 1 checkpoint: 2026-04-02
- Final scorecard freeze: 2026-04-04
- Go/no-go decision: 2026-04-05

## Owner Assignments

- Owner assignment artifact: docs/evidence/OPCLAW-PILOT-001/owner-assignment-template.csv

| Function | Role | Named Owner | Backup | Status |
| --- | --- | --- | --- | --- |
| Product | Pilot accountable owner | TBD | TBD | Open |
| Engineering | Implementation owner | TBD | TBD | Open |
| Security | Control and review owner | TBD | TBD | Open |
| Compliance/Legal | Policy and data owner | TBD | TBD | Open |
| Operations | Support and incident owner | TBD | TBD | Open |

## Pilot User Roster

- Roster artifact: docs/evidence/OPCLAW-PILOT-001/pilot-roster-template.csv
- Baseline checklist artifact: docs/evidence/OPCLAW-PILOT-001/baseline-task-checklist.md
- Target size: 5-10 users
- Mix target:
  - 2-3 frequent Slack users
  - 2-3 project managers or operations users
  - 1-2 engineering users for technical feedback
  - 1 security/compliance observer

## Execution Status Snapshot

- Overall pilot program (OPCLAW-PILOT-001): In Progress (started 2026-03-22)
- Owner and baseline definition (OPCLAW-PILOT-101): In Progress
- Pilot roster and manager approvals (OPCLAW-PILOT-106): In Progress
- Baseline task checklist artifact prepared: Yes (2026-03-22)
- Owner assignment template prepared: Yes (2026-03-22)
- Telemetry and guardrails implementation (OPCLAW-PILOT-002/102/103): Not Started

## 1. Purpose

Run a controlled internal pilot to evaluate OpenClaw-based workflows before any customer-facing offer.

This RFC defines scope, controls, metrics, operating model, and go/no-go gates.

## 2. Problem Statement

Current workflows require manual copy/paste and context switching across tools. We need to validate whether agent-assisted execution can reduce time and error rates while meeting security and compliance requirements.

## 3. Goals

- Validate measurable productivity gains on selected workflows.
- Validate reliability and human oversight patterns.
- Validate security, privacy, and auditability controls.
- Validate cost per successful task against baseline.

## 4. Non-Goals

- No external customer rollout during this pilot.
- No autonomous high-impact actions without explicit approval.
- No broad integration expansion beyond pilot scope.

## 5. Pilot Scope

- Pilot users: 5-10 internal users.
- Use cases (max 2):
  - Use case A: Support inbox triage and drafting (Slack-assisted)
  - Use case B: Project status brief generation from approved internal docs
- Data class: non-sensitive or sanitized internal data only.
- Integrations:
  - Week 1: one collaboration integration (for example Slack).
  - Week 2: optional second integration if Week 1 passes safety checks.

## 6. Architecture Summary

- Runtime: OpenClaw workload running inside OpenShell sandbox with policy enforcement and isolated execution.
- Model platform: Amazon Bedrock with approved foundation model access and environment-level IAM scoping.
- Identity and access: IAM least-privilege roles and scoped credentials.
- Logging and observability: centralized logs with event and tool-call tracing.
- Safety controls: human approval step for high-impact actions.

## 7. Security and Compliance Requirements (Hard Gates)

All items below must be true to continue or launch externally:

- Least privilege enforced for all credentials and connectors.
- Full audit trail enabled for prompts, tool calls, and outcomes.
- Data retention policy documented and implemented.
- Blocklist/allowlist controls enabled for tools and destinations.
- Incident response runbook documented and tested once.
- No critical unresolved findings from security/compliance review.

## 8. Success Metrics

Baseline values must be captured before Week 2 live pilot.

- Time saved per task: target >= 30%.
- First-pass task success rate: target >= 80%.
- Human escalation rate: target <= 20%.
- Critical error rate: target = 0.
- User satisfaction (internal): target >= 4.0/5.
- Cost per completed task: <= manual baseline equivalent.

## 9. Measurement Plan

- Baseline period: 2026-03-22 to 2026-03-26
- Pilot measurement period: 2026-03-29 to 2026-04-05
- Sample size target per use case: >= 40 tasks
- Data sources:
  - Task timestamps
  - Outcome labels (success/failure/escalated)
  - Incident log
  - Cost telemetry
  - User survey
- Reporting artifact: docs/evidence/OPCLAW-PILOT-001/scorecard-template.md
- Pilot roster artifact: docs/evidence/OPCLAW-PILOT-001/pilot-roster-template.csv
- Baseline checklist artifact: docs/evidence/OPCLAW-PILOT-001/baseline-task-checklist.md
- Owner assignment artifact: docs/evidence/OPCLAW-PILOT-001/owner-assignment-template.csv

## 10. Two-Week Execution Plan

### Week 1 (Setup and Controlled Testing)

- Day 1-2: finalize use cases, owners, metrics, baseline method.
- Day 2-3: configure environment, IAM, logging, and guardrails.
- Day 3-4: implement use case A with human-in-the-loop approvals.
- Day 4-5: implement use case B and run dry tests.
- Day 5: security/compliance checkpoint.

### Week 2 (Live Internal Pilot)

- Day 6-7: launch to limited pilot users.
- Day 7-8: monitor failures, escalations, and user friction.
- Day 8-9: tune prompts, tools, and policy controls.
- Day 9-10: compare against baseline and finalize scorecard.
- Day 10: go/no-go decision meeting.

## 11. RACI

- Product owner: accountable for pilot scope and outcomes.
- Engineering owner: accountable for implementation and reliability.
- Security owner: accountable for controls and approval.
- Compliance/legal owner: accountable for policy alignment.
- Operations owner: accountable for support and incident response.

Fill-in:

- Product: Product Lead (TBD)
- Engineering: Engineering Lead (TBD)
- Security: Security Lead (TBD)
- Compliance/Legal: Compliance Lead (TBD)
- Operations: Ops Lead (TBD)

## 12. Risk Register

- Hallucinated or incorrect action recommendations.
  - Mitigation: mandatory approval on high-impact steps, deterministic checks.
- Over-permissioned integrations.
  - Mitigation: scoped credentials and periodic permission review.
- Data leakage or improper retention.
  - Mitigation: redaction filters, retention controls, and audit logging.
- Cost spikes under load.
  - Mitigation: budget thresholds and usage alerts.

## 13. Go/No-Go Criteria

### Go

- All hard security/compliance gates pass.
- At least 5 of 6 success metrics meet target.
- No critical incidents without verified mitigation.
- Support and rollback playbooks ready.

### Conditional Go

- All hard gates pass.
- Exactly one performance metric misses target by < 10%.
- Remediation plan approved with owner and timeline.

### No-Go

- Any hard gate fails.
- Any unresolved critical security or compliance finding.
- Critical error recurrence without deterministic mitigation.

## 14. External Offering Preconditions

Before customer-facing release:

- Offer in assisted mode first (not fully autonomous).
- Narrow workflow scope with explicit usage policy.
- Customer opt-in, monitoring, and documented support boundaries.
- Formal privacy/security review sign-off.

## 15. Decision Log

- 2026-03-22: RFC created and approved for planning with internal-only pilot scope.
- 2026-04-05: Go/no-go decision scheduled.

Decision meeting input artifact:

- docs/evidence/OPCLAW-PILOT-001/scorecard-template.md

## 16. Approvals

- Product: <approve/reject> <date>
- Engineering: <approve/reject> <date>
- Security: <approve/reject> <date>
- Compliance/Legal: <approve/reject> <date>
- Operations: <approve/reject> <date>
