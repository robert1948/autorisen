# Development Context

This note captures the expected local environment defaults, helpful make targets, and smoke checks so onboarding stays quick.

## Services & Ports

- **Backend API**: `http://localhost:8000`
- **Frontend (Vite)**: `http://localhost:3000`
- **Postgres**: `localhost:5433` (`devuser` / `devpass` / `devdb`)
- **Redis**: `localhost:6379`

## Bootstrap Commands

```bash
make venv           # create local virtualenv (.venv)
make install        # install backend dependencies into venv
make plan-open      # open canonical plan CSV + doc
make plan-validate  # lint plan CSV headers/status values
make agents-test     # pytest coverage for local agent adapters
make agents-validate  # schema check for agent registry entries
make agents-run name=<slug> task="..."  # adapter readiness; use --env=stg for staging configs
```

### Running the stack (Docker Compose)

```bash
make docker-build         # build backend image (autorisen:local)
make docker-run           # run backend image exposing port 8000
make heroku-deploy-stg    # push/release image to autorisen Heroku app
```

## Smoke Checks

- Local: `./scripts/smoke_check.sh http://localhost:8000`
- GitHub Actions: `Smoke` workflow (runs on push to `main`,`develop`, plus PRs)
- Staging: `heroku open -a autorisen` after deploy and ensure `/api/health` returns `{ "status": "ok" }`

## CI & Automation

- **PR Checks**: `.github/workflows/ci-pr.yml` (Python 3.12 lint/test + optional frontend hooks)
- **Main Deploy**: `.github/workflows/main-deploy.yml` builds/pushes Heroku image and runs smoke against staging.
- **Agents Validate**: `.github/workflows/agents-validate.yml` runs the registry schema validator whenever agent specs, tool
 configs, or helper scripts change.
- **Plan Sync**: `Plan → Issues Sync` keeps `data/plan.csv` aligned with GitHub issues; the team runs `make plan-validate`
 before commits.
- **Nightly Snapshot**: `Snapshot Project Plan` stores daily copies under `snapshots/` with PRs for audit history.

## Useful Scripts

- `scripts/fetch_assets.sh` – pull favicons/assets from S3
- `scripts/context_snapshot.sh` – generate `context/latest.txt` for Codex tasks
- `scripts/rollback_heroku.sh` – `./scripts/rollback_heroku.sh <app> <release>` (Heroku rollback)
- `scripts/agents_validate.py` – shared schema validator invoked by `make agents-validate`
- `scripts/agents_run.py` – stub runner used by `make agents-run`

Keep this doc in sync whenever ports, scripts, or workflows change—it is the quick reference for the next teammate.
