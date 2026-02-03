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

- Login
- Token refresh
- Logout

(Details to be added; behavior must match implementation.)

### 3.2 CSRF Policy

- Token source
- Cookie name(s)
- Required headers
- Protected endpoints

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

#### 6.1.1 Operating Policy: Plan vs WO (Effective Immediately)

- Default mode is **plan-driven execution**.
  - VS_Chat **MAY** act on any planned item in `docs/project-plan.csv` using the **Plan ID** as the primary handle.
  - Traceability **MUST** include:
    - branch name: `wo/<plan-id>-<topic>-<nnn>`
    - commit message includes `(PLAN_ID)`
    - PR description includes Plan ID, scope, files changed, and verification evidence
- Work Order (WO) documents are **REQUIRED** only when any hard-gate condition applies:
  - migrations / schema changes / data moves
  - dependency additions or updates
  - deployments or pipeline changes (including autorisen) or anything that could touch capecraft/prod
  - security / auth / payments changes
  - broad refactors or multi-module changes beyond a single, bounded plan item
- If a WO is required, VS_Chat **MUST** create it as step 1 of the task (do not wait for pre-existing files):
  - create `docs/work_orders/WO-<YYYYMMDD>-<short-title>.md`
  - include goal, constraints, scope, steps, verification, rollback, evidence commands
  - record the artifact path in the relevant plan row (notes/artifacts) when present
- Reporting standard (**always**):
  - preflight evidence: `git status --porcelain`, `git status -uall`, `git branch --show-current`, `git --no-pager log -1 --oneline`
  - base alignment: work branches **MUST** be based on `origin/<default-base>` (no local diverged base)
  - minimal diffs + verification commands included
  - final evidence pack is pasted back

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
