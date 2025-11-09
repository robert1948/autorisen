# Playbook 02: Backend Auth & Security

**Owner**: Auth Guardian
**Supporting Agents**: TestGuardianAgent, DevOps Pilot
**Status**: Doing
**Priority**: P0

---

## 1) Outcome

Ensure the CapeControl backend provides secure, reliable authentication for both **users** and **developers**, with tested JWT flows, CSRF and rate-limit protection, password management, and environment parity across local, staging, and production.

**Definition of Done (DoD):**

* All auth endpoints fully implemented and documented (`/register`, `/login`, `/logout`, `/refresh`, `/me`).
* CSRF and rate-limit tests pass reliably.
* JWT and refresh token handling secure and expiry-configured.
* Password hashing and reset flows operational.
* Security middleware stack validated (audit, sanitization, DDoS protection).
* Test coverage >90% for `backend/src/modules/auth/`.

---

## 2) Scope (In / Out)

**In Scope:**

* Auth routes and services (FastAPI modules).
* Security middlewares (CSRF, DDoS, rate-limit, sanitization, content moderation).
* JWT token creation and verification.
* Password hashing (bcrypt) and reset workflows.
* Unit + integration tests.

**Out of Scope:**

* OAuth/social logins.
* Role-based permissions beyond basic developer/user split.
* Advanced session analytics.

---

## 3) Dependencies

**Upstream:**

* Base backend configuration (settings, DB models, Alembic migrations).

**Downstream:**

* Playbook 01 – MVP Launch (depends on working auth).
* Playbook 05 – Quality & Test Readiness.

---

## 4) Milestones

| Milestone | Description                                       | Owner             | Status        |
| --------- | ------------------------------------------------- | ----------------- | ------------- |
| M1        | JWT + refresh token flow functional               | Auth Guardian     | ✅ Done        |
| M2        | CSRF and rate-limit protection validated          | TestGuardianAgent | ✅ Done        |
| M3        | Password reset + hashing tested                   | Auth Guardian     | 🔄 Pending    |
| M4        | Middleware stack reviewed (audit, sanitize, DDoS) | DevOps Pilot      | ✅ Done        |
| M5        | Auth docs + schemas finalized                     | Auth Guardian     | 🔄 Pending    |

---

## 5) Checklist (Executable)

* [x] Implement `/api/auth/login`, `/api/auth/register`, `/api/auth/logout`, `/api/auth/refresh`, `/api/auth/me`.
* [x] Add secure password hashing using bcrypt.
* [x] Validate JWT issue/refresh logic.
* [x] Ensure CSRF headers set and validated by tests.
* [x] Enable rate-limit middleware.
* [x] Verify DDoSProtectionMiddleware and InputSanitizationMiddleware active.
* [ ] Write tests in `backend/tests/test_auth_flow.py`.

---

## 6) Runbook / Commands

```bash
## Run tests locally
make test

## Run CSRF and rate-limit tests only
pytest -k "csrf or rate_limit" -v

## Validate environment security vars
printenv | grep -E 'SECRET|TOKEN|CSRF'
```text
---

## 7) Risks & Mitigations

| Risk                                       | Mitigation                                            |
| ------------------------------------------ | ----------------------------------------------------- |
| JWT expiry misconfig causes stale tokens   | Define token TTLs in `.env` and validate during tests |
| CSRF validation fails in some environments | Use TestGuardianAgent to normalize fixture data       |
| Middleware order breaks request flow       | Centralize registration in `backend/src/app.py`       |
| Password reset TTL too long/short          | Validate via configuration and doc consistency        |

---

## 8) Links

* [`docs/PLAYBOOKS_OVERVIEW.md`](../PLAYBOOKS_OVERVIEW.md)
* [`backend/src/modules/auth/`](../../backend/src/modules/auth/)
* [`backend/tests/test_auth_flow.py`](../../backend/tests/test_auth_flow.py)
* [`docs/playbooks/playbook-05-quality-testing.md`](./playbook-05-quality-testing.md)

---

## ✅ Next Actions

1. Add password reset + hashing test coverage (M3).
1. Backfill automated tests around new sanitization & DDoS middleware.
1. Finalize auth schema docs once security middleware validated (M5).
