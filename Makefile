# =============================================================================
# Autorisen / AutoLocal — Makefile (Docker Compose local dev)
# =============================================================================
.ONESHELL:
SHELL := /bin/bash
.DEFAULT_GOAL := help

# ---- Config ---------------------------------------------------------------
PROJECT_NAME ?= autorisen
COMPOSE       ?= docker compose
COMPOSE_FILE  ?= docker-compose.yml
BACKEND_SVC   ?= backend
FRONTEND_SVC  ?= frontend
DB_SVC        ?= db
PORT_API      ?= 8000
PORT_FE       ?= 3000
HOST_DB_PORT  ?= 5433

# Paths inside backend container
ALEMBIC_BIN   ?= /opt/venv/bin/alembic
BACKEND_DIR   ?= /app/backend

# ---- Helpers --------------------------------------------------------------
help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"}; /^[a-zA-Z0-9_\-]+:.*##/ {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ---- Compose lifecycle ----------------------------------------------------
up: ## Build and start all services (detached)
	$(COMPOSE) -f $(COMPOSE_FILE) up --build -d

build: ## Build containers without starting
	$(COMPOSE) -f $(COMPOSE_FILE) build

restart: ## Restart (recreate) all services
	$(COMPOSE) -f $(COMPOSE_FILE) up -d --force-recreate

stop: ## Stop containers (keep)
	$(COMPOSE) -f $(COMPOSE_FILE) stop

down: ## Stop and remove containers (keep volumes)
	$(COMPOSE) -f $(COMPOSE_FILE) down

clean: ## Stop and remove containers + volumes (WIPE DB)
	$(COMPOSE) -f $(COMPOSE_FILE) down -v

# ---- Logs & Open ----------------------------------------------------------
logs: ## Tail all logs
	$(COMPOSE) logs -f --tail=200

be-logs: ## Tail backend logs
	$(COMPOSE) logs -f $(BACKEND_SVC)

fe-logs: ## Tail frontend logs
	$(COMPOSE) logs -f $(FRONTEND_SVC)

open: ## Open Swagger UI
	xdg-open http://localhost:$(PORT_API)/docs || true

fe-open: ## Open Vite frontend
	xdg-open http://localhost:$(PORT_FE) || true

# ---- Database (Alembic) ---------------------------------------------------
migrate: ## Alembic upgrade head (run inside backend container)
	$(COMPOSE) exec -T $(BACKEND_SVC) sh -lc '\
		cd $(BACKEND_DIR) && $(ALEMBIC_BIN) -c alembic.ini upgrade head'

revision: ## Create new Alembic revision with message MSG="..."
	@if [ -z "$(MSG)" ]; then echo "Usage: make revision MSG=\"your message\""; exit 1; fi
	$(COMPOSE) exec -T $(BACKEND_SVC) sh -lc '\
		cd $(BACKEND_DIR) && $(ALEMBIC_BIN) -c alembic.ini revision --autogenerate -m "$(MSG)"'

rollback: ## Alembic downgrade by N steps (use N=1)
	@if [ -z "$(N)" ]; then echo "Usage: make rollback N=1"; exit 1; fi
	$(COMPOSE) exec -T $(BACKEND_SVC) sh -lc '\
		cd $(BACKEND_DIR) && $(ALEMBIC_BIN) -c alembic.ini downgrade -$(N)'

psql: ## Open psql to local DB (host: $(HOST_DB_PORT))
	PGPASSWORD=devpass psql -h localhost -p $(HOST_DB_PORT) -U devuser -d devdb

# ---- Diagnostics ----------------------------------------------------------
smoke: ## Quick health checks (backend + DB + frontend)
	@echo "Checking backend /api/health ..." && curl -fsS http://localhost:$(PORT_API)/api/health || true
	@echo "Checking frontend root ..." && curl -fsS http://localhost:$(PORT_FE)/ || true
	@echo "DB containers:" && $(COMPOSE) ps

doctor: ## Print compose config and port checks
	$(COMPOSE) config
	@echo "Ports in use:"; ss -ltnp | grep -E ":($(PORT_API)|$(PORT_FE)|$(HOST_DB_PORT))" || true

# ---- Heroku (staging: autorisen) -----------------------------------------
heroku-login: ## Log in to Heroku Container Registry
	heroku container:login

heroku-deploy-stg: ## Build & push web image, release to autorisen
	# requires: heroku login, app exists, stack=container
	heroku container:push web -a autorisen
	heroku container:release web -a autorisen

heroku-logs: ## Tail Heroku logs for autorisen
	heroku logs -t -a autorisen

# ---- Docker Hub (optional) -----------------------------------------------
dh-release: ## Build & push to Docker Hub (set IMG=repo/name:tag)
	@if [ -z "$(IMG)" ]; then echo "Usage: make dh-release IMG=user/repo:tag"; exit 1; fi
	docker build -t $(IMG) .
	docker push $(IMG)

# ---- Convenience ----------------------------------------------------------
fe-shell: ## Open a shell in the frontend container
	$(COMPOSE) exec $(FRONTEND_SVC) sh

be-shell: ## Open a shell in the backend container
	$(COMPOSE) exec $(BACKEND_SVC) sh

# Run alembic upgrade against a temp DB URL (used in CI) or local DATABASE_URL
migrate:
	@/opt/venv/bin/alembic -c backend/alembic.ini upgrade head

# Dry-run (generate SQL only) – safe in CI
migrate-dry:
	@/opt/venv/bin/alembic -c backend/alembic.ini upgrade head --sql >/dev/null

# Detect model/schema drift (fails if new autogen wants to create a file)
check-drift:
	@tmpdir=$$(mktemp -d); \
	out="$$tmpdir/auto.py"; \
	/opt/venv/bin/alembic -c backend/alembic.ini revision --autogenerate -m "drift-check" -s "$$tmpdir" >/dev/null; \
	if [ -s "$$out" ] || ls "$$tmpdir"/*.py >/dev/null 2>&1; then \
	  echo "❌ Drift detected: models differ from migrations."; \
	  rm -rf "$$tmpdir"; \
	  exit 1; \
	else \
	  echo "✅ No drift."; \
	  rm -rf "$$tmpdir"; \
	fi
plan-snapshot:
	@python3 tools/snapshot_plan.py && echo "Plan snapshot complete."
