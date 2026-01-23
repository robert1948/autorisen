# CapeControl — System Specification

> Status: DRAFT  
> Last updated: 2026-01-23  
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

### 2.5.3 Interest-Triggered Registration UX Policy (Normative)

Purpose: Define mandatory UX policy governing how and when registration may be presented to unauthenticated users.

Definitions:

**Unauthenticated user**
A visitor without a valid authenticated session (e.g., no JWT or session token).

**Interest signal**
An observable, client-side action by an unauthenticated user that reasonably indicates engagement or intent.
Recognized interest signals include (non-exhaustive):
- Clicking “Learn more”, “Explore”, “Try”, or “Preview” CTAs
- Viewing agent detail pages
- Visiting pricing or plan comparison pages
- Scrolling beyond 50% of page viewport
- Remaining on a page for more than 20 seconds
- Navigating to a second page within the session
- Attempting login with an unknown email address
- Accessing a protected route or feature

The interest signal taxonomy is extensible and does not require backend coordination.

Mandatory UX rules (non-negotiable):
1. **Interest → Invitation rule**: registration prompts must only appear after at least one interest signal has been detected for an unauthenticated user.
1. **Invitation, not barrier rule**: all registration prompts must be optional, clearly dismissible, and include a “Continue browsing” (or equivalent) option.
1. **No first-interaction friction rule**: first-time unauthenticated users must never encounter forced registration, mandatory login, or UX dead ends that block initial exploration.
1. **Soft-gate requirement for protected routes**: access to authenticated features may display an explanatory interstitial, but must not hard-redirect without user choice.
1. **Global reachability rule**: a registration entry point must remain reachable from any screen or UX context.
1. **Accessibility requirement**: all registration CTAs, prompts, and interstitials must meet WCAG 2.1 AA accessibility standards, including keyboard navigation and screen-reader compatibility.

Governance & compliance:
- Applies to all frontend UX work involving authentication, onboarding, or gated features.
- Any UI implementation touching registration or login must comply by default.
- Deviations require explicit approval from Robert (final authority).
- Violations are classified as critical UX defects.

Prohibited behaviors:
- Mandatory registration prior to content access
- Login walls on first interaction
- Modal registration prompts on initial page load
- UX flows that trap unauthenticated users

Auditability:
- Compliance must be verified during pull request reviews, UX audits, and Work Order evidence checks.

---

### 2.5.4 Onboarding Pages (Post-Auth, Pre-App)

Purpose: Profile completion and guided activation.

- `/onboarding/welcome`
- `/onboarding/profile`
- `/onboarding/checklist`
- `/onboarding/guide`

Notes:
- Accessible only after successful authentication
- Completion gates access to App pages

---

### 2.5.5 App Pages (Authenticated Core)

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

### 2.5.6 Help & Support Pages

Purpose: Self-service assistance.

- `/help`
- `/help/knowledge-base`

Notes:
- Read-only
- No ticketing or chat in MVP

---

### 2.5.7 Explicitly Out of Scope (MVP)

- Admin console
- Multi-tenant org management
- Advanced analytics
- In-app payments execution
- Notifications center

---

### 2.5.8 Navigation Rules

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

This section defines the authoritative behavior for authentication and session establishment.
The implementation MUST conform to these flows without adding implicit behaviors.

#### Shared Requirements (All Flows)

- **Endpoints (backend):** authentication routes are served under `/api/auth/*`.
- **CSRF:** All non-`GET`/non-safe requests MUST satisfy the CSRF checks defined in §3.2.
  - Clients MUST obtain a CSRF token via `GET /api/auth/csrf` prior to calling any `POST /api/auth/*` endpoint.
  - The CSRF token MUST be presented in both a cookie (`csrftoken`) and a request header (`X-CSRF-Token`); the values MUST match.
- **Access token usage:** The backend issues an access token (JWT). Clients MUST treat it as a bearer token and send it in `Authorization: Bearer <access_token>` for authenticated API calls.
- **Refresh token usage:** The backend issues a refresh token and sets it as an HttpOnly cookie named `refresh_token` scoped to the `/api/auth` path.
- **reCAPTCHA (when enabled):** If reCAPTCHA verification is enabled, login MUST include a valid `recaptcha_token` or the request fails.

#### Login Flow

- **Endpoint:** `POST /api/auth/login`
- **Input:** `email`, `password`, and (when enabled) `recaptcha_token`.
- **Behavior (MUST):**
  - Normalize the email address (trim + lowercase) before lookup.
  - Enforce auth lockout and rate limiting prior to password verification.
  - If reCAPTCHA verification is enabled, verify `recaptcha_token`.
  - Reject unverified email accounts.
  - Verify credentials; on success issue a new access token and refresh token.
  - Set the `refresh_token` cookie (HttpOnly; `/api/auth` path).
  - Return the access token and refresh token in the response payload.
- **Failure outcomes (MUST):**
  - Locked-out accounts are rejected (with a `Retry-After` hint).
  - Invalid credentials are rejected.
  - Email-not-verified accounts are rejected.

#### Token Refresh Flow

- **Endpoint:** `POST /api/auth/refresh`
- **Input:** refresh token provided either:
  - via request body (`refresh_token`), or
  - via cookie (`refresh_token`).
- **Behavior (MUST):**
  - Validate the presented refresh token.
  - Issue a new access token.
  - Rotate/refresh the refresh token and re-set the `refresh_token` cookie.
  - Return the new access token and refresh token in the response payload.
- **Failure outcomes (MUST):**
  - Missing/invalid refresh tokens are rejected.

#### Logout Flow

- **Endpoint:** `POST /api/auth/logout`
- **Input:** optional JSON payload `{ "all_devices": boolean }`.
- **Behavior (MUST):**
  - Clear the `refresh_token` cookie.
  - If a refresh token cookie is present and server-side revocation is available, revoke it on a best-effort basis.
  - If an access token is available (typically via `Authorization`), the backend MUST denylist that token identifier until expiry (best-effort).
  - If `all_devices=true` and a user can be resolved, the backend MUST invalidate all outstanding tokens for that user by advancing the user token version.
- **Client behavior (MUST):**
  - After logout, the client MUST treat the session as ended (discard any stored access token) and return the user to `/login`.

### 3.2 CSRF Policy

This section defines the authoritative CSRF policy for browser + cookie-based requests.

#### Token Sources and Matching Rule

- CSRF validation MUST require two copies of the same token:
  - **Cookie:** `csrftoken`
  - **Header:** `X-CSRF-Token`
- The backend MUST reject requests if either value is missing.
- The backend MUST reject requests if the cookie and header values do not match.
- The backend MUST validate token integrity (e.g., signed/validated token format) and reject invalid tokens.

#### Token Issuance and Refresh

- **Issuance endpoint:** `GET /api/auth/csrf`
- The backend MUST set the CSRF token as a non-HttpOnly cookie (`csrftoken`) and MUST also return the token to the client (response body and/or response header).
- Clients MAY call `GET /api/auth/csrf` at any time to obtain/refresh a token (e.g., on app load, before the first `POST`, or after a `403` CSRF failure).

#### Protected Methods

- CSRF protection MUST apply to all non-safe HTTP methods:
  - Protected: `POST`, `PUT`, `PATCH`, `DELETE`
  - Not protected: `GET`, `HEAD`, `OPTIONS`, `TRACE`

#### Protected Endpoints

- Unless explicitly exempted below, CSRF protection MUST apply to all protected methods for all paths (including authentication routes).
- As a result, the following auth flows defined in §3.1 MUST be CSRF-protected because they are `POST` requests:
  - `POST /api/auth/login`
  - `POST /api/auth/refresh`
  - `POST /api/auth/logout`

#### Explicit Exemptions (Narrow, Justified)

Some endpoints are designed for server-to-server callbacks and MUST NOT be blocked by browser CSRF enforcement.
Exemptions MUST remain narrowly scoped by **method + path**.

- `POST /api/payments/payfast/checkout` (server-to-server initiation)
- `POST /api/payments/payfast/itn` (PayFast Instant Transaction Notification callback)

> Canonical reference: [SECURITY_CSRF.md](SECURITY_CSRF.md)

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

This section defines the authoritative governance rules for database/schema migrations.
These rules complement §2.6.3 (Migration & Schema Management) and are binding for all environments.

#### Approval (Required)

- Every migration MUST be explicitly approved before execution.
- “Approved” means a recorded, intentional decision by the designated authority for the target environment (see Environment Boundaries).
- Migrations MUST NOT be executed on an “assumed safe” basis.

#### No Implicit / Automatic Migrations

- The application MUST NOT run migrations automatically on startup.
- Deploy and migrate MUST be separate, explicit steps (never implicit).

#### Environment Boundaries

- **Local/dev:** migrations MAY be executed after review/approval in the local dev workflow.
- **Staging (autorisen):** migrations MAY be executed only after explicit approval and with a rollback plan.
- **Production (capecraft):** migrations MUST NOT be executed without explicit Robert approval.

#### Allowed Change Mechanism

- Schema changes MUST be performed only via versioned migrations committed to version control.
- Manual/ad-hoc schema edits MUST NOT be used in any shared environment (staging/production).

#### Rollback Policy

- Every migration MUST include downgrade guidance where feasible.
- Rollbacks in staging MAY be executed when needed and approved.
- Rollbacks in production are high-risk and MUST be treated as an exceptional action requiring explicit Robert approval.

#### Hard Stop Conditions

Migration execution MUST STOP immediately if any of the following are true:
- Approval for the target environment is missing.
- The migration is not present in version control (i.e., not a reviewed, versioned migration).
- The migration implies automatic execution during deploy/startup.
- The environment target is ambiguous (local vs autorisen vs capecraft).

---

## 7. Roadmap & Unlock Criteria

### 7.1 Frozen Milestones

- Auth stability
- Security policy locked

### 7.2 Unlock Conditions

- What enables NEXT-003
- What enables onboarding expansion
- What enables production launch

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
