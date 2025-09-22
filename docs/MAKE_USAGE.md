
# 🛠️ Make Commands — Usage Guide

This file is auto-generated from Makefile comments. Run `make help-md` to refresh.

## Quick Start

```bash
make up            # build + start all services
make logs          # tail all logs
make smoke         # quick health checks
make stg-release   # build → push (Docker Hub) → deploy (Heroku)
```

## Commands

- **be-logs** — Tail backend logs (Ctrl-C to exit)
- **clean** — Stop and remove containers + volumes (WIPE DB & MinIO data)
- **compose-config** — Print normalized compose (helps debug substitutions)
- **db-psql** — psql into local DB on host (:$(HOST_DB_PORT))
- **db-ready** — Wait until DB is ready to accept connections
- **deps** — Install dev dependencies
- **dh-build** — Build backend image for Docker Hub (tags: $(VERSION), latest)
- **dh-config** — Show Docker Hub config that will be used
- **dh-login** — Docker Hub login (interactive)
- **dh-push** — Push both tags to Docker Hub
- **dh-release** — Build + push in one step
- **dh-run** — Run the built image locally on :8000 (override ENV as needed)
- **doctor** — Validate compose + ports
- **down** — Stop and remove containers (keep volumes)
- **env-check** — Verify .env exists (create from .env.example if missing)
- **env-diagnose** — Show env that may affect compose ports
- **env-trim** — Trim trailing spaces/tabs/CR in .env
- **fe-logs** — Tail frontend logs
- **fe-open** — Open Frontend (Vite) in browser
- **help-md** — Generate docs/MAKE_USAGE.md from Makefile help comments
- **help** — Show this help
- **heroku-container-login** — Login to Heroku Container Registry
- **heroku-deploy-stg** — Deploy to Heroku staging using Docker image from this Makefile
- **heroku-docker-login-ci** — Docker login to Heroku registry using HEROKU_API_KEY (no browser)
- **heroku-ensure-image** — Ensure $(IMAGE):$(VERSION) exists locally (pull from Hub if needed)
- **heroku-login** — Open browser login (run OUTSIDE make if interactive blocks)
- **heroku-logs-stg** — Tail Heroku logs (staging)
- **heroku-migrate-stg** — Run DB migrations on staging (set HEROKU_MIGRATE_CMD)
- **heroku-pushimg-stg** — Push image to Heroku registry
- **heroku-release-stg** — Release container on Heroku
- **heroku-set-stack** — Ensure app stack is 'container' (one-time)
- **heroku-tag-stg** — Tag $(IMAGE):$(VERSION) -> $(HEROKU_IMAGE_WEB)
- **heroku-whoami** — Show currently logged-in Heroku account (or fail)
- **logs** — Tail all logs
- **migrate** — Run Alembic migrations inside backend (if alembic.ini exists)
- **net-clean** — Remove dangling compose network (ignore if missing)
- **open** — Open API docs in browser
- **ps** — Show running containers
- **rebuild** — Rebuild backend image without cache
- **reset** — Full reset (containers + volumes + network)
- **restart-hard** — Force-recreate backend (picks up env changes/bootstraps)
- **restart** — Restart backend service
- **sh** — Shell into backend container
- **smoke** — Quick health checks (backend /api/health, DB, frontend)
- **stg-open** — Open staging site in browser
- **stg-release** — Build to Docker Hub then deploy that image to Heroku staging
- **tools-down** — Stop MinIO tools (keeps data)
- **tools-up** — Start MinIO and seed default buckets (cc-static, cc-media)
- **up** — Build and start all services (detached)
- **venv** — Create .venv (python3)

---

### Notes

- Commands are documented inline in the Makefile using `##` comments.
- If something fails with env/ports, run `make doctor`.
