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

Required:
- Connection health checks
- Basic query error logging
- Backup/restore procedure documented
- Simple DB reset procedure for local dev

Optional (post-MVP):
- Advanced metrics, query profiling, partitioning, read replicas

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

- What the system guarantees
- What the system explicitly does NOT guarantee

### 3.4 Frozen vs Flexible Areas

- Frozen: (to be defined)
- Flexible: (to be defined)

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

- Time
- Email
- Rate-limiting

### 5.2 Test Environment Guarantees

- What “green CI” means
- What tests may mock
- What tests must not mock

---

## 6. Operational Guardrails

### 6.1 Development Rules

- Branching strategy
- Merge rules
- Commit discipline

### 6.2 Deployment Rules

- When deploys are allowed
- Required approvals
- Rollback expectations

### 6.3 Migration Rules

- When migrations are allowed
- Approval requirements

---

## 7. Roadmap & Unlock Criteria

### 7.1 Frozen Milestones

- Auth stability
- Security policy locked

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

- Who may edit
- Review process
- Versioning

### 8.2 Authority

In the event of conflict:
- This document overrides playbooks and plans.

---
