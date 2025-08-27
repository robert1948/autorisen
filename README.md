# autorisen 250827

Development site for Cape Control with PostgreSQL Development Environment

## Overview

- **Backend**: FastAPI (Python 3.12+), Gunicorn + Uvicorn worker
- **Frontend**: React / Vite (client/)
- **Database**: PostgreSQL in production (Heroku Postgres), PostgreSQL local development environment, SQLite fallback for quick dev
- **Development**: Automated local PostgreSQL setup with production schema replication

## Quick Setup Options

### Option A: PostgreSQL Development Environment (Recommended)

**Full production parity with automated setup:**

1. **Prerequisites**: Ensure PostgreSQL 16+ is installed locally

2. **Automated Database Setup**:
```bash
# Clone and setup environment
git clone <repo-url>
cd autorisen
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
pip install -r backend/requirements.txt

# Run automated PostgreSQL setup (creates local DB with production schema)
bash ./scripts/setup_local_postgres.sh "postgres://[HEROKU_DB_URL]" autorisen_local vscode
```

3. **Start Development**:
```bash
# Backend (with PostgreSQL)
export PYTHONPATH=backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (separate terminal)
cd client
npm install
npm run dev
```

### Option B: SQLite Quick Development

**For rapid prototyping without PostgreSQL setup:**

1. Create and activate a virtualenv, install tools:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
pip install -r backend/requirements.txt
# Optional: install core + optional (Stripe) for local development
pip install -r backend/requirements-dev.txt
```

2. Set environment variables (example `.env` or export manually):

```bash
export DATABASE_URL=sqlite:///./dev.db
export STRIPE_SECRET_KEY=sk_test_...
# other env vars per backend/config.py
```

3. Run the backend (development):

```bash
# from repository root
export PYTHONPATH=backend
uvicorn app.main:app --reload
```

## Database Management

### Local PostgreSQL Environment

**Connection Details:**
- Host: `localhost`
- Port: `5432` 
- Database: `autorisen_local`
- Username: `vscode`
- Password: `123456`

**Database Schema:**
- `users_v2` - User accounts and authentication
- `tokens_v2` - Authentication tokens and sessions  
- `developer_earnings_v2` - Developer payment tracking
- `password_resets_v2` - Password reset functionality
- `audit_logs_v2` - Security audit trail

**Useful Commands:**
```bash
# Connect to local database
PGPASSWORD=123456 psql -h localhost -U vscode -d autorisen_local

# Test user registration
python ./scripts/dummy_register.py

# View database tables
psql> \dt
```

## Heroku Buildpack Deployment

- Heroku now uses buildpack-based deployment (not container-based). No `heroku.yml` is required.
- The Procfile uses `PYTHONPATH=backend` so Heroku starts the app as `gunicorn app.main:app -k uvicorn.workers.UvicornWorker`.
- Heroku reads the top-level `requirements.txt` during build, which references `backend/requirements.txt` for backend dependencies. Keep `backend/requirements.txt` authoritative for backend runtime packages.
- Avoid importing optional SDKs (e.g., `stripe`, `openai`) at module import time for modules that are imported during app startup. Use try/except and a flag (e.g., `STRIPE_AVAILABLE`) or defer import into the function that needs it.

## Stripe & optional integrations

- The project contains Stripe integration under `backend/app/services/stripe_service.py` and routes in `backend/app/routes/`.
- If you don't want to install Stripe in a given environment, the codebase has been updated to be resilient: routes return 503 when the Stripe SDK is not available.
- To enable Stripe fully, add `stripe` to `backend/requirements.txt` and set `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET` in environment variables.

Optional install (Stripe)

To install the optional Stripe SDK (used only if you enable payments), run:

```bash
# from repository root
pip install -r backend/requirements-optional.txt
```

# autorisen — CapeControl integration/staging

This repository is the staging/integration workspace for CapeControl (Capecraft).

Quick facts

- Backend: FastAPI 0.110.0 (Python 3.12)
- Frontend: React 18 + Vite (in `client/`)
- Production deployment: Heroku (app: `capecraft`, current v663)

Purpose

- Host integration work for autorisen features before merging into CapeControl production.
- Provide import-sanity checks and OpenAPI diffing in CI to prevent startup or contract regressions.

Local quickstart

1. Create and activate a virtualenv and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
pip install -r backend/requirements.txt
# Optional: install core + optional (Stripe) for local development
pip install -r backend/requirements-dev.txt
```

2. Configure environment variables (example):

```bash
export DATABASE_URL=sqlite:///./dev.db
export STRIPE_SECRET_KEY=sk_test_...
# see backend/app/config.py for other env vars
```

3. Run backend locally:

```bash
export PYTHONPATH=backend
uvicorn app.main:app --reload --port 8000
```

Notes

- The canonical FastAPI app module is `backend/app/main.py` (import path: `app.main:app`).
- The project defers optional SDK imports (e.g., `stripe`) to runtime to avoid import-time crashes on Heroku.
- CI contains an import-sanity job and an OpenAPI diff script under `.github/workflows/` and `scripts/`.

Heroku

- Procfile and top-level `requirements.txt` are used by Heroku; ensure `backend/requirements.txt` is referenced appropriately.
- Recommended Stripe pin for Heroku compatibility: `stripe==7.7.0` (or update to match your actual requirements).

If you'd like, I can:

- Produce and commit `docs/openapi_baseline.json` (exported from production/staging) so CI diffs will run against a baseline.
- Add a short 'Rollback' section to `docs/Release Runbook.md` with Heroku restore commands.
