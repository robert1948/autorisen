# CapeControl Deployment Checklist

> Last updated: March 4, 2026 (v0.2.5) — supersedes the Nov 7, 2025 revision.

## ✅ Backend Authentication

- [x] JWT access + refresh tokens with httpOnly cookie support
- [x] Multi-step registration (`/register/step1`, `/register/step2`) with password policy (12+ chars)
- [x] Login: email/password, Google OAuth, LinkedIn OAuth (PKCE-style signed state)
- [x] TOTP MFA: setup, verify, disable, status — secrets encrypted at rest (Fernet)
- [x] Password reset flow (`/password-reset/request`, `/password-reset/confirm`)
- [x] Token refresh with JTI denylist (Redis-backed)
- [x] Logout with all-devices option (token version bump)
- [x] Admin invite emails wired (SMTP via mailer)

## ✅ Security Hardening

- [x] reCAPTCHA on login, registration, and OAuth (server + client)
- [x] Input sanitisation ASGI middleware (XSS, prompt-injection patterns)
- [x] DDoS protection middleware (token bucket + burst detection + IP blocking)
- [x] Rate limiting: slowapi global + per-auth-endpoint via `login_audits` table
- [x] CSRF signed HMAC tokens with TTL — mutating requests enforced, PayFast ITN exempt
- [x] Production secret-key startup guard (rejects `dev-*` keys when `ENV=prod`)
- [x] MFA TOTP secrets encrypted at rest (`MFA_ENCRYPTION_KEY` / Fernet)
- [x] CORS properly configured in app factory
- [ ] Dedicated security response headers middleware (HSTS, X-Content-Type-Options, X-Frame-Options, CSP) — currently relies on CDN/proxy layer

## ✅ Deployment Pipeline

### Container Build

- [x] Multi-stage Dockerfile: Node 20 Alpine (frontend) → Python 3.12-slim (backend)
- [x] Non-root user, Gunicorn + UvicornWorker, optimised pip install
- [x] `make docker-build` with retry logic

### CI/CD (GitHub Actions)

- [x] `ci-test.yml` — pytest + ruff lint on every PR
- [x] `deploy-heroku.yml` — auto-deploy on push to `main` (path-filtered)
- [x] `security.yml` — dependency & code security scanning
- [x] `frontend-ci.yml` — TypeScript compilation + Vite build check
- [x] Post-deploy verification: `/api/health`, `/api/auth/csrf`, `/api/version`

### Manual Deploy

```bash
make deploy          # build → push → release (capecraft, 3-attempt retry)
make ship            # test → build → deploy → verify (full pipeline)
make verify-deploy   # health + CSRF + version check only
```

## ✅ Database & Migrations

- [x] Alembic migrations (head: `7a1b2c3d4e5f`)
- [x] Auto-migrate **disabled** in production (`RUN_DB_MIGRATIONS_ON_STARTUP=0`)
- [x] GitHub Actions runs `heroku run alembic upgrade heads` post-deploy
- [x] Manual: `make migrate-up`, `make heroku-run-migrate`
- [x] Test isolation: SQLite for CI (`codex-test`), ephemeral Postgres (`codex-test-pg`)

## ✅ Testing

- [x] 100 pytest tests across 20 test files (auth, CSRF, billing, marketplace, MFA crypto, module smoke, etc.)
- [x] Smoke tests for 9 modules: account, audit, capsules, chat, ops, rag, support, usage, user
- [x] `make codex-test` (SQLite CI), `make codex-test-pg` (Postgres integration)
- [x] `make codex-test-cov` (coverage), `make codex-test-heal` (fixture regeneration)
- [x] Frontend: vitest + Playwright (`pnpm test`, `pnpm ui:smoke`)

## ✅ Frontend

- [x] Vite 5 + React 18 + TypeScript + Tailwind CSS
- [x] React Query, React Router, React Hook Form, Zod
- [x] Dev proxy: `/api` → `localhost:8000` with WebSocket support
- [x] Logo asset system (favicon, PWA manifest, Apple Touch, Android Chrome)
- [x] reCAPTCHA client integration (`VITE_RECAPTCHA_SITE_KEY`)
- [x] Accessibility: ARIA labels, keyboard nav, WCAG 2.1 AA contrast

## ✅ Monitoring & Observability

- [x] Health endpoints: `/api/health` (DB check), `/api/health/alive`, `/api/health/ping`
- [x] Version endpoint: `/api/version` (build metadata)
- [x] Metrics: `MonitoringMiddleware` → per-path latency (p50/p95/p99), status codes, error rates at `/api/metrics`
- [x] Audit logging: `/api/audit/events`, `/api/audit/export`, `/api/audit/stats`
- [x] Sentry integration: `SENTRY_DSN`, 20% trace sampling, release tagging
- [x] Security stats: `/api/security/stats` (DDoS, sanitisation, rate limiting)

## 🔄 Pre-Deploy Verification

```bash
make codex-test                # unit tests (SQLite)
make codex-test-pg             # integration tests (Postgres)
make docker-build && make docker-run   # local container smoke test
make deploy                    # push to capecraft (requires ALLOW_PROD=1)
make heroku-logs               # tail production logs
```

## 📋 Remaining Items

- [ ] Security response headers middleware (HSTS, CSP, X-Frame-Options) — or document CDN coverage
- [ ] Align package manager: `pnpm-lock.yaml` in client vs `npm` in Dockerfile
- [ ] Stripe payment integration (BP-STRIPE-001 — deferred to Q3 2026)
