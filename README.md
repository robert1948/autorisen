# autorisen

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

## Troubleshooting

- Dyno crashes at boot with ModuleNotFoundError: inspect the import stack in Heroku logs. If a package is missing, either add it to `backend/requirements.txt` or wrap the import in try/except.
- Useful local checks:

```bash
# sanity import
export PYTHONPATH=backend
python -c "import app; print('import ok')"

# byte-compile files to catch syntax errors
python -m py_compile backend/app/services/developer_earnings_service.py backend/app/services/stripe_service.py
```

## Contributing

- Follow the code style in the repo. Run tests where available and add import-sanity checks to PRs when touching startup modules.

## Contact / Notes

- Repo owner: robert1948 (see GitHub repo for issues)
