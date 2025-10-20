# Master Project Plan — autorisen

Snapshot: 2025-10-18

Purpose

- Provide a single, actionable project plan derived from `docs/senior_devops.md` for ops, infra, and product to execute and
  update.
- Make tasks small, assign owners, set target dates, list dependencies, acceptance criteria, and status.

How to use this document

- Owners update their task status inline (To Do / In Progress / Done) and append short notes with date + initials.
- The project lead runs weekly triage against this plan and updates priorities.

Legend

- R: Responsible (executor)
- A: Accountable (decision owner)
- S: Stakeholders / Support
- Dates are target dates (YYYY-MM-DD)

Master milestones (high level)

1. Restore production auth service and publish healthy root/health endpoints (Target: 2025-10-16)
1. Harden Heroku container release workflow with repeatable scripts (Target: 2025-10-18)
1. Stabilize database migrations and local developer setup (Target: 2025-10-20)
1. Finalize ChatKit rollout and analytics instrumentation (Target: 2025-10-22)

Detailed tasks

Task 1 — Restore auth router and redeploy to Heroku

- ID: T1
- Owner (R/A): backend lead / ops
- Target: 2025-10-16
- Steps:
  1. Confirm `backend/src/modules/auth/router.py` matches service-based implementation (no `modules.auth.security`). (R)
  1. Rebuild container with `docker build --no-cache -t autorisen:local .` and push to Heroku registry. (R)
  1. Release to Heroku and smoke test `/` and `/api/health` endpoints. (R)
  1. Document release outcome in `docs/DEPLOYMENTS.md`. (R)
- Dependencies: Heroku CLI authenticated; `HEROKU_API_KEY` exported locally.
- Acceptance criteria: Heroku logs show successful boot, GET `/` returns JSON payload, login route available.
- Status: Done — 2025-10-16 — release v244 deployed; health + auth endpoints verified (ops)

Task 2 — Structured login debug logging rollout

- ID: T2
- Owner (R/A): backend lead
- Target: 2025-10-16
- Steps:
  1. Add contextual debug logs around login flow (attempt, rate-limit, success, failure). (R)
  1. Verify logs in staging/Heroku to aid diagnostics. (R)
- Dependencies: Task 1 deployment.
- Acceptance criteria: Logs visible in Heroku tail with expected `auth.login.*` messages.
- Status: Done — 2025-10-15 — logs present after deployment (backend)

Task 3 — Root health responder for monitoring

- ID: T3
- Owner (R/A): backend
- Target: 2025-10-15
- Steps:
  1. Add FastAPI route for `/` returning service heartbeat JSON. (R)
  1. Confirm 200 response via curl/Heroku logs. (R)
- Dependencies: Task 1 redeploy.
- Acceptance criteria: Heroku router logs show 200 for GET `/` with JSON body.
- Status: Done — 2025-10-15 — verified locally and in logs (backend)

Task 4 — Automate container release workflow

- ID: T4
- Owner (R/A): ops
- Target: 2025-10-18
- Steps:
  1. Script build/tag/push/release sequence (`scripts/deploy-heroku.sh`) with guardrails (R).
  1. Capture build logs and tag image digest in `docs/DEPLOYMENTS.md`. (R)
  1. Add GitHub Action (manual trigger) invoking script with fresh build (R).
- Dependencies: Task 1.
- Acceptance criteria: One-command/manual workflow redeploys latest `main`; logs stored with digest.
- Status: In Progress — 2025-10-17 — `make deploy-heroku` run successfully; script + GH Action outstanding (ops)

Task 5 — Fix database migration issues for SQLite and Postgres

- ID: T5
- Owner (R/A): backend / data
- Target: 2025-10-20
- Steps:
  1. Investigate Alembic constraint failures on SQLite (`OperationalError: near "ADD CONSTRAINT"`). (R)
  1. Add batch migrations or conditional logic for SQLite compatibility. (R)
  1. Re-run migrations locally and in staging DB snapshot. (R)
- Dependencies: None.
- Acceptance criteria: `alembic upgrade head` succeeds on SQLite dev DB and Postgres staging.
- Status: Done — 2025-10-18 — added SQLite guards + startup migration runner; `ALEMBIC_DATABASE_URL=sqlite:///tmp_migrations.db alembic -c backend/alembic.ini upgrade head` now passes (backend)

Task 6 — ChatKit rollout validation

- ID: T6
- Owner (R/A): product / backend
- Target: 2025-10-22
- Steps:
  1. Validate `/api/chatkit/token` requires auth and returns 200 with valid credentials. (R)
  1. Coordinate frontend ChatKit provider initialization with new endpoint. (S: frontend)
  1. Update docs/env samples with required ChatKit secrets. (R)
- Dependencies: Stable auth deployment (Task 1).
- Acceptance criteria: Frontend chat UI connects via ChatKit; Heroku logs show successful token issuance.
- Status: In Progress — 2025-10-15 — endpoint returns 401 w/o auth; next step add auth header (backend)

Task 7 — Update developer documentation & tooling

- ID: T7
- Owner (R/A): docs lead / backend
- Target: 2025-10-19
- Steps:
  1. Document new login debug logs and health endpoints in `docs/USAGE_TEMPLATES.md`. (R)
  1. Add isort requirement and confirm editor integration works. (R)
  1. Refresh README deployment section with current Heroku workflow. (R)
- Dependencies: Task 4 script for accuracy.
- Acceptance criteria: Docs updated; tooling warnings (isort) resolved in local dev.
- Status: In Progress — 2025-10-17 — isort installed in .venv; doc updates + README refresh pending (docs)

Task 8 — Resolve production 404s on flows/agents APIs

- ID: T8
- Owner (R/A): backend lead / product
- Target: 2025-10-19
- Steps:
  1. Reproduce `/api/flows/runs` and `/api/flows/onboarding/checklist` 404s in staging/prod with authenticated session and capture logs. (R)
  1. Confirm router imports succeed after `_safe_import` logging and inspect request handling for missing tenant/user data. (R)
  1. Decide on UX: return 200 with empty payload vs. hard 404 when user has no runs/agents; implement fix. (R/A)
  1. Add regression tests covering empty datasets and authenticated access paths. (R)
- Dependencies: Task 1 (auth router restored), Task 4 (deploy path) for rollout.
- Acceptance criteria: Authenticated requests return 200 and expected JSON (possibly empty list); logs show successful handler execution; tests cover scenario.
- Status: To Do — 2025-10-17 — reproducible 404 observed in Heroku logs; investigation queued (backend)

Task 9 — Align user profile FK types with UUID ids

- ID: T9
- Owner (R/A): backend / data
- Target: 2025-10-18
- Steps:
  1. Create migration altering `user_profiles.user_id` to `VARCHAR(36)` (or UUID) and reapply FK to `users.id`. (R)
  1. Verify registration step 2 completes locally and in staging after migration. (R)
  1. Backfill/validate existing rows for consistency and note outcome in deployment log. (R)
- Dependencies: Task 5 (migration hygiene) for tooling consistency.
- Acceptance criteria: `/api/auth/register/step2` succeeds; inserts no longer raise datatype mismatch; schema reflects UUID FK.
- Status: To Do — 2025-10-17 — production error logged `psycopg.errors.DatatypeMismatch` during signup (backend)

Task 10 — Stand up analytics tracking endpoint

- ID: T10
- Owner (R/A): backend / product analytics
- Target: 2025-10-20
- Steps:
  1. Implement `/api/auth/analytics/track` handler persisting events with CSRF validation. (R)
  1. Add allow-list for event types and protect against anonymous abuse (rate limit or auth). (R)
  1. Confirm client POSTs return 201 and events stored; document payload contract. (R)
- Dependencies: Task 9 (registration flow healthy) to ensure forms emit events without errors.
- Acceptance criteria: Network tab shows 201 responses for analytics calls; `analytics_events` table receives new rows; Heroku logs free of 405 errors.
- Status: To Do — 2025-10-17 — client POSTs currently receive 405 (backend)

Task 11 — Enable Google/LinkedIn social login

- ID: T11
- Owner (R/A): backend / frontend auth
- Target: 2025-10-19
- Steps:
  1. Add `/api/auth/login/google` and `/api/auth/login/linkedin` endpoints, exchanging codes and issuing internal tokens. (R)
  1. Persist social credentials/sessions and reuse refresh cookie flow. (R)
  1. Update SPA login form with reCAPTCHA enforcement, provider buttons, and callback handler. (R)
- Dependencies: Task 5 (migration stability) and Task 7 (docs tooling) for updated environment variables.
- Acceptance criteria: Users can sign in via Google or LinkedIn, refresh cookie set, SPA stores tokens, README documents required env vars.
- Status: Done — 2025-10-18 — endpoints + callback shipped; see backend/src/modules/auth/router.py and client/src/pages/SocialCallback.tsx (backend)

Communications & Reporting

- Weekly sync: every Monday 10:00 UTC — short triage to move tasks forward (owner: project lead).
- Slack channel: #autorisen-ops — use for immediate blockers.
- Artifacts: store audit outputs under `artifacts/live-audit/YYYYMMDD/` (or a secure artifact store if large).

Risks & Mitigations

- Secret drift — mitigate by scripted Heroku deploys (Task 4) and store release notes.
- Unintended writes — use dry-run mode in deployment script and require reviewer sign-off.
- Auth downtime — add smoke tests in release workflow; monitor `auth.login.*` debug logs after deploy.

Templates (for updating tasks)

- Status line example: `T1 — Restore auth router — In Progress — 2025-10-16 — notes: rebuild running (ops)`

Appendix — Useful commands

- Create role (example):

```bash
aws iam create-role --role-name gh-oidc-autorisen-ecr \
  --assume-role-policy-document file://infra/aws-ecs-skel/trust-policy.json
```

Maintainers: <ops@example.com>, <infra@example.com>, <backend@example.com>
