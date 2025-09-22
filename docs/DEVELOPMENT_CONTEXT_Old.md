# Autorisen – Development Context

**Last Updated:** 2025-08-21  
**Repo:** [https://github.com/robert1948/autorisen]
**Purpose:** Central reference for architecture, environments, operational notes, and current remediation steps.

## 1) System Overview

- **Frontend:** (if applicable) React / Vite (planned)
- **Backend:** FastAPI (Python 3.12+), Gunicorn/Uvicorn worker
- **Database:** PostgreSQL (Heroku Postgres in prod), SQLite for quick local dev (optional)
- **Infra:** Heroku (staging/prod), GitHub Codespaces for dev, Docker/Compose for local
- **CI/CD:** GitHub Actions (build, test, deploy), Heroku pipelines
- **Key Domains:** cape-control.com (platform brand), _Autorisen_ app for API/services

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
    - `services/` – business/service layer (ai\_\*, audit, alerts, analytics, auth, etc.)
  - `alembic/` – migrations

## 3) Environments

- **Local:** Docker Compose; `.env.dev`
- **Staging (Heroku):** `autorisen` staging app; `.env.staging` via Heroku config vars
- **Production (Heroku):** `capecraft` production app; `.env.prod` via Heroku config vars

### Recent operational notes (Aug 2025)

- Heroku uses buildpack-based deployment (Procfile, requirements.txt, runtime.txt at backend root). The repository delegates backend dependencies to `backend/requirements.txt` using `-r backend/requirements.txt` in top-level `requirements.txt`.
- Avoid top-level unconditional imports of optional SDKs (for example: `stripe`, `openai`, `anthropic`) in modules that are imported by `app.main` on startup. Doing so caused dyno crashes during startup; several modules were made resilient by guarding imports.
- The Procfile uses `PYTHONPATH=backend gunicorn app.main:app -k uvicorn.workers.UvicornWorker` to ensure `app` resolves to the `backend/app` package.

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

- If the dyno crashes during boot with ModuleNotFoundError: No module named 'X', confirm `backend/requirements.txt` includes that package and top-level `requirements.txt` references it (if needed for Heroku build). After changes, push to `main` to trigger a new Heroku build.
- Common crash sources: import-time side effects (setting API keys, initializing SDK clients). Fix pattern: wrap `import stripe` or other optional SDK imports in try/except and set a `STRIPE_AVAILABLE` (or similar) flag.
- Logs: run `heroku logs --tail -a <app>` and look for the import stack that leads to the failing module.

## 7) Active Workstreams

- [ ] Finalize auth routes parity with production
- [ ] `/me` endpoints for user/developer
- [ ] API docs autogen and Swagger tuning
- [ ] Stabilize staging→prod pipeline (buildpacks, runtime, requirements lock)
- [ ] Analytics dashboard MVP

## 8) Recent fixes and follow-ups

- Fixed corrupted/partially written route files that contained Markdown/code fences (e.g., `backend/app/routes/stripe_routes_simple.py`) and removed code that caused syntax errors.
- Hardened Stripe integration modules so the app boots when `stripe` is not installed; dependent endpoints return 503 when the integration is disabled.
- Follow-up items:
  - Scan repository for other optional SDKs imported at module level and harden them similarly.
  - Consolidate runtime dependencies in `backend/requirements.txt` and pin critical packages to reduce Heroku build surprises.
  - Add a lightweight smoke test in CI that does an import-sanity check (e.g., `python -c "import app; print('ok')"`) so import-time exceptions are caught in CI before deploy.

## 8) Risks

- Drift between staging (autorisen) and prod (capecraft)
- Rate limit defaults vs. real traffic
- Missing env vars in Codespaces/Heroku

## 9) References

- `DEPLOYMENT_GUIDE_2025.md` – detailed ops guide
- `API_DOCUMENTATION_2025.md` – routes & schemas
- `AUTH_TROUBLESHOOTING_GUIDE.md` – quick fixes for login/registration
