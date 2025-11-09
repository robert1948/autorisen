# Master Project Plan — autorisen

**Snapshot:** 2025-10-18

<!-- markdownlint-disable MD013 -->

## Contents

- [Purpose](#purpose)
- [How to Use This Document](#how-to-use-this-document)
- [Legend](#legend)
- [Master Milestones (High Level)](#master-milestones-high-level)
- [Task Overview](#task-overview)
- [Detailed Tasks](#detailed-tasks)
- [Communications & Reporting](#communications--reporting)
- [Risks & Mitigations](#risks--mitigations)
- [Templates](#templates)
- [Appendix — Useful Commands](#appendix--useful-commands)
- [Maintainers](#maintainers)

## Purpose

- Provide a single, actionable project plan derived from `docs/senior_devops.md` for ops, infra, and product to execute and update.
- Make tasks small, assign owners, set target dates, list dependencies, acceptance criteria, and status.

## How to Use This Document

- Owners update their task status inline (To Do / In Progress / Done) and append short notes with date + initials.
- The project lead runs weekly triage against this plan and updates priorities.

## Legend

- **R:** Responsible (executor)
- **A:** Accountable (decision owner)
- **S:** Stakeholders / Support
- **Dates:** Target dates formatted as YYYY-MM-DD

## Master Milestones (High Level)

1. Restore production auth service and publish healthy root/health endpoints (Target: 2025-10-16)
1. Harden Heroku container release workflow with repeatable scripts (Target: 2025-10-18)
1. Stabilize database migrations and local developer setup (Target: 2025-10-20)
1. Finalize ChatKit rollout and analytics instrumentation (Target: 2025-10-22)

## Task Overview

| ID  | Title                                           | Target     | Owner (R/A)              | Status |
| --- | ----------------------------------------------- | ---------- | ------------------------ | ------ |
| T1  | Restore Auth Router and Redeploy to Heroku      | 2025-10-16 | backend lead / ops       | Done |
| T2  | Structured Login Debug Logging Rollout          | 2025-10-16 | backend lead             | Done |
| T3  | Root Health Responder for Monitoring            | 2025-10-15 | backend                  | Done |
| T4  | Automate Container Release Workflow             | 2025-10-18 | ops                      | In Progress |
| T5  | Fix Database Migration Issues                   | 2025-10-20 | backend / data           | Done |
| T6  | ChatKit Rollout Validation                      | 2025-10-22 | product / backend        | In Progress |
| T7  | Update Developer Documentation & Tooling        | 2025-10-19 | docs lead / backend      | In Progress |
| T8  | Resolve Production 404s on Flows/Agents APIs    | 2025-10-19 | backend lead / product   | To Do |
| T9  | Align User Profile FK Types with UUID IDs       | 2025-10-18 | backend / data           | To Do |
| T10 | Stand Up Analytics Tracking Endpoint            | 2025-10-20 | backend / product analytics | To Do |
| T11 | Enable Google/LinkedIn Social Login (Scaffold)  | 2025-10-22 | backend / frontend auth  | In Progress |
| T12 | Enforce Email Verification for Password Accounts| 2025-10-19 | backend / frontend auth  | Done |

## Detailed Tasks

### Task T1 — Restore Auth Router and Redeploy to Heroku

- **Owner (R/A):** backend lead / ops
- **Target:** 2025-10-16
- **Dependencies:** Heroku CLI authenticated; `HEROKU_API_KEY` exported locally
- **Acceptance Criteria:** Heroku logs show successful boot, GET `/` returns JSON payload, login route available
- **Status:** Done — 2025-10-16 — release v244 deployed; health + auth endpoints verified (ops)
- **Steps:**
  1. Confirm `backend/src/modules/auth/router.py` matches service-based implementation (no `modules.auth.security`). (R)
  1. Rebuild container with `docker build --no-cache -t autorisen:local .` and push to Heroku registry. (R)
  1. Release to Heroku and smoke test `/` and `/api/health` endpoints. (R)
  1. Document release outcome in `docs/DEPLOYMENTS.md`. (R)

### Task T2 — Structured Login Debug Logging Rollout

- **Owner (R/A):** backend lead
- **Target:** 2025-10-16
- **Dependencies:** Task T1 deployment
- **Acceptance Criteria:** Logs visible in Heroku tail with expected `auth.login.*` messages
- **Status:** Done — 2025-10-15 — logs present after deployment (backend)
- **Steps:**
  1. Add contextual debug logs around login flow (attempt, rate-limit, success, failure). (R)
  1. Verify logs in staging/Heroku to aid diagnostics. (R)

### Task T3 — Root Health Responder for Monitoring

- **Owner (R/A):** backend
- **Target:** 2025-10-15
- **Dependencies:** Task T1 redeploy
- **Acceptance Criteria:** Heroku router logs show 200 for GET `/` with JSON body
- **Status:** Done — 2025-10-15 — verified locally and in logs (backend)
- **Steps:**
  1. Add FastAPI route for `/` returning service heartbeat JSON. (R)
  1. Confirm 200 response via curl/Heroku logs. (R)

### Task T4 — Automate Container Release Workflow

- **Owner (R/A):** ops
- **Target:** 2025-10-18
- **Dependencies:** Task T1
- **Acceptance Criteria:** One-command/manual workflow redeploys latest `main`; logs stored with digest
- **Status:** In Progress — 2025-10-17 — `make deploy-heroku` run successfully; script + GitHub Action outstanding (ops)
- **Steps:**
  1. Script build/tag/push/release sequence (`scripts/deploy-heroku.sh`) with guardrails. (R)
  1. Capture build logs and tag image digest in `docs/DEPLOYMENTS.md`. (R)
  1. Add GitHub Action (manual trigger) invoking script with fresh build. (R)

### Task T5 — Fix Database Migration Issues for SQLite and Postgres

- **Owner (R/A):** backend / data
- **Target:** 2025-10-20
- **Dependencies:** None
- **Acceptance Criteria:** `alembic upgrade head` succeeds on SQLite dev DB and Postgres staging
- **Status:** Done — 2025-10-18 — added SQLite guards + startup migration runner; `ALEMBIC_DATABASE_URL=sqlite:///tmp_migrations.db alembic -c backend/alembic.ini upgrade head` now passes (backend)
- **Steps:**
  1. Investigate Alembic constraint failures on SQLite (`OperationalError: near "ADD CONSTRAINT"`). (R)
  1. Add batch migrations or conditional logic for SQLite compatibility. (R)
  1. Re-run migrations locally and in staging DB snapshot. (R)

### Task T6 — ChatKit Rollout Validation

- **Owner (R/A):** product / backend
- **Target:** 2025-10-22
- **Dependencies:** Stable auth deployment (Task T1)
- **Acceptance Criteria:** Frontend chat UI connects via ChatKit; Heroku logs show successful token issuance
- **Status:** In Progress — 2025-10-15 — endpoint returns 401 w/o auth; next step add auth header (backend)
- **Steps:**
  1. Validate `/api/chatkit/token` requires auth and returns 200 with valid credentials. (R)
  1. Coordinate frontend ChatKit provider initialization with new endpoint. (S: frontend)
  1. Update docs/env samples with required ChatKit secrets. (R)

### Task T7 — Update Developer Documentation & Tooling

- **Owner (R/A):** docs lead / backend
- **Target:** 2025-10-19
- **Dependencies:** Task T4 script for accuracy
- **Acceptance Criteria:** Docs updated; tooling warnings (isort) resolved in local dev
- **Status:** In Progress — 2025-10-17 — isort installed in .venv; doc updates + README refresh pending (docs)
- **Steps:**
  1. Document new login debug logs and health endpoints in `docs/USAGE_TEMPLATES.md`. (R)
  1. Add isort requirement and confirm editor integration works. (R)
  1. Refresh README deployment section with current Heroku workflow. (R)

### Task T8 — Resolve Production 404s on Flows/Agents APIs

- **Owner (R/A):** backend lead / product
- **Target:** 2025-10-19
- **Dependencies:** Task T1 (auth router restored), Task T4 (deploy path) for rollout
- **Acceptance Criteria:** Authenticated requests return 200 and expected JSON (possibly empty list); logs show successful handler execution; tests cover scenario
- **Status:** To Do — 2025-10-17 — reproducible 404 observed in Heroku logs; investigation queued (backend)
- **Steps:**
  1. Reproduce `/api/flows/runs` and `/api/flows/onboarding/checklist` 404s in staging/prod with authenticated session and capture logs. (R)
  1. Confirm router imports succeed after `_safe_import` logging and inspect request handling for missing tenant/user data. (R)
  1. Decide on UX: return 200 with empty payload vs. hard 404 when user has no runs/agents; implement fix. (R/A)
  1. Add regression tests covering empty datasets and authenticated access paths. (R)

### Task T9 — Align User Profile FK Types with UUID IDs

- **Owner (R/A):** backend / data
- **Target:** 2025-10-18
- **Dependencies:** Task T5 (migration hygiene) for tooling consistency
- **Acceptance Criteria:** `/api/auth/register/step2` succeeds; inserts no longer raise datatype mismatch; schema reflects UUID FK
- **Status:** To Do — 2025-10-17 — production error logged `psycopg.errors.DatatypeMismatch` during signup (backend)
- **Steps:**
  1. Create migration altering `user_profiles.user_id` to `VARCHAR(36)` (or UUID) and reapply FK to `users.id`. (R)
  1. Verify registration step 2 completes locally and in staging after migration. (R)
  1. Backfill/validate existing rows for consistency and note outcome in deployment log. (R)

### Task T10 — Stand Up Analytics Tracking Endpoint

- **Owner (R/A):** backend / product analytics
- **Target:** 2025-10-20
- **Dependencies:** Task T9 (registration flow healthy) to ensure forms emit events without errors
- **Acceptance Criteria:** Network tab shows 201 responses for analytics calls; `analytics_events` table receives new rows; Heroku logs free of 405 errors
- **Status:** To Do — 2025-10-17 — client POSTs currently receive 405 (backend)
- **Steps:**
  1. Implement `/api/auth/analytics/track` handler persisting events with CSRF validation. (R)
  1. Add allow-list for event types and protect against anonymous abuse (rate limit or auth). (R)
  1. Confirm client POSTs return 201 and events stored; document payload contract. (R)

### Task T11 — Enable Google/LinkedIn Social Login (Scaffold Phase)

- **Owner (R/A):** backend / frontend auth
- **Target:** 2025-10-22
- **Dependencies:** Task T12 (email verification) for login guard clarity; Task T7 (docs tooling) for env updates
- **Acceptance Criteria:** Users can sign in via Google or LinkedIn, refresh cookie set, SPA stores tokens, README documents required env vars
- **Status:** In Progress — 2025-10-19 — auth router exposes TODO(M2/M3) stubs and login buttons exist; provider exchange + token issuance pending (backend)
- **Steps:**
  1. Implement `/api/auth/oauth/google/{start,callback}` and `/api/auth/oauth/linkedin/{start,callback}` with code exchange + user upsert. (R)
  1. Persist social credentials/sessions and reuse refresh cookie flow. (R)
  1. Wire SPA login buttons to new start routes and handle verified/not-verified flows. (R)

### Task T12 — Enforce Email Verification for Password Accounts

- **Owner (R/A):** backend / frontend auth
- **Target:** 2025-10-19
- **Dependencies:** Task T5 (migration hygiene) so new migration is stable; Task T7 (docs) for env samples
- **Acceptance Criteria:** Registration sends email via SMTP, `/api/auth/verify?token=...` marks user verified, login for unverified users returns 403 with guidance, resend throttled, SPA displays verification state
- **Status:** Done — 2025-10-19 — migration `202502191200_email_verification` applied; backend routes `/api/auth/verify*` live; React guard + VerifyEmail page shipped (backend/frontend)
- **Steps:**
  1. Add email verification token helper + SMTP mailer, update schema with `email_verified_at` and default `token_version=0`. (R)
  1. Send verification email during registration, add resend route, and protect `/auth/login` until verified. (R)
  1. Provide `/verify-email/:token` SPA route, gated dashboard, and resend UX. (R)

## Communications & Reporting

- Weekly sync every Monday at 10:00 UTC — short triage to move tasks forward (owner: project lead)
- Slack channel `#autorisen-ops` — use for immediate blockers
- Store audit outputs under `artifacts/live-audit/YYYYMMDD/` (or a secure artifact store if large)

## Risks & Mitigations

- Secret drift — mitigate by scripted Heroku deploys (Task T4) and store release notes
- Unintended writes — use dry-run mode in deployment script and require reviewer sign-off
- Auth downtime — add smoke tests in release workflow; monitor `auth.login.*` debug logs after deploy

## Templates

- Status line example: `T1 — Restore auth router — In Progress — 2025-10-16 — notes: rebuild running (ops)`

## Appendix — Useful Commands

```bash
aws iam create-role --role-name gh-oidc-autorisen-ecr \
  --assume-role-policy-document file://infra/aws-ecs-skel/trust-policy.json
```text
## Maintainers

- <ops@example.com>
- <infra@example.com>
- <backend@example.com>
