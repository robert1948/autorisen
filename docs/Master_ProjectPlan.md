# Master Project Plan — CapeControl

**Snapshot:** 2026-03-15 | **Build:** 539 | **Platform:** https://cape-control.com

> **Canonical plan:** `docs/project-plan.csv`.
> The PLAN block at the bottom of this document is auto-synced by `scripts/plan_sync.py --apply`.
> See also: `docs/agents.md`, `docs/SYSTEM_SPEC.md`

<!-- markdownlint-disable MD013 -->

## Overview

CapeControl is a production SaaS platform for AI-powered business automation, deployed as Docker containers to Heroku. The platform provides project management, AI instruction generation, agent marketplace, compliance tooling, and workflow capsules for regulated SMBs.

**Current state:** 86 tasks tracked, 81 done, 5 planned.

## Architecture

- **Backend:** FastAPI (Python) with modular agent-based design
- **Frontend:** React + TypeScript + Vite + Tailwind CSS
- **Database:** PostgreSQL (Heroku `postgresql-rigid-25868`)
- **AI Provider:** Anthropic (Claude 3 Haiku for budget, Claude Sonnet 4 for premium)
- **Payments:** PayFast (ZAR), Stripe planned for international (Q3 2026)
- **Deployment:** Docker → Heroku Container Registry → `capecraft` app

## Workstreams

### Completed (Q1 2026)

| Area | Key Deliverables |
|---|---|
| **Auth & Security** | JWT + CSRF dual-token, Google/LinkedIn OAuth, MFA with encrypted TOTP, DDoS protection, prod secret guard, Sentry |
| **Payments** | PayFast integration (ITN, subscriptions, billing cycle), Free/Pro/Enterprise plans with ZAR pricing |
| **Plan Enforcement** | Project limits (Free: 3, Pro: 25, Enterprise: unlimited), AI instructions gated to paid plans, execution/agent quotas |
| **AI Features** | CapeAI chat, AI project instruction sheets (guided format), model router (budget/premium), usage tracking |
| **Marketplace** | Real agent registry, download counts, trending algorithm, featured agents |
| **RAG & Capsules** | Controlled retrieval pipeline, evidence trace, workflow capsule engine |
| **Dashboard** | Live stat cards, project management CRUD, onboarding checklist, AppShell layout |
| **Compliance** | Audit trail, evidence pack PDF export, tenant isolation, RBAC |
| **Performance** | Lighthouse 98 (mobile), GZip, lazy routes, non-blocking mount |
| **Docs & Quality** | 220+ tests, deployment checklist, security posture docs, beta pilot playbook |

### In Progress / Planned

| Area | Status | Target |
|---|---|---|
| **Beta User Shipment** | Ready to invite (P0) | Q1 2026 |
| **Pro Plan Purchase Flow** | Todo — PayFast checkout (P0) | Q2 2026 |
| **Dashboard Metrics Polish** | Todo — real-time charts (P1) | Q2 2026 |
| **E2E Test Coverage** | Todo — Playwright (P1) | Q2 2026 |
| **Stripe International** | Deferred (P2) | Q3 2026 |

## How to Update

1. Edit `docs/project-plan.csv` for task changes (status, owner, priority).
2. Run `python scripts/plan_sync.py --apply` to regenerate the table below.
3. Use `make project-info` for a live summary.
4. Commit: `docs(plan): <short description>`

## Key Commands

```bash
make project-info          # Live stats from CSV
make codex-plan-diff       # Check for drift
make codex-plan-apply      # Regenerate table from CSV
make codex-test            # Run tests (SQLite)
make codex-test-pg         # Run tests (Postgres)
ALLOW_PROD=1 ALLOW_PROD_DEPLOY=YES make deploy  # Production deploy
```

## Risk Register

| Risk | Impact | Mitigation |
|---|---|---|
| AI model retirement (Anthropic deprecates models) | Service outage | Model router with fallback; tested alternatives on file |
| Free plan AI cost overrun | Margin erosion | Platform budget circuit breaker, per-user execution limits |
| PayFast webhook failures | Billing gaps | ITN validation, idempotent processing, transaction logging |
| Deployment regression | Downtime | Rollback checklist, tagged images, post-deploy smoke tests |

<!-- PLAN:BEGIN -->

| Id | Task | Owner | Status | Priority | Completion_date |
| --- | --- | --- | --- | --- | --- |
| DOCS-001 | Derive downstream management artifacts from SYSTEM_SPEC | docs | done | P0 | 2026-01-06 |
| SPEC-001 | Fill in Auth Flows details (login/refresh/logout) to match implementation | docs | done | P0 | 2026-02-10 |
| SPEC-002 | Fill in CSRF policy details (token source/cookie/header/protected endpoints) | docs | done | P0 | 2026-02-12 |
| SPEC-003 | Define Session Guarantees and non-guarantees | docs | done | P1 | 2026-02-19 |
| SPEC-004 | Define Frozen vs Flexible areas in spec | docs | done | P1 | 2026-02-19 |
| SPEC-005 | Define Testing determinism requirements (time/email/rate-limiting) | docs | done | P1 | 2026-02-20 |
| SPEC-006 | Define 'green CI' guarantees + mocking boundaries | docs | done | P1 | 2026-02-20 |
| SPEC-007 | Define development rules (branching/merge/commit discipline) | docs | done | P2 | 2026-02-20 |
| SPEC-008 | Define deployment rules (approvals/rollback expectations) | docs | done | P1 | 2026-02-20 |
| SPEC-009 | Define migration rules (approvals required; no implicit migrations) | docs | done | P0 | 2026-02-12 |
| SPEC-010 | Define roadmap unlock criteria (NEXT-003 + production launch) | docs | done | P2 | 2026-02-03 |
| SPEC-011 | Define change control process (who may edit/review/versioning) | docs | done | P1 | 2026-02-20 |
| MVP-ROUTES-001 | Publish MVP pages & routes checklist (no code scaffolding) | docs | done | P0 | 2026-02-19 |
| MVP-ROUTES-002 | Define onboarding gate rules (cannot skip onboarding) | docs | done | P0 | 2026-02-19 |
| DB-001 | Establish Postgres MVP data scope as system-of-record | docs | done | P0 | 2026-01-06 |
| DB-002 | Publish DB migrations playbook (approval gate; no manual prod changes) | docs | done | P0 | 2026-02-19 |
| DB-003 | Document DB observability/maintenance expectations (health/logging/backups/local reset) | docs | done | P1 | 2026-02-13 |
| NEXT-003 | Execute PayFast production transaction | management | done | P0 | 2026-02-19 |
| PAY-INTENT-001 | Maintain payments intent-only scope (no implementation in MVP) | management | done | P0 | 2026-01-06 |
| GOV-001 | Publish auth changes playbook (guardrails for auth/csrf edits) | docs | done | P0 | 2026-02-19 |
| GOV-002 | Publish release & deploy playbook (deploy rules + rollback) | docs | done | P1 | 2026-02-13 |
| GOV-003 | Perform management freeze review and publish results | management | done | P0 | 2026-02-19 |
| ROUTING-SPA-API-001 | Fix SPA fallback intercepting /api and /sw.js (autorisen) | engineering | done | P0 | 2026-02-09 |
| CHORE-REPO-001 | Update ignore files for repo hygiene | engineering | done | P2 | 2026-02-10 |
| CI-DOCKER-001 | Add manual Docker Hub publish workflow | engineering | done | P2 | 2026-02-10 |
| DOC-OPS-DOCKER-001 | Update Docker Hub repo General page metadata | ops | done | P2 | 2026-02-10 |
| WO-OPS-REPO-HYGIENE-001 | Repo hygiene: declutter autorisen (gitignore + cleanup tools + evidence policy) + clean docs/project-plan.csv formatting | VS_Chat | done | P0 | 2026-02-19 |
| WO-DASH-PROJECT-STATUS-VAL-001 | Dashboard: project status returns non-null value | VS_Chat | done | P0 | 2026-02-19 |
| FEAT-AGENTS-001 | Create 4 AI agent modules (code-review/security-scan/perf-opt/doc-gen) + wire into router | engineering | done | P0 | 2026-02-18 |
| FEAT-PAY-ALIGN-001 | Align payment plans to Free/Pro/Enterprise with ZAR pricing | engineering | done | P0 | 2026-02-19 |
| FEAT-LANDING-001 | Fix landing page CTAs and feature promises | engineering | done | P1 | 2026-02-18 |
| FEAT-OAUTH-001 | Activate Google and LinkedIn OAuth login (end-to-end) | engineering | done | P0 | 2026-02-18 |
| FEAT-DASH-WELCOME-001 | Wire dashboard WelcomeHeader to live API data | engineering | done | P0 | 2026-02-18 |
| FEAT-ONBOARD-PROFILE-001 | Onboarding profile page: dark theme + pre-fill from OAuth + optional fields | engineering | done | P1 | 2026-02-19 |
| FEAT-TRIAL-BTN-001 | Smart trial button: check auth status before redirect | engineering | done | P1 | 2026-02-19 |
| FEAT-LOGIN-NOTIFY-001 | Send login email notification for all providers (Google/LinkedIn/email) | engineering | done | P0 | 2026-02-19 |
| FIX-AUTH-CSRF-002 | Self-heal login when CSRF token is stale | engineering | done | P0 | 2026-03-16 |
| FIX-ONBOARD-GATE-002 | Block onboarding completion for unverified email accounts | engineering | done | P0 | 2026-03-16 |
| FIX-DDOS-OAUTH-001 | Exempt OAuth callbacks from DDoS burst detection | engineering | done | P1 | 2026-02-18 |
| FIX-DASH-PREVIEW-001 | Fix dashboard stuck in read-only preview mode | engineering | done | P0 | 2026-02-19 |
| FIX-SCAFFOLD-REDIRECT-001 | Replace scaffold route stubs with Navigate redirects and real LogoutAction | engineering | done | P1 | 2026-02-19 |
| FEAT-PAYMENTS-FLAG-001 | Enable payments feature flag by default (opt-out pattern) | engineering | done | P1 | 2026-02-19 |
| GOV-FREEZE-UPDATE-001 | Update FREEZE_REVIEW §3.3 and §3.4 from PLACEHOLDER to FROZEN | docs | done | P2 | 2026-02-19 |
| FEAT-DASHBOARD-OVERHAUL-001 | Dashboard overhaul with AppShell sidebar and mobile bottom nav | engineering | done | P1 | 2026-02-19 |
| BP-RAG-001 | Design and implement controlled RAG pipeline (approved-doc-only retrieval) | engineering | done | P0 | 2026-02-24 |
| BP-RAG-002 | Implement evidence output layer (citations + source trace + timestamps) | engineering | done | P0 | 2026-02-24 |
| BP-RAG-003 | Implement unsupported policy enforcement (refuse ungrounded answers) | engineering | done | P0 | 2026-02-24 |
| BP-CAPSULE-001 | Design and implement workflow capsule engine | engineering | done | P1 | 2026-02-24 |
| BP-TENANT-001 | Implement tenant isolation and granular RBAC | engineering | done | P1 | 2026-02-24 |
| BP-AUDIT-001 | Implement audit export and evidence pack generation | engineering | done | P1 | 2026-02-24 |
| PAY-010 | Complete PayFast ITN ingestion + transaction logging | engineering | done | P0 | 2026-03-02 |
| PAY-011 | Payment return page UX — success polling + cancel context | engineering | done | P0 | 2026-03-02 |
| PAY-012 | Subscription management UI — real billing data | engineering | done | P0 | 2026-03-02 |
| PAY-013 | Free → Pro conversion flow — upgrade prompts + plan awareness | engineering | done | P0 | 2026-03-02 |
| PAY-014 | Automated billing cycle + missed payment logging + reminder emails | engineering | done | P0 | 2026-03-04 |
| PROD-001 | Connect marketplace to real agent registry API | engineering | done | P0 | 2026-03-01 |
| PROD-003 | Connect onboarding checklist to real backend API | engineering | done | P0 | 2026-03-01 |
| PROD-004 | Evidence pack PDF export (audit module + CompliancePage export button) | engineering | done | P0 | 2026-03-01 |
| PROD-007 | Dashboard V2 — wire stat cards to real usage data | engineering | done | P0 | 2026-03-01 |
| HARD-005 | Add dedicated privacy policy page | engineering | done | P1 | 2026-02-28 |
| HARD-007 | Add Sentry error tracking | engineering | done | P1 | 2026-02-28 |
| HARD-008 | Implement database backup schedule | engineering | done | P1 | 2026-02-28 |
| SEC-001 | Add prod secret_key startup guard | engineering | done | P0 | 2026-03-04 |
| SEC-002 | Encrypt MFA TOTP secrets at rest | engineering | done | P0 | 2026-03-04 |
| SEC-003 | Wire admin invite email delivery | engineering | done | P1 | 2026-03-04 |
| QUAL-001 | Add smoke tests for untested modules | engineering | done | P1 | 2026-03-04 |
| QUAL-002 | Remove hardcoded marketplace 4.5 star rating | engineering | done | P1 | 2026-03-04 |
| QUAL-003 | Update stale deployment checklist | docs | done | P2 | 2026-03-04 |
| FEAT-MKTPLACE-001 | Marketplace download counts + trending algorithm | engineering | done | P2 | 2026-03-04 |
| FEAT-MKTPLACE-002 | Featured agents admin flag | engineering | done | P2 | 2026-03-04 |
| ENG-OAUTH-VERIFY-001 | Google OAuth brand verification approved by Google | engineering | done | P0 | 2026-03-03 |
| ENG-PERF-001 | Lighthouse mobile performance 71 → 98 (GZip + lazy routes + non-blocking mount) | engineering | done | P0 | 2026-03-08 |
| BP-STRIPE-001 | Integrate Stripe for international payment rails | engineering | todo | P2 |  |
| BP-BETA-001 | Launch closed beta with 10–20 compliance-heavy SMBs | management | done | P0 | 2026-02-24 |
| BP-MONITOR-001 | Implement monitoring and alerting infrastructure (runbooks + backups) | engineering | done | P1 | 2026-02-24 |
| BP-SECURITY-DOC-001 | Publish security posture documentation for buyer due diligence | docs | done | P1 | 2026-02-24 |
| BP-DOCS-ALIGN-001 | Audit and align docs/agents.md with actual codebase | docs | done | P2 | 2026-02-24 |
| FEAT-INSTRUCT-001 | AI-generated project instruction sheets | engineering | done | P1 | 2026-03-15 |
| FIX-MODEL-001 | Fix retired Haiku model references across backend | engineering | done | P0 | 2026-03-15 |
| FIX-USAGE-001 | Fix usage tracking — missing db.commit() | engineering | done | P0 | 2026-03-15 |
| FIX-RETRY-001 | Fix infinite retry loop on project instructions error | engineering | done | P1 | 2026-03-15 |
| FEAT-PLANLIMIT-001 | Gate project creation by plan limits | engineering | done | P0 | 2026-03-15 |
| FEAT-PLANLIMIT-002 | Gate AI instructions by paid plan | engineering | done | P0 | 2026-03-15 |
| FEAT-INSTRUCT-002 | Expand Next Steps with guided headings and detail | engineering | done | P1 | 2026-03-15 |
| BETA-SHIP-001 | Ship platform to beta users from contact list | management | todo | P0 |  |
| FEAT-UPGRADE-001 | Add Pro plan purchase flow via PayFast | engineering | todo | P0 |  |
| FEAT-DASH-METRICS-001 | Dashboard real-time metrics polish | engineering | todo | P1 |  |
| QUAL-E2E-001 | Add Playwright end-to-end test coverage | engineering | todo | P1 |  |

<!-- PLAN:END -->
