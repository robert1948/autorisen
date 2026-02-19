# Master Project Plan — autorisen

Snapshot: 2025-11-14

Canonical plan notice

- Canonical plan: `docs/project-plan.csv`.
- The PLAN block in this document is auto-synced by `scripts/plan_sync.py`.
- Legacy narrative in this document may be historical/outdated; follow `docs/SYSTEM_SPEC.md` and `docs/project-plan.csv` for authoritative scope and status.

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
  - Legacy status vocabulary note: the canonical statuses are `planned`, `in_progress`, `blocked`, `done` (see `docs/project-plan.csv`).
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
| DOCS-001 | Derive downstream management artifacts from SYSTEM_SPEC | docs | done | P0 | 2026-01-06 |
| SPEC-001 | Fill in Auth Flows details (login/refresh/logout) to match implementation | docs | done | P0 | 2026-02-10 |
| SPEC-002 | Fill in CSRF policy details (token source/cookie/header/protected endpoints) | docs | done | P0 | 2026-02-12 |
| SPEC-003 | Define Session Guarantees and non-guarantees | docs | planned | P1 |  |
| SPEC-004 | Define Frozen vs Flexible areas in spec | docs | planned | P1 |  |
| SPEC-005 | Define Testing determinism requirements (time/email/rate-limiting) | docs | planned | P1 |  |
| SPEC-006 | Define 'green CI' guarantees + mocking boundaries | docs | planned | P1 |  |
| SPEC-007 | Define development rules (branching/merge/commit discipline) | docs | planned | P2 |  |
| SPEC-008 | Define deployment rules (approvals/rollback expectations) | docs | planned | P1 |  |
| SPEC-009 | Define migration rules (approvals required; no implicit migrations) | docs | done | P0 | 2026-02-12 |
| SPEC-010 | Define roadmap unlock criteria (NEXT-003 + production launch) | docs | done | P2 | 2026-02-03 |
| SPEC-011 | Define change control process (who may edit/review/versioning) | docs | planned | P1 |  |
| MVP-ROUTES-001 | Publish MVP pages & routes checklist (no code scaffolding) | docs | done | P0 | 2026-02-19 |
| MVP-ROUTES-002 | Define onboarding gate rules (cannot skip onboarding) | docs | planned | P0 |  |
| DB-001 | Establish Postgres MVP data scope as system-of-record | docs | done | P0 | 2026-01-06 |
| DB-002 | Publish DB migrations playbook (approval gate; no manual prod changes) | docs | done | P0 | 2026-02-19 |
| DB-003 | Document DB observability/maintenance expectations (health/logging/backups/local reset) | docs | done | P1 | 2026-02-13 |
| NEXT-003 | Execute PayFast production transaction | management | in-progress | P0 | 2026-02-15 |
| PAY-INTENT-001 | Maintain payments intent-only scope (no implementation in MVP) | management | done | P0 | 2026-01-06 |
| GOV-001 | Publish auth changes playbook (guardrails for auth/csrf edits) | docs | done | P0 | 2026-02-19 |
| GOV-002 | Publish release & deploy playbook (deploy rules + rollback) | docs | done | P1 | 2026-02-13 |
| GOV-003 | Perform management freeze review and publish results | management | done | P0 | 2026-02-19 |
| ROUTING-SPA-API-001 | Fix SPA fallback intercepting /api and /sw.js (autorisen) | engineering | done | P0 | 2026-02-09 |
| CHORE-REPO-001 | Update ignore files for repo hygiene | engineering | done | P2 | 2026-02-10 |
| CI-DOCKER-001 | Add manual Docker Hub publish workflow | engineering | done | P2 | 2026-02-10 |
| DOC-OPS-DOCKER-001 | Update Docker Hub repo General page metadata | ops | done | P2 | 2026-02-10 |
| WO-OPS-REPO-HYGIENE-001 | Repo hygiene: declutter autorisen (gitignore + cleanup tools + evidence policy) + clean docs/project-plan.csv formatting | VS_Chat | Planned | P0 |  |
| WO-DASH-PROJECT-STATUS-VAL-001 | Dashboard: project status returns non-null value | VS_Chat | In Review | P0 | 2026-02-12 |
| FEAT-AGENTS-001 | Create 4 AI agent modules (code-review/security-scan/perf-opt/doc-gen) + wire into router | engineering | done | P0 | 2026-02-18 |
| FEAT-PAY-ALIGN-001 | Align payment plans to Free/Pro/Enterprise with ZAR pricing | engineering | done | P0 | 2026-02-18 |
| FEAT-LANDING-001 | Fix landing page CTAs and feature promises | engineering | done | P1 | 2026-02-18 |
| FEAT-OAUTH-001 | Activate Google and LinkedIn OAuth login (end-to-end) | engineering | done | P0 | 2026-02-18 |
| FEAT-DASH-WELCOME-001 | Wire dashboard WelcomeHeader to live API data | engineering | done | P0 | 2026-02-18 |
| FEAT-ONBOARD-PROFILE-001 | Onboarding profile page: dark theme + pre-fill from OAuth + optional fields | engineering | done | P1 | 2026-02-19 |
| FEAT-TRIAL-BTN-001 | Smart trial button: check auth status before redirect | engineering | done | P1 | 2026-02-19 |
| FEAT-LOGIN-NOTIFY-001 | Send login email notification for all providers (Google/LinkedIn/email) | engineering | done | P0 | 2026-02-19 |
| FIX-DDOS-OAUTH-001 | Exempt OAuth callbacks from DDoS burst detection | engineering | done | P1 | 2026-02-18 |
| FIX-DASH-PREVIEW-001 | Fix dashboard stuck in read-only preview mode | engineering | done | P0 | 2026-02-19 |

<!-- PLAN:END -->
