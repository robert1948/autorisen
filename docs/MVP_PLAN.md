# MVP Project Plan

**Last updated:** 2025-09-18 15:29 UTC

## Legend

- `[ ]` = open  
- `[x]` = done  
- IDs are in `(ID: ...)` for scripting.

---

## Phase 1 — Production-grade Auth

- [ ] Replace dev login stub with real DB lookup + password hash (ID: P1-AUTH-DB)
- [ ] Email verification flow (register → email link → verify) (ID: P1-AUTH-VERIFY)
- [ ] Password reset flow (forgot → email link → reset) (ID: P1-AUTH-RESET)
- [ ] Rate limiting on login/forgot (Redis) (ID: P1-AUTH-RATE)

---

## Phase 2 — Post-login Hello World

- [ ] Protected `/api/protected/ping` and dashboard card (ID: P2-PING)
- [ ] Mini feature (choose one: Notes/Projects/Profile) CRUD (ID: P2-MINI-FEATURE)

---

## Phase 3 — Files (optional for MVP+)

- [ ] Avatar upload via MinIO (presigned PUT/GET) (ID: P3-FILES-AVATAR)

---

## Phase 4 — Payments (optional for MVP+)

- [ ] Stripe checkout + webhook sets plan (test mode) (ID: P4-PAY-STRIPE)

---

## Phase 5 — Release Readiness

- [ ] CI (lint/test/build) (ID: P5-CI)
- [ ] One-command deploy to Heroku + auto-migrate (ID: P5-CD)
- [ ] Harden cookies/CORS for HTTPS (ID: P5-SECURE-COOKIES)
- [ ] Basic logs + health checks green on staging (ID: P5-OBS)

---

## Done Log

(append notes when you check items)

---

## Testing Commands

- Auth Verify Flow: `docker exec -e PYTHONPATH=/app/backend -w /app/backend autorisen-backend /opt/venv/bin/pytest -q tests/test_auth_verify_flow.py -q`
