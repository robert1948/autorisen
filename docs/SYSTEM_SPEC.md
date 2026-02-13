# CapeControl — System Specification

> Status: DRAFT  
> Last updated: 2026-01-06  
> Owners: CapeControl Management Team  
> Scope: MVP → First Production Release

---

## 1. Purpose & Scope

### 1.1 Purpose

Define the authoritative intent, boundaries, and guardrails for the CapeControl system.
This document is the single source of truth from which:
- Project plans
- Playbooks
- VS_Chat instructions
- Codex execution tasks  
are derived.

### 1.2 In Scope

- Authentication and session management
- Security policies (CSRF, cookies, headers)
- Payment intent and constraints
- Testing and CI guarantees
- Operational and deployment guardrails

### 1.3 Out of Scope

- UI/UX design details
- Performance optimization beyond MVP needs
- Multi-tenant scaling
- Payment provider changes outside approved scope

---

## 2. System Boundaries

### 2.1 Frontend Responsibilities

- User interaction and form submission
- Attaching required auth and CSRF headers
- Handling auth state transitions
- No direct payment logic

### 2.2 Backend Responsibilities

- Auth enforcement
- Session lifecycle
- Security validation
- Payment orchestration (server-side only)

### 2.3 External Dependencies

- Email provider
- Payment provider (PayFast)
- Hosting and CI infrastructure

### 2.4 Explicitly Blocked Work

- NEXT-003 (PayFast implementation) — **ON HOLD**
- Reason for block:
  - Pending specification approval
  - Security and flow invariants not yet frozen

---

## 2.5 MVP Pages & Navigation (Authoritative)

This section defines the complete set of pages required for the CapeControl MVP.
Pages listed here are considered **in scope** for MVP delivery.
Any page not listed here is **out of scope** unless explicitly approved.

---

### 2.5.1 Public Pages (Unauthenticated)

Purpose: Entry, trust-building, and access to authentication.

- `/` — Landing
- `/about`
- `/docs`
- `/login`
- `/register`
- `/reset-password`
- `/reset-password/confirm`

Notes:
- No authenticated data
- No payment actions
- Minimal logic

---

### 2.5.2 Authentication Flow Pages

Purpose: Secure account access and session establishment.

- `/register/step-1`
- `/register/step-2`
- `/verify-email/:token`
- `/logout` (action, not full page)

Notes:
- Must comply with Auth & CSRF policy
- No onboarding logic here

---

### 2.5.3 Onboarding Pages (Post-Auth, Pre-App)

Purpose: Profile completion and guided activation.

- `/onboarding/welcome`
- `/onboarding/profile`
- `/onboarding/checklist`
- `/onboarding/guide`

Notes:
- Accessible only after successful authentication
- Completion gates access to App pages

---

### 2.5.4 App Pages (Authenticated Core)

Purpose: Primary product interaction.

- `/dashboard`
- `/settings`
  - `/settings/profile`
  - `/settings/security`
  - `/settings/billing` (UI only; no payment execution until NEXT-003 unblocked)

Notes:
- Requires active session
- Billing page is **display-only** for MVP

---

### 2.5.5 Help & Support Pages

Purpose: Self-service assistance.

- `/help`
- `/help/knowledge-base`

Notes:
- Read-only
- No ticketing or chat in MVP

---

### 2.5.6 Explicitly Out of Scope (MVP)

- Admin console
- Multi-tenant org management
- Advanced analytics
- In-app payments execution
- Notifications center

---

### 2.5.7 Navigation Rules

- Public → Auth → Onboarding → App is strictly linear
- Users may not skip onboarding
- Logout returns user to `/login`

Onboarding gate expectations (normative):
- Users who have not completed onboarding MUST be routed to onboarding pages before any App pages.
- Direct navigation to App routes MUST redirect to the next required onboarding step.
- Onboarding completion is the only condition that unlocks App pages (no bypasses for MVP).
- The gate applies to all App routes, including deep links (e.g., `/settings/*`).

---

## 2.6 Data & PostgreSQL (Authoritative)

CapeControl uses PostgreSQL as the system-of-record for MVP data.
This section defines MVP database scope, ownership, and operational rules.

---

### 2.6.1 MVP Data Responsibilities

PostgreSQL must store:
- User identities and authentication-related records
- Onboarding progress and profile data
- Settings data (profile/security; billing display-only)
- Audit/security-relevant events (minimal)

PostgreSQL must NOT store:
- Secrets in plaintext (tokens, passwords, provider keys)
- Large blobs/media files (use object storage if needed later)
- High-volume analytics/events beyond MVP needs

---

### 2.6.2 MVP Core Tables (Conceptual)

Minimum conceptual entities (final schema may vary):
- `users`
- `sessions` or `refresh_tokens` (depending on implementation)
- `csrf_tokens` (only if persisted; otherwise cookie-based only)
- `onboarding_profiles`
- `onboarding_checklist_items` (or a single progress record)
- `user_settings`
- `audit_events` (minimal, append-only)

---

### 2.6.3 Migration & Schema Management

- All schema changes are managed via migrations (Alembic).
- Migrations are reviewed and committed to version control.
- No manual schema edits in production.

Rules:
- No migrations are run without explicit approval (management gate).
- Deploy and migrate are separate steps (never implicit).
- Every migration must be reversible where feasible (downgrade guidance).

#### Migration Rules (SPEC-009)

1. No implicit migrations
   - The app must not auto-run schema migrations on startup by default.
   - CI/CD must not run migrations implicitly as part of deploy.

2. Explicit approvals required
   - Any schema change requires an explicit approval step (PR review plus documented go/no-go).
   - Migration execution must be a conscious action (manual command), not a side-effect.

3. Environment boundary
   - autorisen (staging): migrations allowed with evidence pack and verification.
   - capecraft (production): forbidden unless Robert explicitly instructs and approvals are recorded.

4. Minimum migration PR requirements
   - Alembic revision (or migration script) included and reviewed.
   - Rollback plan documented (downgrade path or recovery approach).
   - Verification commands included (examples: `alembic heads`, `alembic history`, `alembic current`, SQL checks).
   - Evidence artifacts captured under `docs/evidence/<WO_ID>/logs/`.

5. Execution guard
   - Migrations must require an explicit flag or guard (example policy language):
     "Only run migrations when `ALLOW_MIGRATIONS=1` (or equivalent) is present, and only in staging unless explicitly approved."

---

### 2.6.4 Environments

Local/dev:
- Docker Compose PostgreSQL
- Safe dev credentials
- Seed data allowed

Test:
- Isolated database (or transactional strategy)
- Deterministic fixtures
- No external email/payment calls

Production:
- Managed Postgres (Heroku)
- Backups enabled
- Least-privileged DB user
- Secure connection required

---

### 2.6.5 Observability & Maintenance (MVP)

#### Connection Health Checks

The application exposes three health endpoints:

| Endpoint | DB query? | Purpose |
|---|---|---|
| `GET /api/health` | **Yes** (`SELECT 1`) | Full health with DB connectivity check |
| `GET /api/health/alive` | No | Liveness probe (container is running) |
| `GET /api/health/ping` | No | Lightweight readiness probe |

`/api/health` opens a `SessionLocal` session, executes `SELECT 1`, and reports
`"database_connected": true/false`. On failure it returns `"status": "degraded"`
and logs the exception. This endpoint is used by:
- Heroku Dockerfile `HEALTHCHECK` instruction
- Post-deploy smoke tests (`make smoke-staging`, `make smoke-prod`)
- CI Docker build tests (`ci-test.yml`)
- Deployment verification (`deploy-staging.yml`, `deploy-heroku.yml`)

#### Connection Pool Configuration

| Setting | Env Var | Default | Notes |
|---|---|---|---|
| `pool_pre_ping` | — | `True` | Validates connections before use |
| `pool_size` | `DB_POOL_SIZE` | `5` | Conservative for single-dyno Heroku |
| `max_overflow` | `DB_MAX_OVERFLOW` | `5` | Max 10 concurrent connections |
| `pool_recycle` | `DB_POOL_RECYCLE` | `1800` | 30-minute recycle to avoid stale connections |
| SSL mode | `DATABASE_SSL` | Auto-detect | Enabled for `amazonaws.com` or `heroku` URLs |

Pool monitoring (event listeners, metrics export) is **not implemented** in MVP.

#### Query Error Logging

- SQLAlchemy query-level logging (`echo=True`) is not enabled by default.
- Database connection failures are caught and logged in the `/api/health` handler.
- SQL errors during request handling are propagated as HTTP 500 responses with
  structured error logging via the middleware stack.
- Slow query detection is **not implemented** in MVP.

#### Backup & Restore

- **Heroku Postgres**: Automatic daily backups are provided by the Heroku Managed
  Postgres plan. No additional backup automation exists in the repository.
- **Backup verification**: Not automated. Verify via `heroku pg:backups -a <app>`.
- **Restore**: Use `heroku pg:backups:restore` for point-in-time recovery.
- **Local backups**: Not applicable — local dev uses disposable Docker volumes.

Backup verification targets (`heroku pg:info`, `heroku pg:diagnose`) are **not yet
added** to the Makefile. This is a known gap.

#### Local Database Reset

No dedicated `db-reset` Makefile target exists. The manual procedure is:

```bash
# 1. Destroy the Docker volume (removes all local data)
docker compose down -v

# 2. Restart Postgres
docker compose up -d db
sleep 3

# 3. Run migrations to recreate schema
make migrate-up
# Or: ALEMBIC_DATABASE_URL="postgresql://devuser:devpass@localhost:5433/devdb" \
#     alembic -c backend/alembic.ini upgrade head
```

Local Postgres runs on port `5433` (not default `5432`) with credentials
`devuser` / `devpass` / `devdb`. pgAdmin is available on port `5050` via the
`tools` profile: `docker compose --profile tools up -d`.

No seed data scripts exist. Fresh local databases start empty after migrations.

#### Heroku Database Operations

| Operation | Command |
|---|---|
| Check migration version | `heroku pg:psql -a <app> -c "SELECT version_num FROM alembic_version"` |
| Run migrations | `make heroku-run-migrate HEROKU_APP_NAME=<app>` |
| Interactive shell | `make heroku-shell` |
| View DB info | `heroku pg:info -a <app>` |
| View connection stats | `heroku pg:diagnose -a <app>` |
| View backups | `heroku pg:backups -a <app>` |

Only the first three are currently wired into Makefile targets.

#### Post-MVP (Not Implemented)

- Advanced connection pool monitoring (SQLAlchemy pool events, metrics export)
- Slow query detection and logging
- Query profiling
- Automated backup verification
- Database partitioning
- Read replicas

---

### 2.6.6 Explicitly Out of Scope (MVP)

- Multi-tenant row-level security and complex tenant sharding
- Event sourcing / CQRS
- Data warehouse / BI pipeline
- Full audit/compliance program beyond minimal audit log

---

## 3. Authentication & Security Model

### 3.1 Auth Flows

All auth endpoints are served under `/api/auth`. Non-GET endpoints require a
CSRF header+cookie pair (see §3.2).

Login
- Endpoint: `POST /api/auth/login`
- Request JSON: `{ "email": "...", "password": "...", "recaptcha_token"?: "..." }`
- Success `200`:
   - Response JSON: `{ "access_token": "...", "refresh_token": "...", "token_type": "bearer", "email_verified": true }`
   - Sets `refresh_token` cookie (HttpOnly, path `/api/auth`, `SameSite` and
      `Secure` per settings; `Max-Age`/`Expires` derived from access TTL)
- Failure:
   - `401` invalid credentials
   - `403` email not verified
   - `429` rate-limited (Retry-After header)

Token refresh
- Endpoint: `POST /api/auth/refresh`
- Request: accepts refresh token from JSON body `{ "refresh_token": "..." }`
   or from `refresh_token` cookie
- Success `200`:
   - Response JSON: `{ "access_token": "...", "refresh_token": "...", "expires_at": "..." }`
   - Rotates refresh token (new token stored; cookie updated)
- Failure: `401` invalid refresh token

Current user
- Endpoint: `GET /api/auth/me`
- Auth: `Authorization: Bearer <access_token>`
- Success `200`: `MeResponse` with role, profile, and summary

Logout
- Endpoint: `POST /api/auth/logout`
- Request JSON (optional): `{ "all_devices": false }`
- Behavior:
   - Clears `refresh_token` cookie
   - Revokes refresh token if present
   - If `all_devices=true`, increments user token version (invalidates tokens)
- Response:
   - `200` with `{ "message": "Logged out" }` when token is present
   - `204` when no token is provided

CSRF bootstrap
- Endpoint: `GET /api/auth/csrf`
- Response JSON: `{ "csrf": "...", "csrf_token": "...", "token": "..." }`
- Sets `csrftoken` cookie (not HttpOnly) and mirrors the token in response header
   `X-CSRF-Token`

### 3.2 CSRF Policy

- Canonical policy: [SECURITY_CSRF.md](SECURITY_CSRF.md)
- Token source: `GET /api/auth/csrf` returns JSON keys `csrf`, `csrf_token`, `token`,
   sets `csrftoken` cookie (Path `/`, not HttpOnly) and mirrors `X-CSRF-Token`.
- Cookie/header requirements: requests MUST include matching CSRF cookie + header.
   Header accepted: `X-CSRF-Token` (preferred), `X-CSRFToken`, `X-XSRF-TOKEN`.
   Cookie accepted: `csrftoken` (preferred), `csrf_token`, `XSRF-TOKEN`.
- Protected scope: all non-safe methods (`POST`, `PUT`, `PATCH`, `DELETE`) across
   the API, except explicit exemptions:
   `POST /api/payments/payfast/checkout`, `POST /api/payments/payfast/itn`.

### 3.3 Session Guarantees

#### 3.3.1 What the system guarantees

Token lifecycle:
- Access tokens are stateless JWTs (HS256), signed with `SECRET_KEY`.
- Refresh tokens are opaque (48 random bytes, base64url-encoded), stored server-side
  as SHA-256 hashes in the `sessions` table.
- CSRF tokens are signed (`nonce.timestamp.HMAC-SHA256`), validated statelessly.

Token lifetimes:
- Access token: 7 days (`ACCESS_TOKEN_TTL_MINUTES`, default 10,080).
- Refresh token: 7 days (`REFRESH_TOKEN_EXPIRE_DAYS`, default 7).
- CSRF token: 1 hour (hardcoded).
- Password reset token: 30 minutes (`PASSWORD_RESET_TTL_MINUTES`).
- Temporary registration token: 15 minutes (`TEMP_TOKEN_TTL_MINUTES`).

Refresh behavior:
- Refresh rotates both access and refresh tokens (single-use rotation).
- The old refresh token is implicitly invalidated (hash replaced in the session row).
- The session row's `expires_at` is extended on each successful refresh.

Logout:
- Single-device logout clears the refresh cookie, revokes the session row
  (`revoked_at` set), and adds the access token's JTI to a deny list.
- All-devices logout additionally increments `users.token_version`, which invalidates
  all existing access JWTs for that user on their next API call.

Persistence:
- Refresh sessions (`sessions` table) survive server restarts.
- `token_version` is authoritative in the database; cache misses fall back to DB.
- CSRF tokens are stateless and survive restarts (no server state required).
- Access JWTs are stateless and survive restarts (validated by signature + expiry).

Server-side session state:
- Each login creates a row in `sessions` with: `user_id`, `token_hash`, `user_agent`,
  `ip_address`, `created_at`, `expires_at`, `revoked_at`.
- This is a per-device session model.

#### 3.3.2 What the system explicitly does NOT guarantee

- **Immediate revocation of access tokens without Redis.** The JTI deny list uses
  Redis when available; the in-memory fallback is lost on server restart. A revoked
  access token may be usable until its natural expiry if Redis is unavailable.
- **Refresh token replay detection.** If a rotated-out refresh token is reused, it
  simply fails lookup. There is no breach alerting or session-family revocation.
- **Per-user session limits.** Users may have unlimited concurrent sessions/devices.
- **Expired session cleanup.** Stale `sessions` rows are not reaped automatically;
  they are rejected at refresh time but remain in the table.
- **Cross-device logout propagation for single-device logout.** Only the current
  device's tokens are affected. Other devices continue until their tokens expire.
- **All-devices logout does not individually revoke session rows.** It relies on
  `token_version` mismatch to reject future access tokens from other sessions.
- **Sliding expiry on access tokens.** Access tokens expire at the fixed time set
  at creation; activity does not extend their lifetime.
- **CSRF token auto-refresh.** CSRF tokens expire after 1 hour. Clients must
  periodically call `GET /api/auth/csrf` to obtain fresh tokens for mutations.
  The CSRF TTL is shorter than the access token TTL.

### 3.4 Frozen vs Flexible Areas

This section defines what is locked for MVP stability and what may evolve.
See also: FREEZE_REVIEW.md for the full management assessment.

#### Frozen (no changes without PLAYBOOK_AUTH_CHANGES.md procedure)

- **Auth endpoint contracts** — Request/response shapes, status codes, and endpoint
  paths for login, refresh, logout, me, and csrf (§3.1).
- **CSRF double-submit pattern** — Cookie name (`csrftoken`), header name
  (`X-CSRF-Token`), validation rules, and exemption list (§3.2, SECURITY_CSRF.md).
- **Refresh token rotation model** — Single-use opaque tokens stored as SHA-256
  hashes in the `sessions` table (§3.3.1).
- **Cookie attributes** — `refresh_token` (HttpOnly, path `/api/auth`), `csrftoken`
  (not HttpOnly, path `/`). SameSite/Secure per environment settings.
- **Token signing** — HS256 with `SECRET_KEY`. Algorithm and key material must not
  change without a dedicated security review work order.
- **`token_version` revocation model** — All-devices logout increments
  `users.token_version` to invalidate outstanding access JWTs.

#### Flexible (may evolve within guardrails)

- **Token TTL values** — Access, refresh, CSRF, and temporary token lifetimes may
  be tuned via environment variables without changing the auth model.
- **Rate limiting thresholds** — Login attempt limits and lockout durations may be
  adjusted without changing the auth flow.
- **Deny list backend** — May switch between Redis and in-memory without changing
  the auth contract (Redis is recommended for production).
- **Session table cleanup** — A reaper for expired session rows may be added without
  changing the auth flow.
- **OAuth provider configuration** — Google/LinkedIn OAuth scopes and callback handling
  may be refined without changing the core JWT/CSRF model.
- **Error message wording** — Auth error response text may be improved for clarity
  without changing status codes or response structure.

---

## 4. Payments — Intent Only (No Implementation)

### 4.1 Payment Philosophy

- Payments are explicit, user-initiated actions
- No implicit billing
- No background or silent charges

### 4.2 Payment Triggers

- What actions may initiate a payment
- Preconditions for payment eligibility

### 4.3 PayFast Constraints

- What PayFast is allowed to do
- What PayFast must never do

### 4.4 NEXT-003 Preconditions

NEXT-003 may only resume when:
- This specification is approved
- Auth and CSRF sections are frozen
- Explicit management approval is recorded

---

## 5. Testing Strategy

### 5.1 Determinism Requirements

Tests must be deterministic: identical inputs produce identical results regardless
of environment, time of day, or external service availability.

Time:
- Rate limiter `_now()` is frozen to a constant epoch (`1_700_000_000.0`) via the
  `_auth_rate_limiter_determinism` autouse fixture.
- No `freezegun` or `freeze_time` is used. Tests must not depend on wall-clock time.
- If time-dependent behavior is tested in the future, a deterministic time source
  must be injected (mock or fixture), never `datetime.now()` or `time.time()` directly.

Email:
- `smtplib.SMTP` is monkeypatched with `_DummySMTP` via the `_email_sink` autouse fixture.
  All sent email is captured in `app.state.test_emails` / `app.state.mailbox` / `app.state.outbox`.
- The `mailer_core` module appends to `TEST_OUTBOX` when `settings.env == "test"` instead
  of sending via SMTP.
- No real SMTP connection is ever made during tests.

Rate-limiting:
- Rate limiter state (`_attempts`, `_blocks`) is cleared before each test via autouse fixture.
- `RATE_LIMIT_BACKEND=memory` and `DISABLE_RATE_LIMIT=1` are set in test environment.
- Tests that verify rate-limit behavior must use the deterministic in-memory backend.

External services:
- `DISABLE_RECAPTCHA=true` in test environment — no external captcha calls.
- OpenAI is mocked via `mock_openai` fixture (returns `AsyncMock` with canned responses).
- No external HTTP calls are permitted in tests. Any integration requiring an external
  service must use a mock or stub.

Database:
- Tests use disposable SQLite at `/tmp/autolocal_test.db`.
- The database is dropped and recreated at session start via `_prepare_test_db` fixture.
- `RUN_DB_MIGRATIONS_ON_STARTUP=0` — schema is created via `Base.metadata.create_all`,
  not Alembic migrations.

### 5.2 Test Environment Guarantees

#### What "green CI" means

A passing CI run confirms:
- Backend tests pass (`pytest tests/ -q`).
- Python linting passes (`ruff check`, `ruff format --check`).
- Frontend linting, type-checking, and production build succeed.
- Docker image builds and `/api/health` responds (on PRs).
- Documentation lint passes.
- Security scan completes (Trivy filesystem scan).

A passing CI run does NOT confirm:
- Production database compatibility (tests use SQLite, not PostgreSQL).
- Alembic migration correctness (migrations are not run in tests).
- Frontend E2E behavior (Playwright tests exist but are not required to pass).
- MyPy type-checking strictness (allowed to fail with `|| true`).

#### What tests may mock

- SMTP / email delivery (`_DummySMTP` fixture).
- Rate limiter time source (`_now()` frozen to constant).
- Rate limiter state (cleared per test).
- OpenAI / LLM API calls (`mock_openai` fixture).
- reCAPTCHA validation (disabled via `DISABLE_RECAPTCHA`).

#### What tests must NOT mock

- Auth endpoint behavior — tests must call real `/api/auth/*` endpoints.
- CSRF validation — tests must obtain and use real CSRF tokens.
- Database operations — tests must use real ORM operations against SQLite.
- JWT signing and validation — tests must use real `python-jose` with test secret key.

---

## 6. Operational Guardrails

### 6.1 Development Rules

#### Branching strategy

| Purpose | Branch prefix | Example |
|---------|---------------|--------|
| Work orders | `wo/` | `wo/spec-005` |
| Features | `feature/` | `feature/marketplace-agent` |
| Bug fixes | `fix/` | `fix/csrf-cookie-domain` |
| Chores | `chore/` | `chore/dep-update` |
| Integration | `develop` | — |
| Staging | `staging` | — |
| Production | `main` | — |

All feature branches are created from `main` (or `origin/main`) unless the work
order explicitly specifies otherwise.

#### Merge rules

- All merges to `main` require a pull request.
- PRs must use the structured PR template (`.github/pull_request_template.md`):
  title, related issues, changes, testing performed, deployment notes, checklist.
- At least one approval is recommended; owner (`robert1948`) may self-merge when
  sole contributor.
- Squash-merge is the default merge strategy.
- Force-pushes to `main` and `develop` are prohibited.

#### Commit discipline

- Commit messages should be imperative present tense ("Add", "Fix", "Update").
- Reference work order ID or issue number where applicable.
- Codex guard (`.github/workflows/codex-guard.yml`) runs pre-commit validation
  on `wo/**` branches.

### 6.2 Deployment Rules

#### When deploys are allowed

| Target | Trigger | Workflow |
|--------|---------|----------|
| Staging (`autorisen`) | Push to `develop` or `staging` | `deploy-staging.yml` |
| Production (`capecraft`) | Push to `main` | `deploy-heroku.yml` |
| Docker Hub | Push to `main` | Included in `deploy-heroku.yml` |

Manual deployment is available via `make deploy-heroku` with retry logic (3 attempts).

#### Required approvals

- Staging: No approval required; CI must pass.
- Production: CI must pass and PR must be merged to `main`.
- Production (capecraft): Requires `ALLOW_PROD=1` environment variable to confirm intent.

#### Deployment pipeline

1. CI tests run (backend, frontend, Docker build, security scan).
2. Docker image built (`docker build -t autorisen:local .`).
3. Image pushed to Heroku Container Registry.
4. `heroku container:release web` executes.
5. Release phase: `bash scripts/release.sh` — migrations are **disabled** by policy
   (`RUN_DB_MIGRATIONS_ON_STARTUP=0`); script runs health check only.
6. Post-deploy smoke: `/api/health` and `/api/auth/csrf` verified.
7. On staging: explicit migration via `make heroku-run-migrate` if needed.

#### Rollback expectations

- Rollback is via `heroku rollback` or by reverting the merge commit and re-deploying.
- Database rollbacks require manual Alembic downgrade — see `PLAYBOOK_DB_MIGRATIONS.md`.
- There is no automated rollback trigger; human judgment is required.

### 6.3 Migration Rules

Migration policy is defined authoritatively in **§2.6.3** (SPEC-009). This section
summarizes the operational guard rails.

#### When migrations are allowed

- **Local / test**: Any time; SQLite is disposable.
- **Staging**: After staging deploy, via `make heroku-run-migrate`. Must be verified
  before merging to `main`.
- **Production**: Only after explicit approval and evidence that the migration ran
  cleanly on staging. Execute via `make heroku-run-migrate`.

#### Approval requirements

- Migrations must be in a dedicated PR (or clearly separated in a mixed PR).
- PR description must include the Alembic revision chain and expected DDL.
- The `PLAYBOOK_DB_MIGRATIONS.md` playbook must be followed.
- `RUN_DB_MIGRATIONS_ON_STARTUP` must remain `0` in production — migrations
  are never auto-applied in the release phase.

---

## 7. Roadmap & Unlock Criteria

### 7.1 Frozen Milestones

- **Auth stability**: JWT + CSRF + refresh token architecture is frozen per §3.
  No structural changes without GOV-001 playbook procedure.
- **Security policy locked**: Rate limiting, CSRF, input sanitization, and DDoS
  protection configuration is frozen. Changes require security review.

### 7.2 Roadmap Unlock Criteria (Normative)

This section defines the **objective criteria** that MUST be met to “unlock” the next roadmap stage. Unlocks are designed to prevent scope drift and ensure that each stage is **stable, auditable, and supportable** before progressing.

#### 7.2.1 Global prerequisites (apply to every unlock)
An unlock MUST NOT be granted unless all of the following are true:

1. **Plan + traceability**
   - The work is represented in the SSOT plan (project-plan.csv) and is not marked **blocked** or **done**.
   - The change is linked to a single Work Order / plan item, and the PR description includes verification evidence.

2. **No P0/P1 unresolved**
   - There are no known unresolved P0/P1 issues affecting user access, data integrity, authentication, or safety controls.

3. **Security baseline is intact**
   - Authentication flows behave as specified (login/refresh/logout/me as applicable).
   - CSRF/session protections remain consistent with the security policy already defined in this spec.

4. **Observability + version trace**
   - The running system exposes a reliable build identifier (e.g., `/api/version` or equivalent) and the UI displays it where required (e.g., footer).
   - Logs/monitoring are sufficient to diagnose user-impacting errors (minimum viable observability).

5. **Rollback/containment is defined**
   - There is a clear rollback path for the release (container rollback/release rollback procedure), and it is feasible without data migrations.

#### 7.2.2 Stage gates
Roadmap progression is unlocked only when the current stage gate is satisfied.

**Stage A — Internal Release Candidate (autorisen/staging)**
- Core journeys work end-to-end on staging:
  - Public pages load reliably (no broken routes).
  - Auth journey functions (register/login/logout/refresh/me as applicable).
  - Onboarding flow is coherent and does not dead-end.
- A smoke-check is documented in the PR evidence (manual checks are acceptable during docs-only work; implementation WOs MUST include commands/screens).
- A stability window is observed on staging (no repeatable P0/P1 regressions after deployment).

**Stage B — Private Beta**
- Access is controlled (invite-only or equivalent) and support contact/triage path is defined.
- The top friction points from early testers are captured and are addressable without redesigning the system architecture.
- Support load is within capacity, and issues are not repeatedly re-opened due to missing observability.

**Stage C — Public Soft Launch**
- The product can be used by the public without direct operator intervention for normal flows.
- Support load remains manageable and does not compromise system stability.
- Trust basics are present (clear user messaging, stable navigation, and no “surprise” behavior).

**Stage D — General Availability**
- The system is operationally supportable with defined incident severity handling (P0–P2) and a viable rollback plan.
- Monitoring is sufficient to detect and respond to user-impacting failures quickly.
- The MVP promise is consistently delivered under expected usage without frequent P0/P1 incidents.

#### 7.2.3 Unlock discipline
- Unlock criteria are **necessary conditions**. Meeting them authorizes progression; it does not force it.
- If an unlock would introduce new scope, migrations, or production release requirements, it MUST be handled under a separate approved Work Order and gate review.

---

## 8. Change Control

### 8.1 How This Spec Is Updated

#### Who may edit

- Repository owner (`robert1948`) has final authority over all sections.
- AI agents (Copilot, Codex) may propose spec changes via PRs on `wo/` branches;
  all proposals require human review before merge.
- No `CODEOWNERS` file is currently configured; branch protection is managed
  via GitHub repository settings.

#### Review process

1. Spec changes must be submitted as a pull request using the structured PR template.
2. The PR must identify which sections are modified and whether they are
   **frozen**, **flexible**, or **deferred** (see §3.4).
3. Changes to **frozen** sections require explicit justification and must follow
   the applicable playbook (e.g., `PLAYBOOK_AUTH_CHANGES.md` for §3).
4. Changes to **flexible** sections may proceed with standard PR review.
5. The `FREEZE_REVIEW.md` must be updated when frozen-section changes are merged.

#### Versioning

- The spec version tracks the application version in `VERSION` (currently v0.2.10).
- Substantive changes increment the document revision noted in the spec header.
- The revision history is maintained via git log; no in-document changelog is required.
- `project-plan.csv` is updated to record which work order modified which section.

### 8.2 Authority

In the event of conflict:
- This document overrides playbooks and plans.

---
