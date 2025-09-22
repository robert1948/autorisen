# Autorisen – Development Context

**Last Updated:** 2025-09-21
**Repo:** https://github.com/robert1948/autorisen
**Purpose:** Central reference for architecture, environments, operational notes, and current remediation steps.

## Working Tracker (edit this section as you make progress)

- Date: 2025-09-21
- Author: Robert

- Progress (short bullets):
  - [ ] Example: Backend smoke checks passing locally

- Next steps (1–3 concrete items):
  1. Standardize host-facing ports in docs and Makefile (status: done)
  2. Optional: Sweep docs to add clarifiers for container-internal port 5173 (status: pending)

- Blockers / Needs:
  - None currently

- Related files / quick commands:
  - `Makefile` — available dev targets (e.g., `make dev-up`, `make smoke`, `make fe-local`)
  - `docker-compose.yml` — container service mappings

Quick run (from repo root):

```bash
docker compose up -d backend
cd client && VITE_API_BASE="http://localhost:8000" pnpm dev -- --host 0.0.0.0 --port 3000
make smoke
```

---

## Archive: previous DEVELOPMENT_CONTEXT.md (DEVELOPMENT_CONTEXT.md.bak)

````plaintext
Project development notes — AutoLocal
==================================

This file captures quick development context for the repository so contributors have a
single place to check common local commands, environment variables, and deployment
notes.

Local ports (compose / dev):
- Backend (API): http://localhost:8000  (container binds 8000 -> host 8000)
- Frontend (Vite dev): http://localhost:3000 (compose) or local Vite may pick a free port (e.g. 3005)
- Postgres (host): 5433 -> container 5432
- Redis: 6379

Common local commands (run from repo root):
- Start dev stack (compose):
  ```bash
  make dev-up
  ```
- Apply migrations (inside container):
  ```bash
  make migrate
  ```
- Start frontend locally (hot reload):
  ```bash
  make fe-local
  ```
- Tail backend logs:
  ```bash
  make be-logs
  ```

Notes about `make smoke` and ports:
- `make smoke` uses `HOST_HTTP_PORT` default (8010). If your backend is bound to 8000,
  either export `HOST_HTTP_PORT=8000` in your shell or set it in `.env` so the smoke
  target checks the correct port.

Heroku staging (safe operations only):
- The project ships with Makefile helpers for building and pushing container images to
  Heroku's Container Registry and releasing them to the `autorisen` staging app.
- By default the Makefile avoids provisioning addons or setting secrets automatically
  to prevent accidental changes. If you need to deploy to Heroku, follow the
  `heroku-stg-preview` and `heroku-stg-apply` targets and review printed instructions.

Do not change Heroku app settings or addons without explicit confirmation from the
project owner. The `autorisen` staging app is already configured and should not be
modified unless you're performing an approved update.

If this file was accidentally deleted, this is a reasonable minimal replacement. Edit
as needed to include any other local instructions specific to your machine.

````

---

## 1) System Overview

- **Frontend:** (if applicable) React / Vite (planned)
- **Backend:** FastAPI (Python 3.12+), Gunicorn/Uvicorn worker
- **Database:** PostgreSQL (Heroku Postgres in prod), SQLite for quick local dev (optional)
- **Infra:** Heroku (staging/prod), GitHub Codespaces for dev, Docker/Compose for local
- **CI/CD:** GitHub Actions (build, test, deploy), Heroku pipelines
- **Key Domains:** cape-control.com (platform brand), *Autorisen* app for API/services

## 2) Directory Map (High-level)

See `COMPREHENSIVE_FILE_DIAGRAM.md` for full tree. Highlights:

- `backend/`

  - `app/`

    - `api/` – route modules (e.g., payment, health, auth, analytics)
    - `config/` – settings, environment handling
    - `core/` – app factory, startup, logging
    - `middleware/` – rate limit, monitoring, input sanitization
    - `models/` – SQLAlchemy models
    - `routes/` – include routers (auth_v2, alerts, analytics, etc.)
    - `services/` – business/service layer (ai_*, audit, alerts, analytics, auth, etc.)

  - `alembic/` – migrations

## 3) Environments

- **Local:** Docker Compose; `.env.dev` (see DB helpers in `Makefile`)
- **Staging (Heroku):** `autorisen` staging app; `.env.staging` via Heroku config vars
- **Production (Heroku):** `capecraft` production app; `.env.prod` via Heroku config vars

### Recent operational notes (Aug–Sep 2025)

- Heroku uses buildpack-based deployment (Procfile, requirements.txt, runtime.txt at backend root). The repository delegates backend dependencies to `backend/requirements.txt` using `-r backend/requirements.txt` in top-level `requirements.txt`.
- Avoid top-level unconditional imports of optional SDKs (for example: `stripe`, `openai`, `anthropic`) in modules imported by `app.main` on startup. Doing so caused dyno crashes during startup; modules were made resilient by guarding imports.
- The Procfile uses `PYTHONPATH=backend gunicorn app.main:app -k uvicorn.workers.UvicornWorker` to ensure `app` resolves to the `backend/app` package.
- **Local DB connectivity:** from the host, connect to Postgres via **`127.0.0.1:5433`** (mapped to container `db:5432`). Do **not** use the Docker service hostname `db` from the host; it only resolves inside the Docker network. See **Remediation Steps** below for the Makefile/env fix.

## 4) Security & Compliance

- HTTPS termination by Heroku
- JWT auth (users & developers), password hashing (bcrypt/passlib)
- DDoS/input-sanitization/content moderation middleware
- Audit logs & analytics (service layer)
- Secrets in environment (never committed)

## 5) Data & Migrations

- **ORM:** SQLAlchemy
- **Migrations:** Alembic – see `DEPLOYMENT.md` for commands
- **Backups:** Heroku PG backups (auto & manual)

## 6) Observability

- **Logs:** Heroku logs, structured logging in `services/*`
- **Health:** `/health` route
- **Performance:** `ai_performance_service` metrics

### Troubleshooting notes

- If the dyno crashes during boot with `ModuleNotFoundError: No module named 'X'`, confirm `backend/requirements.txt` includes that package and top-level `requirements.txt` references it (if needed for Heroku build). After changes, push to `main` to trigger a new Heroku build.
- Common crash sources: import-time side effects (setting API keys, initializing SDK clients). Fix pattern: wrap `import stripe` or other optional SDK imports in try/except and set a `STRIPE_AVAILABLE` (or similar) flag.
- Logs: run `heroku logs --tail -a <app>` and look for the import stack that leads to the failing module.

## 7) Active Workstreams

- [ ] **Registration verification and email communication** (develop/test on *autorisen* first)
- [ ] Finalize auth routes parity with production
- [ ] `/me` endpoints for user/developer
- [ ] API docs autogen and Swagger tuning
- [ ] Stabilize staging→prod pipeline (buildpacks, runtime, requirements lock)
- [ ] Analytics dashboard MVP

## 8) Recent fixes and follow-ups

- Fixed corrupted/partially written route files that contained Markdown/code fences (e.g., `backend/app/routes/stripe_routes_simple.py`) and removed code that caused syntax errors.
- Hardened Stripe integration modules so the app boots when `stripe` is not installed; dependent endpoints return 503 when the integration is disabled.
- **Follow-up items:**

  - Scan repository for other optional SDKs imported at module level and harden them similarly.
  - Consolidate runtime dependencies in `backend/requirements.txt` and pin critical packages to reduce Heroku build surprises.
  - Add a lightweight smoke test in CI that does an import-sanity check (e.g., `python -c "import app; print('ok')"`) so import-time exceptions are caught in CI before deploy.

## 9) Remediation Steps (Local DB & Alembic)

- **Symptom:** `psycopg.OperationalError: [Errno -5] No address associated with hostname` when running Alembic locally.
- **Root cause:** Host was using `POSTGRES_HOST=db` (Docker-only name). From the host, use `127.0.0.1` with published port `5433`.
- **Fix:**

  1. Add a host-only env file `.env.host`:

     ```ini
     POSTGRES_USER=dev_user
     POSTGRES_PASSWORD=dev_password
     POSTGRES_DB=autorisen_dev
     POSTGRES_HOST=127.0.0.1
     POSTGRES_PORT=5433

     ```

  2. Update `Makefile` DB helpers to load env files in order (container file first, host overrides last), and **unset `DATABASE_URL`** so `env.py` composes from `POSTGRES_*`.
  3. One-shot sanity:

     ```bash
     PGPASSWORD=dev_password psql -h 127.0.0.1 -p 5433 -U dev_user -d autorisen_dev -c "\conninfo"
     DATABASE_URL="postgresql+psycopg2://dev_user:dev_password@127.0.0.1:5433/autorisen_dev" alembic current -v
     ```

## 10) Risks

- Drift between staging (*autorisen*) and prod (*capecraft*)
- Rate limit defaults vs. real traffic
- Missing env vars in Codespaces/Heroku

## 11) References

- `DEPLOYMENT_GUIDE_2025.md` – detailed ops guide
- `API_DOCUMENTATION_2025.md` – routes & schemas
- `AUTH_TROUBLESHOOTING_GUIDE.md` – quick fixes for login/registration

---

## PR Checklist (copy/paste into pull requests)

```markdown
### Environment Promotion Policy ✅
- [ ] Localhost: implemented & fully tested.
- [ ] Staging (Heroku: `autorisen`): deployed & cloud-tested end‑to‑end.
- [ ] Production (Heroku: `capecraft`): promote only after staging verification.

### Container / Release 📦
- [ ] Image built from commit: `<SHA>`; image tag: `<IMAGE:TAG>`.
- [ ] Pushed to registry: `registry.heroku.com/autorisen/web`.
- [ ] Released to staging: `autorisen` (Heroku release: `v###`).
- [ ] Staging app URL: https://autorisen.herokuapp.com  (or custom domain)

### Migrations & Data 🗄️
- [ ] Alembic status at head on staging (`alembic current` matches repo).
- [ ] Migrations applied on staging (`alembic upgrade head`).
- [ ] Rollback plan noted (previous release `v###` or migration `down` step).

### Smoke & Functional 🔎
- [ ] `/alive` health OK on staging.
- [ ] Assets MIME check OK (CSS/JS not served as text/html).
- [ ] Critical user flows verified on staging (list):
      - [ ] Registration verification email delivered
      - [ ] Email link/token validates account
      - [ ] Login after verification

### Approvals ✅
- [ ] QA sign‑off
- [ ] Reviewer sign‑off
- [ ] Ready to promote to `capecraft`
```
     POSTGRES_PORT=5433

     ```

  2. Update `Makefile` DB helpers to load env files in order (container file first, host overrides last), and **unset `DATABASE_URL`** so `env.py` composes from `POSTGRES_*`.
  3. One-shot sanity:

     ```bash
     PGPASSWORD=dev_password psql -h 127.0.0.1 -p 5433 -U dev_user -d autorisen_dev -c "\\conninfo"
     DATABASE_URL="postgresql+psycopg2://dev_user:dev_password@127.0.0.1:5433/autorisen_dev" alembic current -v
     ```

## 10) Risks

 - Drift between staging (*autorisen*) and prod (*capecraft*)
 - Rate limit defaults vs. real traffic
 - Missing env vars in Codespaces/Heroku

## 11) References

 - `DEPLOYMENT_GUIDE_2025.md` – detailed ops guide
 - `API_DOCUMENTATION_2025.md` – routes & schemas
 - `AUTH_TROUBLESHOOTING_GUIDE.md` – quick fixes for login/registration

---

## PR Checklist (copy/paste into pull requests)

```markdown
### Environment Promotion Policy ✅
- [ ] Localhost: implemented & fully tested.
- [ ] Staging (Heroku: `autorisen`): deployed & cloud-tested end‑to‑end.
- [ ] Production (Heroku: `capecraft`): promote only after staging verification.

### Container / Release 📦
- [ ] Image built from commit: `<SHA>`; image tag: `<IMAGE:TAG>`.
- [ ] Pushed to registry: `registry.heroku.com/autorisen/web`.
- [ ] Released to staging: `autorisen` (Heroku release: `v###`).
- [ ] Staging app URL: https://autorisen.herokuapp.com  (or custom domain)

### Migrations & Data 🗄️
- [ ] Alembic status at head on staging (`alembic current` matches repo).
- [ ] Migrations applied on staging (`alembic upgrade head`).
- [ ] Rollback plan noted (previous release `v###` or migration `down` step).

### Smoke & Functional 🔎
- [ ] `/alive` health OK on staging.
- [ ] Assets MIME check OK (CSS/JS not served as text/html).
- [ ] Critical user flows verified on staging (list):
      - [ ] Registration verification email delivered
      - [ ] Email link/token validates account
      - [ ] Login after verification

### Approvals ✅
- [ ] QA sign‑off
- [ ] Reviewer sign‑off
- [ ] Ready to promote to `capecraft`
```
