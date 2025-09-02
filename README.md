# autorisen

[![Docker Pulls](https://img.shields.io/docker/pulls/stinkie/autorisen?style=flat-square)](https://hub.docker.com/r/stinkie/autorisen) [![Docker Image Version](https://img.shields.io/docker/v/stinkie/autorisen?label=docker%20hub&style=flat-square)](https://hub.docker.com/r/stinkie/autorisen)

Development site for Cape Control with PostgreSQL development environment.

## Overview

- **Backend**: FastAPI (Python 3.11+), Gunicorn + Uvicorn worker
- **Frontend**: React + Vite (in `client/`)
- **Database**: PostgreSQL in production (Heroku Postgres); SQLite fallback for quick dev

## Quick setup

### Option A — PostgreSQL (recommended)

1. Prerequisites: PostgreSQL 16+ installed locally.

1. Automated database setup:

```bash
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

1. Start development:

```bash
# Backend
export PYTHONPATH=backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (separate terminal)
cd client
npm install
npm run dev
```

### Option B — SQLite (quick)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
pip install -r backend/requirements.txt
# Optional: install dev/optional deps
pip install -r backend/requirements-dev.txt
```

Set environment variables:

```bash
export DATABASE_URL=sqlite:///./dev.db
export STRIPE_SECRET_KEY=sk_test_...
```

Run backend:

```bash
export PYTHONPATH=backend
uvicorn app.main:app --reload
```

## Local PostgreSQL

**Connection details**

- Host: `localhost`
- Port: `5432`
- Database: `autorisen_local`
- Username: `vscode`
- Password: `123456`

**Useful commands**

```bash
PGPASSWORD=123456 psql -h localhost -U vscode -d autorisen_local
python ./scripts/dummy_register.py
```

## Heroku deployment options

The project supports both buildpack-based and container-based Heroku deployments.

- Buildpack deploys (classic): keep `Procfile`, `requirements.txt` and `runtime.txt` at the repository root. Heroku will use the `Procfile` to start the web process.

- Container Registry deploys: build and push an image to `registry.heroku.com/<app>/web` and run `heroku container:release web -a <app>`. When using container deploys the final image must start a process that binds to `$PORT`.

If you see R10 (boot timeout), verify the container image binds to `$PORT` (the Vite dev server listening on port 3000 is a common cause).

## Notes

- Canonical FastAPI app: `backend/app/main.py` (import path: `app.main:app`).
- Optional SDKs (e.g., `stripe`) are deferred to runtime; add `stripe` to `backend/requirements.txt` to enable payments.
- CI contains import-sanity checks and OpenAPI diffing in `.github/workflows/` and `scripts/`.

---

If you'd like, I can also:

- Add `docs/openapi_baseline.json` (exported from production) for CI diffs
- Add a Docker Hub / Actions badge
- Add a Makefile target for local `docker build --target release` and push
