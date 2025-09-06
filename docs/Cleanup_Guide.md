# Project Cleanup Guide

Purpose: safely reduce clutter (logs, caches, build artifacts) without breaking builds, tests, or deploys.

Last updated: 2025-09-06

---

## Safety first

- Work on a branch. Commit before destructive actions.
- Don’t run destructive commands on production hosts.
- Back up any local databases you care about.

## Keep these files/folders

- App/infra: `Dockerfile`, `docker-compose.yml`, `Procfile`, `Makefile*`, `alembic.ini` (if used)
- Manifests/locks: `requirements*.txt`, `pyproject.toml`, `package.json`, `package-lock.json`
- Database migrations: `backend/migrations/`, `alembic/versions/` (if present)
- Docs and runbooks under `docs/`

## Common junk to remove (safe)

- Logs: `*.log` under repo
- Python caches: `__pycache__/`, `*.pyc`, `*.pyo`, `.pytest_cache/`
- Node/Vite caches: `node_modules/.cache/`, `.vite/`, `.cache/`
- Build artifacts: `dist/`, `build/`, `coverage/`, `htmlcov/`
- Editor cruft: `.DS_Store`, `Thumbs.db`, swap files (`*.swp`, `*~`)

Ensure these are in `.gitignore` (see snippet below).

## Minimal cleanup commands

Python (safe):

```bash
find . -type d -name "__pycache__" -prune -exec rm -rf {} +
find . -type f -name "*.py[co]" -delete
rm -rf .pytest_cache coverage htmlcov .mypy_cache || true
```

Node (safe to re-install):

```bash
rm -rf client/node_modules/.cache client/.vite || true
# Optional heavy cleanup (will require reinstall):
# rm -rf client/node_modules
# (then) cd client && npm ci
```

Frontend/backend build artifacts:

```bash
rm -rf client/dist client/build backend/.coverage || true
```

Docker (local only):

```bash
# Prune unused containers/images (CAUTION: removes dangling resources)
docker system prune -f
```

## .gitignore quick snippet

Add/verify these entries in `.gitignore`:

```gitignore
# Python
__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/

# Node / Vite
client/node_modules/
client/.vite/
client/node_modules/.cache/

# Builds & coverage
dist/
build/
coverage/
htmlcov/

# OS/editor
.DS_Store
Thumbs.db
*.swp
*~
```

## Verify nothing broke

- Install deps if you removed caches:
  - Backend: ensure Python deps installed per `backend/requirements.txt`
  - Frontend: `cd client && npm ci`
- Run quick smoke checks:
  - If available: `make smoke` or run health endpoint locally
- Commit cleanup changes in a single PR for easy review.

## Notes for this repo

- Large test DB artifacts (`test_*.db`) should generally remain untracked; keep only what tests require.
- CI and Heroku deploys read from `Dockerfile` (release target). Don’t remove it.
