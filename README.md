# autorisen 250826B

Development site for Cape Control 250817

# autorisen

Development site for Cape Control (Cape Control / Autorisen)

## Overview

- Backend: FastAPI (Python 3.11+), Gunicorn + Uvicorn worker
- Frontend: React / Vite (client/)
- Database: PostgreSQL in production (Heroku Postgres), SQLite fine for quick local dev

## Quickstart (local)

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

## Heroku notes

- The Procfile uses `PYTHONPATH=backend` so Heroku starts the app as `gunicorn app.main:app -k uvicorn.workers.UvicornWorker`.
- Heroku reads top-level `requirements.txt` during build. The repo delegates backend packages via `-r backend/requirements.txt` in the top-level requirements file — keep `backend/requirements.txt` authoritative for backend runtime packages.
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

- Backend: FastAPI 0.104.1 (Python 3.11)
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
- Recommended Stripe pin for Heroku compatibility: `stripe==7.7.0`.

If you'd like, I can:

- Produce and commit `docs/openapi_baseline.json` (exported from production/staging) so CI diffs will run against a baseline.
- Add a short 'Rollback' section to `docs/Release Runbook.md` with Heroku restore commands.
