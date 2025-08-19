# Autorisen – Development Context
**Last Updated:** 2025-08-19  
**Repo:** https://github.com/robert1948/autorisen  
**Purpose:** Central reference for architecture, environments, security, and active workstreams.

## 1) System Overview
- **Frontend:** (if applicable) React / Vite (planned)  
- **Backend:** FastAPI (Python 3.11+), Gunicorn/Uvicorn worker  
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
- **Local:** Docker Compose; `.env.dev`  
- **Staging (Heroku):** `autorisen` staging app; `.env.staging` via Heroku config vars  
- **Production (Heroku):** `capecraft` production app; `.env.prod` via Heroku config vars

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

## 7) Active Workstreams
- [ ] Finalize auth routes parity with production
- [ ] `/me` endpoints for user/developer
- [ ] API docs autogen and Swagger tuning
- [ ] Stabilize staging→prod pipeline (buildpacks, runtime, requirements lock)
- [ ] Analytics dashboard MVP

## 8) Risks
- Drift between staging (autorisen) and prod (capecraft)
- Rate limit defaults vs. real traffic
- Missing env vars in Codespaces/Heroku

## 9) References
- `DEPLOYMENT_GUIDE_2025.md` – detailed ops guide
- `API_DOCUMENTATION_2025.md` – routes & schemas
- `AUTH_TROUBLESHOOTING_GUIDE.md` – quick fixes for login/registration
