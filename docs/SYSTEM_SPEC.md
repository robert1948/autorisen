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

**Purpose:** Define the MVP authentication contract and session behavior for Auth v1.

**Diagram references:**
- Source: `docs/diagrams/src/auth-workflow.mup`
- Export: `docs/diagrams/export/auth-workflow.pdf`

#### 3.1.1 Error Shape (canonical)
All auth endpoints SHOULD use a single error shape:

```json
{
   "error": {
      "code": "STRING",
      "message": "STRING",
      "fields": { "field": "message" }
   }
}
```

#### 3.1.2 Endpoint Contracts (MVP)

**POST `/api/auth/register`** (single-step registration)
- **Request JSON**
   - `first_name` (string, required)
   - `last_name` (string, required)
   - `email` (string, required, email format)
   - `password` (string, required)
   - `confirm_password` (string, required, must match)
   - `role` (string, optional; default `Customer`)
   - `company_name` (string, optional)
   - `profile` (object, optional)
   - `recaptcha_token` (string, optional; required when reCAPTCHA enabled)
- **Validation**
   - Email format enforced.
   - Password policy (see §3.1.6).
- **Success**
   - `201 Created`
   - Response JSON: `{ "access_token": "...", "refresh_token": "...", "token_type": "bearer", "email_verified": true }`
   - Also sets `refresh_token` httpOnly cookie.
- **Failures**
   - `400` validation error
   - `409` account already exists
   - `429` rate limited

**POST `/api/auth/login`**
- **Request JSON**
   - `email` (string, required, email format)
   - `password` (string, required)
   - `recaptcha_token` (string, optional; required when reCAPTCHA enabled)
- **Success**
   - `200 OK`
   - Response JSON: `{ "access_token": "...", "refresh_token": "...", "token_type": "bearer", "email_verified": true }`
   - Also sets `refresh_token` httpOnly cookie.
- **Failures**
   - `401` invalid credentials (generic message)
   - `403` email not verified
   - `429` rate limited (`Retry-After` header)

**Notes:** The backend also supports a two-step registration flow:
`POST /api/auth/register/step1` → `POST /api/auth/register/step2` (temp token + profile). This spec treats `/api/auth/register` as the canonical MVP contract.

#### 3.1.3 Session / Token Model (MVP)
- **Access token**: JWT; TTL configurable via `ACCESS_TOKEN_TTL_MINUTES` (current default 7 days).
- **Refresh token**: opaque token stored server-side and rotated; returned in JSON and set as `refresh_token` cookie.
- **Cookie settings**: `HttpOnly`, `SameSite={lax|strict|none}`, `Secure` auto-enabled when `SameSite=None`, `Path=/api/auth`.
- **Storage (frontend)**: access token stored in local storage; refresh token stored in local storage (fallback) and via httpOnly cookie.
   Security note: storing refresh tokens in localStorage is discouraged; prefer the httpOnly cookie as the primary mechanism.
- **Refresh**: `POST /api/auth/refresh` returns new tokens and rotates refresh cookie.
- **Logout**: `POST /api/auth/logout` clears refresh cookie and invalidates server-side refresh token.
- **Authorization**: `Authorization: Bearer <access_token>` on protected endpoints.

#### 3.1.4 Account Status Rules
- **active**: `is_active=true` and `email_verified=true` → login allowed.
- **pending_verification**: `email_verified=false` → login denied with `403`.
- **disabled**: `is_active=false` → login denied with `401` (generic invalid credentials).

#### 3.1.5 Rate Limiting / Lockout (Measurable)
- **Per-IP+email login gate** (in-memory):
   - Max attempts: `AUTH_LOGIN_MAX_ATTEMPTS` (default 5)
   - Window: `AUTH_LOGIN_WINDOW_SEC` (default 300s)
   - Block: `AUTH_LOGIN_BLOCK_SEC` (default 300s)
   - Response: `429` with `Retry-After`
- **Global rate limit**: `RATE_LIMIT_PER_MIN` (default 10/min) applied via auth rate limiter.
- **Audit events**: login attempt, login success, lockout (see login audit model).

#### 3.1.6 Password Policy + UX Rules
- **Minimum**: 12 characters; must include uppercase, lowercase, digit, and special character.
- **Register UX**: field-level errors allowed.
- **Login UX**: generic error only (avoid account enumeration).
- **Show/Hide password**: allowed for UX.

#### 3.1.7 Mismatch / Follow-up WO
- **Error shape**: current implementation returns `{ "detail": "..." }` from FastAPI errors. Align to the canonical error envelope in a follow-up WO.
- **CSRF on refresh**: SECURITY_CSRF.md requires CSRF for `POST /api/auth/refresh`, but the current endpoint does not enforce it. Align in a follow-up WO.

### 3.2 CSRF Policy

Canonical reference: [SECURITY_CSRF.md](SECURITY_CSRF.md)

**Token source**
- `GET /api/auth/csrf` returns JSON with `csrf`, `csrf_token`, and `token`.
- Sets cookie `csrftoken` (readable, not HttpOnly) and mirrors into `X-CSRF-Token` response header.

**Cookie names accepted**
- `csrftoken` (preferred)
- `csrf_token`

**Required headers**
- `X-CSRF-Token` (preferred) or `X-CSRFToken`

**Protected endpoints**
- All non-safe methods: `POST`, `PUT`, `PATCH`, `DELETE`.
- Auth endpoints requiring CSRF include: `/api/auth/login`, `/api/auth/register`, `/api/auth/logout` (see mismatch note for refresh).

### 3.3 Session Guarantees

**Guarantees**
- Auth endpoints return access + refresh tokens on success.
- Refresh token cookie is set with HttpOnly and SameSite policy.
- Access tokens authorize protected endpoints via `Authorization: Bearer`.

**Non-guarantees**
- Sessions are not durable across hard cookie deletion or localStorage clearing.
- Token refresh is not guaranteed if refresh token is expired/invalid.

### 3.4 Frozen vs Flexible Areas

**Frozen**
- CSRF policy (token source + cookie/header names).
- Auth endpoint contracts (`/api/auth/login`, `/api/auth/register`, `/api/auth/refresh`, `/api/auth/logout`, `/api/auth/me`).
- Refresh cookie name/path and httpOnly requirement.

**Flexible**
- Token TTLs (env-configured).
- Rate limit thresholds (env-configured).
- UI copy/UX affordances (as long as security rules are unchanged).

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
