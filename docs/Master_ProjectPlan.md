# Master Project Plan — autorisen

Snapshot: 2025-11-14

See also: `docs/senior_devops.md`

<!-- markdownlint-disable MD013 -->

Overview

- Purpose: keep a single, actionable roadmap for shipping monetization, operational hardening, and UX polish without regressing the production baseline.
- Scope: finish Stripe-backed billing, stand up usage metering, keep Heroku operations healthy, and document release/rollback guardrails.

Scope & MVP definition

- MVP scope (current):
  - Production-ready Stripe billing with hardened webhook handling.
  - Usage metering for AI workloads and dashboard surfacing.
  - Ops automation for security/compliance guardrails.
  - Maintain existing Heroku platform while we assess an ECS migration path.

Workstreams

- Payments (R: backend lead)
  - Finalize Stripe integration, subscription tiers, and metering pipelines.
  - Acceptance: end-to-end subscription purchase succeeds with invoices generated.

- Frontend (R: frontend lead)
  - Deliver payment UI flows and expose metering data in dashboard views.
  - Acceptance: pilot users can self-manage plans without console intervention.

- Platform (R: devops lead)
  - Keep CI pipelines, container builds, and Heroku release automation green.
  - Acceptance: deployments remain reversible and observability dashboards stay healthy.

- Security & Compliance (R: security lead)
  - Run hardening audit, validate secrets sync, and ratify billing data retention.
  - Acceptance: audit checklist complete with evidence stored in shared drive.

- Business Enablement (R: project lead)
  - Align pricing, analytics, and documentation with the technical rollout.
  - Acceptance: launch narrative and docs available before GA toggle.

Authoritative project plan (CSV)

The primary source of truth for actionable tasks is the CSV located at `docs/project-plan.csv`. Edit that file to add, update, or change task rows; the Markdown narrative in this document provides context and milestones but the CSV is the machine-readable, team-facing plan.

Snapshot (from `docs/project-plan.csv`) — 2025-11-14

- Total tasks: 35
- Status counts: todo: 22, in-progress: 1, completed: 12
- Estimated hours: 118 completed, 240 remaining
- Phase focus: payments in-flight; optimization, business, and maintenance queued next

Recent updates (2025-11-14): sanitized the CSV to remove narrative rows, recomputed completion/remaining hours, and regenerated this Markdown snapshot via `scripts/plan_sync.py --apply`. All summary figures now match the authoritative dataset.

Top priority (P0/P1) tasks — quick view

| Task ID | Title | Owner | Status | Estimate | Depends On |
|---|---|---|---|---:|---|
| PAY-001 | Stripe payment integration | backend | in-progress | 16 | AGENT-001 |
| PAY-002 | Subscription tiers and billing logic | backend | todo | 12 | PAY-001 |
| PAY-003 | Usage tracking and metering | backend | todo | 10 | PAY-001 |
| PAY-004 | Payment UI components | frontend | todo | 8 | PAY-001 |
| OPT-001 | Database query optimization and indexing | backend | todo | 8 | FOUND-001 |
| MAINT-001 | Comprehensive security audit and hardening | security | todo | 12 | FOUND-006 |

How to use and update

- Edit `docs/project-plan.csv` for day-to-day task changes (status, owner, estimates). Follow the CSV schema:
  - Required header: id,phase,task,owner,status,priority,dependencies,estimated_hours,completion_date,artifacts,verification,notes,codex_hints
  - `status` must be one of: todo, in-progress, completed, blocked, deferred
  - `completion_date` values (when present) use ISO 8601 (YYYY-MM-DD)
- Commit message convention: `docs(plan): <short description>` (e.g., `docs(plan): mark PAY-001 in-progress`)
- When milestones or high-level narrative shift, update this Markdown to capture context and decisions; link to PRs or Action runs in the CSV `notes` column for traceability.

Automation note

- Use `scripts/plan_sync.py --apply` to regenerate the Markdown snapshot after editing the CSV. `scripts/plan_md_to_csv.py` remains available for one-off conversions from Markdown tables back to CSV if needed.

Milestones & dates (Gantt-style)

| ID | Milestone | Owner | Start | Target | Notes |
|---:|---|---|---:|---:|---|
| M1 | Stripe integration sandbox verified | backend | 2025-11-11 | 2025-11-18 | PAY-001 complete, webhook smoke tests pass |
| M2 | Subscription gating live | backend | 2025-11-18 | 2025-11-22 | PAY-002 feature flags enabled for pilot |
| M3 | Usage metering pipeline operational | backend | 2025-11-22 | 2025-11-29 | PAY-003 backfills + cron schedule validated |
| M4 | Payment UI beta to pilot customers | frontend | 2025-11-24 | 2025-11-30 | PAY-004 flow QA + analytics hooks |
| M5 | Security hardening audit completed | security | 2025-11-25 | 2025-12-02 | MAINT-001 checklist evidence archived |
| M6 | Go-live readiness review | project lead | 2025-12-03 | 2025-12-06 | Cross-team release readiness gate |

RACI (key roles)

| Role | Short | Responsibility |
|---|---|---|
| Project Lead | PL | Prioritize backlog, coordinate releases, publish comms |
| Backend Lead | BE | Own Stripe integration, usage metering, backend tests |
| Frontend Lead | FE | Deliver payment UX, dashboard updates, user testing |
| DevOps Lead | DEVOPS | Maintain CI/CD, observability, release automation |
| Security Lead | SEC | Security reviews, secrets hygiene, compliance evidence |

Risk Register

| ID | Risk | Impact | Likelihood | Mitigation |
|---:|---|---|---:|---|
| R1 | Stripe webhook failures causing billing gaps | High | Medium | Enable idempotency keys, monitor event replay queue, add alerting |
| R2 | Usage metering data loss from worker crashes | High | Medium | Persist events durably, nightly reconciliation job, coverage tests |
| R3 | Deployment regression on Heroku release | Medium | Medium | Keep rollback checklist current, tag container images, smoke-test post deploy |
| R4 | Secrets drift between GitHub and Heroku | High | Low | Continue GitHub → Heroku sync with dry-run logs and approvals |

Operating Cadence

- Daily (async): status in `#autorisen-ops`; flag blockers in `#autorisen-payments`.
- Twice weekly: Payments/Platform sync (Tue & Thu 17:00 UTC) owned by PL.
- On-demand: merge high-priority fixes after at least one reviewer + green CI.

Checklists

Release checklist (minimal)

1. CI green for `ci-health` and `docker-publish` (or run locally).
1. `HEROKU_APP_NAME` and `HEROKU_API_KEY` present in repo secrets.
1. Smoke test `services/health` and payment happy path after deploy.

Rollback checklist

1. Revert release commit and re-run deploy using previous image tag.
1. Verify `/alive` and `/api/health` return 200.
1. Reconcile Stripe events to ensure no duplicate invoices.

Secrets & Infra change checklist

1. Update mapping in `infra/secrets-mapping.json` (reviewed by SEC).
1. Run sync in dry-run (`ci/sync-github-to-heroku.yml`).
1. Approve and run `--apply` in controlled workflow; capture audit link in CSV `notes` column.

Appendix — Helpful commands

```bash
## Validate Stripe webhook forwarding locally
stripe listen --forward-to localhost:8000/api/payment/webhook

## Production health check
curl -sS https://autorisen-dac8e65796e7.herokuapp.com/api/health

## Regenerate Markdown snapshot after CSV edits
python scripts/plan_sync.py --apply
```

Maintainers: ops@example.com, payments@example.com, platform@example.com

<!-- PLAN:BEGIN -->

| Id | Task | Owner | Status | Priority | Completion_date |
| --- | --- | --- | --- | --- | --- |
| AUTH-001 | Core authentication infrastructure | backend | completed | P0 | 2025-11-07 |
| AUTH-002 | Login/Register UI components | frontend | completed | P0 | 2025-11-07 |
| AUTH-003 | CSRF protection implementation | backend | completed | P0 | 2025-11-07 |
| AUTH-004 | MFA system (TOTP) | backend | completed | P0 | 2025-11-07 |
| AUTH-005 | Security hardening & tests | backend | completed | P0 | 2025-11-07 |
| AUTH-006 | Production authentication validation | backend | completed | P0 | 2025-11-07 |
| FE-001 | React SPA foundation | frontend | completed | P1 | 2025-11-07 |
| FE-002 | Routing & navigation | frontend | completed | P1 | 2025-11-07 |
| FE-003 | Auth context & state management | frontend | completed | P1 | 2025-11-07 |
| FE-004 | Login page + form | frontend | completed | P0 | 2025-11-07 |
| FE-005 | Logo integration & favicon system | frontend | completed | P1 | 2025-11-07 |
| FE-006 | Authentication flow testing | frontend | completed | P0 | 2025-11-07 |
| FE-007 | Full-width layout optimization | frontend | completed | P1 | 2025-11-09 |
| FE-008 | Dynamic version display | frontend | completed | P1 | 2025-11-09 |
| FE-009 | TypeScript error resolution | frontend | completed | P1 |  |
| FE-010 | Page content creation | frontend | completed | P1 |  |
| FE-011 | Feature flag infrastructure | frontend | completed | P1 | 2025-12-16 |
| FE-012 | Route gating & feature protection | frontend | completed | P1 | 2025-12-16 |
| UI-001 | Logo component with size variants | frontend | completed | P2 | 2025-11-07 |
| UI-002 | Responsive logo design system | frontend | completed | P2 | 2025-11-07 |
| DEVOPS-001 | Docker containerization | devops | completed | P1 | 2025-11-07 |
| DEVOPS-002 | Heroku deployment pipeline | devops | completed | P0 | 2025-11-07 |
| DEVOPS-003 | Environment configuration | devops | completed | P1 | 2025-11-07 |
| DEVOPS-004 | Database migrations | devops | completed | P1 | 2025-11-07 |
| DEVOPS-005 | CI/CD GitHub Actions | devops | completed | P1 | 2025-11-07 |
| DEVOPS-035 | Production deployment | devops | completed | P0 | 2025-11-07 |
| DEVOPS-036 | Static asset optimization | devops | completed | P1 | 2025-11-07 |
| DEVOPS-006 | Staging deployment automation | devops | completed | P1 | 2025-12-16 |
| CODE-001 | Python linting & optimization | backend | completed | P1 | 2025-12-18 |
| CODE-002 | Markdown documentation linting | docs | completed | P1 | 2025-11-09 |
| CODE-003 | Backend performance optimizations | backend | completed | P1 | 2025-11-09 |
| CHAT-001 | ChatKit backend integration | backend | completed | P0 | 2025-11-10 |
| CHAT-002 | Agent registry database schema | backend | completed | P0 | 2025-11-08 |
| CHAT-003 | Flow orchestration API | backend | completed | P0 | 2025-11-10 |
| CHAT-004 | ChatKit frontend components | frontend | completed | P0 | 2025-11-13 |
| CHAT-005 | Agent marketplace UI | frontend | completed | P1 | 2026-01-01 |
| CHAT-006 | Developer agent builder | frontend | todo | P1 |  |
| CHAT-007 | Onboarding flow integration | frontend | todo | P1 |  |
| PAY-001 | PaymentsAgent service | backend | completed | P0 | 2025-11-10 |
| PAY-002 | Checkout API + ChatKit tool | backend | completed | P0 | 2025-11-10 |
| PAY-003 | ITN ingestion & audit log | backend | completed | P0 | 2026-01-01 |
| PAY-004 | Payments DB schema | backend | completed | P0 | 2026-01-01 |
| PAY-006 | Payments UI entry points | frontend | completed | P1 | 2026-01-01 |
| PAY-007 | Security & validation | security | completed | P0 | 2026-01-01 |
| PAY-008 | Configure production PayFast env | devops | todo | P0 |  |
| PAY-009 | Create live test product | product | completed | P0 | 2026-01-06 |
| PAY-010 | Execute live production transaction | qa | todo | P0 |  |
| PAY-011 | Verify ITN and Audit Logs | backend | todo | P0 |  |
| AI-001 | Anthropic API integration | backend | completed | P0 | 2026-01-02 |
| AI-002 | Model configuration update | backend | completed | P0 | 2026-01-02 |
| AI-003 | API testing infrastructure | devops | completed | P1 | 2026-01-02 |
| AI-004 | Anthropic integration documentation | docs | completed | P1 | 2026-01-02 |
| AI-005 | Streaming response implementation | backend | todo | P1 |  |
| AI-006 | Tool use implementation | backend | todo | P0 |  |
| AI-007 | Vision capability implementation | backend | todo | P2 |  |
| AI-008 | Conversation history | backend | todo | P1 |  |
| NEXT-001 | Configure PayFast production environment | devops | todo | P0 |  |
| NEXT-002 | Create live R5 verification product | backend | completed | P0 | 2026-01-06 |
| NEXT-003 | Execute live PayFast production transaction | qa | todo | P0 |  |
| NEXT-004 | Verify PayFast ITN and audit logs | backend | todo | P0 |  |
| NEXT-005 | Remove payment feature flag after verification | frontend | todo | P0 |  |
| NEXT-006 | Tag production release v0.2.11 | devops | todo | P1 |  |
| NEXT-007 | Implement Developer Agent Builder UI | frontend | completed | P1 | 2026-01-02 |
| NEXT-008 | Integrate onboarding checklist UI | frontend | completed | P1 | 2026-01-02 |
| NEXT-009 | Enable agent tool/function calling | backend | todo | P0 |  |
| NEXT-010 | Add streaming responses to ChatKit agents | backend | todo | P1 |  |
| NEXT-011 | Production smoke-test checklist run | qa | todo | P0 |  |
| NEXT-012 | Update Release Runbook with payment verification | docs | todo | P1 |  |

<!-- PLAN:END -->
