# Deployment Guide 2025 – Autorisen
A step-by-step runbook for staging→production with parity and safe rollbacks.

## 1) Parity with Production
- Match **Python runtime** (`runtime.txt`) to production.
- Freeze **requirements** from production and commit as `requirements.txt`.
- Verify **buildpacks** (Python only unless needed).
- Sync critical **config vars** (without secrets) between staging and prod.

## 2) CI/CD (GitHub Actions)
- Workflows:
  - `deploy-staging.yml` – on push to `main`, build & deploy to Heroku staging.
  - `deploy.yml` – manual `workflow_dispatch` to production after approvals.
- Gates:
  - Lint + type check (mypy)
  - Unit tests with coverage threshold
  - Smoke test: `GET /health`

## 3) Promotion Strategy
- Prefer **config parity** + **image parity** where possible.
- If using slug promotion, ensure slug sizes/runtimes align.
- Manual prod deploy only after staging passes checks.

## 4) Observability & Alerts
- Verify logs, health endpoint, and analytics counters post-deploy.
- Rollback procedure in `DEPLOYMENT.md`.

## 5) Common Pitfalls
- Missing env vars (JWT secrets, DB URL)
- Alembic not applied
- Worker count too high for Heroku dyno
