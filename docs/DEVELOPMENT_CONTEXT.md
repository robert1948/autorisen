# 🛠 DEVELOPMENT CONTEXT

**Last Updated**: August 23, 2025  
**Source of truth**: CapeControl / Capecraft project (synchronized with latest Heroku deployment logs)  
**Project Status**: Production Ready — Registration fixed, AI Security Suite deployed, Payment & Developer Earnings live  
**Current Version**: v663 (Heroku, deployed Aug 17, 2025) ✅ RUNNING
**Latest Update**: Heroku buildpack deployment enabled (Python 3.12, FastAPI 0.110.0)

---

## Executive Summary

This document captures the authoritative development and deployment context for the CapeControl / Capecraft project, incorporating `autorisen` features into the main CapeControl platform.

- **Production App**: `capecraft` (Heroku, version v663)
- **Staging Source**: `autorisen` repo, feature integration validated here
- **Goal**: Feature-flagged integration of `autorisen` modules into CapeControl, with validation gates before production promotion.

---

## 1. Company Information

- **Legal Entity**: Cape Craft Projects CC
- **Trading Name**: Cape Control
- **VAT Number**: 4270105119

---

## 2. Project Status & Versions

- **Production**: Heroku app `capecraft` (v663, deployed Aug 17, 2025, release `f8783ce4`)
- **Staging Source**: `autorisen` (used for integration testing)
-- **Backend**: FastAPI 0.110.0 on Python 3.12
- **Frontend**: React 18 + Vite, served by FastAPI
- **Stripe**: integration deployed and test-ready (Heroku-compatible at `stripe==7.7.0`)

---

## 3. Repositories & Structure

- **Production Repo**: `localstorm` / `capecontrol` (contains `backend/` and `client/`)
- **Staging Repo**: `autorisen` (features to be merged under `apps/autorisen` or `backend/app/routes/autorisen`)

---

## 4. Development Workflow

### Local Development (recommended)

Use the repository-local virtualenv and the helper script to start the backend reliably.

1. Create & activate a repo venv (if not present):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install backend dependencies:

```bash
pip install -r requirements.txt
pip install -r backend/requirements.txt
# Optional: pip install -r backend/requirements-dev.txt
```

3. Create a `.env` from the example (defaults will use SQLite):

```bash
cp .env.example .env
# By default the app uses: DATABASE_URL=sqlite:///./capecontrol.db
```

4. Start the backend using the repo helper (activates venv, sets PYTHONPATH, writes logs to /tmp):

```bash
./scripts/start-localhost-autorisen.sh 8000 localhost
# Health URL printed by the script: http://localhost:8000/api/health
tail -f /tmp/capecontrol_uvicorn.log
```

Notes:

- The project defaults to SQLite (`DATABASE_URL=sqlite:///./capecontrol.db`) so you can develop without Postgres or Docker.
- If you want Postgres, set `DATABASE_URL` in `.env` and run migrations (see `backend/migrations` or alembic scripts).

### Frontend (optional)

```bash
cd client
npm install
npm run dev
# Frontend typically served at http://localhost:3000
```

### CI / CD & Heroku

- GitHub Actions contains a consolidated workflow (`cicd.yml`) that builds and deploys to Heroku using buildpack-based deployment (not container-based).
- The workflow is configured to trigger on pushes to `main` and supports manual promotion to production via workflow_dispatch.
- Staging deploys are achieved by pushing the contents of `backend/` (with `Procfile`, `requirements.txt`, and `runtime.txt` at root) to the Heroku git remote.
- If you prefer staging-only deploys from a feature branch, update the workflow to trigger only on that branch and use manual promotion from `main` for production.
