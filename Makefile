PY ?= python3
# =============================================================================
# AutoLocal — Makefile (Docker Compose local dev)
# -----------------------------------------------------------------------------
# Usage:
#   make                 # help
#   make up              # build + start all services
#   make down            # stop & remove containers (keep volumes)
#   make clean           # stop & remove containers + volumes (WIPE DB/MinIO)
#   make be-logs         # tail backend logs (Ctrl-C to exit)
#   make fe-logs         # tail frontend logs
#   make open            # open Swagger docs
#   make fe-open         # open Vite frontend
#   make migrate         # alembic upgrade heads (multi-branch friendly)
#   make tools-up        # start MinIO + seed buckets
#   make tools-down      # stop MinIO
#   make doctor          # validate compose + ports and print config
#   make dh-release      # build + push image to Docker Hub
# =============================================================================

.ONESHELL:
SHELL := /bin/bash
.DEFAULT_GOAL := help

# ---- Compose runners ---------------------------------------------------------
COMPOSE       ?= docker compose
# Unset port envs so compose mappings like "HOST:CONTAINER" don't get mutated
COMPOSE_SAFE  ?= env -u HOST_DB_PORT -u HOST_HTTP_PORT -u APP_PORT docker compose

# ---- Services ----------------------------------------------------------------
SVC_BACKEND   ?= backend
SVC_DB        ?= db
SVC_FRONTEND  ?= frontend
SVC_MINIO     ?= minio
SVC_REDIS     ?= redis

# ---- Defaults (keep in sync with docker-compose.yml) -------------------------
HOST_HTTP_PORT ?= 8000
HOST_DB_PORT   ?= 5433

# ---- Paths (container) -------------------------------------------------------
# Compose mounts ./backend -> /app/backend ; Uvicorn app is app.main:app
BACKEND_DIR ?= /app/backend
ALEMBIC_BIN ?= /opt/venv/bin/alembic
UVICORN_BIN ?= /opt/venv/bin/uvicorn

# ---- Pretty output helpers ---------------------------------------------------
define OK
	echo -e "\033[1;32m✔\033[0m" $(1)
endef
define WARN
	echo -e "\033[1;33m⚠\033[0m" $(1)
endef
define ERR
	echo -e "\033[1;31m✖\033[0m" $(1)
endef

# ---- Load .env into make (simple KEY=VAL, no quotes) -------------------------
ifneq (,$(wildcard .env))
  include .env
  export $(shell sed -n 's/^\([A-Za-z_][A-Za-z0-9_]*\)=.*/\1/p' .env)
endif

# ---- Phony -------------------------------------------------------------------
.PHONY: help up down clean restart restart-hard rebuild ps be-logs fe-logs logs \
	sh db-psql db-ready migrate tools-up tools-down open fe-open smoke \
	compose-config doctor dotenv-check env-trim env-diagnose net-clean reset \
	dh-login dh-build dh-push dh-release dh-run dh-config auth-smoke \
	heroku-whoami heroku-login heroku-container-login heroku-set-stack \
	heroku-tag-stg heroku-pushimg-stg heroku-release-stg heroku-migrate-stg \
	heroku-deploy-stg stg-release heroku-docker-login-ci heroku-ensure-image \
	venv deps heroku-logs-stg stg-open help-md env-init env-check mail-test \
	heroku-stg-help heroku-stg-preview heroku-stg-apply

# ---- Help --------------------------------------------------------------------
help: ## Show this help
	@API_PORT=$${HOST_HTTP_PORT:-$(HOST_HTTP_PORT)}; \
	 DB_PORT=$${HOST_DB_PORT:-$(HOST_DB_PORT)}; \
	 FE_PORT=3000; \
	 APP_URL="http://localhost:$$API_PORT"; \
	 FE_URL="http://localhost:$$FE_PORT"; \
	 DB_URL="postgres://$${POSTGRES_USER:-devuser}:$${POSTGRES_PASSWORD:-devpass}@localhost:$$DB_PORT/$${POSTGRES_DB:-devdb}"; \
	 echo "════════════════════════════════════════════════════════════"; \
	 echo " AutoLocal — Local Dev Stack (Docker Compose)"; \
	 echo "════════════════════════════════════════════════════════════"; \
	 echo " API        : $$APP_URL  (/docs, /alive)"; \
	 echo " Frontend   : $$FE_URL"; \
	 echo " Database   : $$DB_URL"; \
	 echo " Compose    : $(COMPOSE)"; \
	 echo " Project    : $$(basename $$PWD)   Git: $(GIT_SHA)"; \
	 echo ""; \
	 echo " Quick start:"; \
	 echo "   make up        # build + start all services"; \
	 echo "   make be-logs   # tail backend logs"; \
	 echo "   make fe-logs   # tail frontend logs"; \
	 echo "   make smoke     # quick health checks"; \
	 echo "   make migrate   # alembic upgrade heads"; \
	 echo "   make down      # stop containers (keep volumes)"; \
	 echo ""; \
	 echo " Commands:"; \
	 grep -E '^[a-zA-Z0-9_\-]+:.*?##' $(firstword $(MAKEFILE_LIST)) \
	   | sed -E 's/:.*?##/: /' | sort

# ---- Env utilities -----------------------------------------------------------
dotenv-check: ## Verify .env exists (create from .env.example if missing)
	@if [ ! -f .env ] && [ -f .env.example ]; then cp .env.example .env && $(call WARN,"Created .env from .env.example (edit secrets)"); fi
	@if [ ! -f .env ]; then $(call WARN,"No .env found (defaults will be used)"); fi

env-trim: ## Trim trailing spaces/tabs/CR in .env
	@if [ -f .env ]; then sed -i -e 's/[ \t\r]*$$//' .env && $(call OK,"Trimmed whitespace in .env"); fi

env-diagnose: ## Show env that may affect compose ports
	@echo "HOST_HTTP_PORT=$${HOST_HTTP_PORT:-$(HOST_HTTP_PORT)}"
	@echo "HOST_DB_PORT=$${HOST_DB_PORT:-$(HOST_DB_PORT)}"
	@echo "APP_PORT=$${APP_PORT:-8000}"

# ---- Compose helpers ----------------------------------------------------------
compose-config: ## Print normalized compose (helps debug substitutions)
	$(COMPOSE_SAFE) config

doctor: env-trim ## Validate compose + ports
	@if [ -f .env ]; then \
	  if ! grep -Eq '^(HOST_HTTP_PORT|HOST_DB_PORT|APP_PORT)=[0-9]+$$' .env; then \
	    $(call WARN,"Check numeric port lines in .env (HOST_HTTP_PORT/APP_PORT/HOST_DB_PORT)"); \
	  fi; \
	fi
	@if $(COMPOSE_SAFE) config >/dev/null; then $(call OK,"compose parse ok"); else $(call ERR,"compose parse failed"); exit 2; fi

# ---- Lifecycle ---------------------------------------------------------------
up: dotenv-check ## Build and start all services (detached)
	$(COMPOSE_SAFE) up --build -d
	$(call OK,"Stack is up -> http://localhost:$(HOST_HTTP_PORT)")

down: ## Stop and remove containers (keep volumes)
	$(COMPOSE_SAFE) --profile tools down || true
	$(COMPOSE_SAFE) down || true
	$(MAKE) net-clean
	$(call OK,"Containers stopped")

clean: ## Stop and remove containers + volumes (WIPE DB & MinIO data)
	$(COMPOSE_SAFE) --profile tools down -v || true
	$(COMPOSE_SAFE) down -v || true
	$(MAKE) net-clean
	$(call WARN,"All volumes removed (database wiped)")

net-clean: ## Remove dangling compose network (ignore if missing)
	- docker network rm autolocal_default 2>/dev/null || true

reset: ## Full reset (containers + volumes + network)
	$(MAKE) clean

restart: ## Restart backend service
	$(COMPOSE_SAFE) restart $(SVC_BACKEND)
	-$(COMPOSE_SAFE) logs -f $(SVC_BACKEND)

restart-hard: ## Force-recreate backend (picks up env changes/bootstraps)
	$(COMPOSE_SAFE) up -d --force-recreate $(SVC_BACKEND)
	-$(COMPOSE_SAFE) logs -f $(SVC_BACKEND)

rebuild: ## Rebuild backend image without cache
	$(COMPOSE) build --no-cache $(SVC_BACKEND)

ps: ## Show running containers
	$(COMPOSE) ps

# ---- Developer shortcuts ----------------------------------------------------
dev-up: dotenv-check ## Build and start backend + db + redis + frontend (detached)
	@echo "Starting backend + db + redis + frontend (ports: $$HOST_HTTP_PORT, $$HOST_DB_PORT)"
	$(COMPOSE_SAFE) up --build -d $(SVC_DB) $(SVC_REDIS) $(SVC_BACKEND) $(SVC_FRONTEND)
	$(call OK,"Dev stack is up -> http://localhost:$(HOST_HTTP_PORT)")

dev-down: ## Stop dev stack (keep volumes)
	$(COMPOSE_SAFE) down || true
	$(call OK,"Dev stack stopped")

FE_DEV_PORT ?= 3001
fe-local: ## Run frontend locally (pnpm preferred, falls back to npm) on port $(FE_DEV_PORT)
	@echo "Starting frontend dev server on http://localhost:$(FE_DEV_PORT) (API -> http://localhost:$${HOST_HTTP_PORT:-$(HOST_HTTP_PORT)})"; \
	if command -v pnpm >/dev/null 2>&1; then \
		echo "Using pnpm"; VITE_API_BASE="http://localhost:$${HOST_HTTP_PORT:-$(HOST_HTTP_PORT)}" pnpm dev -- --host 0.0.0.0 --port $(FE_DEV_PORT); \
	else \
		echo "pnpm not found, falling back to npm"; VITE_API_BASE="http://localhost:$${HOST_HTTP_PORT:-$(HOST_HTTP_PORT)}" npm run dev -- --host 0.0.0.0 --port $(FE_DEV_PORT); \
	fi

smoke-local: ## Run local smoke tests (auth flow + /alive). Non-fatal on errors.
	@$(MAKE) smoke || true

heroku-stg-help: ## Print recommended Heroku staging steps (safe copy-paste checklist)
	@echo "Heroku staging checklist (manual steps):"; \
	echo " 1) Ensure you're logged in: heroku auth:whoami"; \
	echo " 2) Create app if missing: heroku create autorisen"; \
	echo " 3) Provision addons: heroku addons:create heroku-postgresql:hobby-dev -a autorisen"; \
	echo "    and a Redis provider if needed (example: Heroku Redis)"; \
	echo " 4) Set config vars from backend/.env.development (use heroku config:set KEY=VAL -a autorisen)"; \
	echo " 5) Build & push image: make heroku-deploy-stg"; \
	echo " 6) Run migrations: make heroku-migrate-stg (ensure HEROKU_MIGRATE_CMD is set)"; \
	echo " 7) Smoke test staging: curl -fsS https://autorisen.herokuapp.com/alive";

# ---- Logs / Shell ------------------------------------------------------------
be-logs: ## Tail backend logs (Ctrl-C to exit)
	-$(COMPOSE_SAFE) logs -f $(SVC_BACKEND)

fe-logs: ## Tail frontend logs
	-$(COMPOSE_SAFE) logs -f $(SVC_FRONTEND) || true

logs: ## Tail all logs
	-$(COMPOSE_SAFE) logs -f

sh: ## Shell into backend container (POSIX shell; -T for non-interactive safe)
	$(COMPOSE) exec -T $(SVC_BACKEND) sh -lc 'exec sh' || $(COMPOSE) run --rm $(SVC_BACKEND) sh -lc 'exec sh'

# ---- DB ----------------------------------------------------------------------
db-psql: ## psql into local DB on host (:$(HOST_DB_PORT))
	@psql -h localhost -p $(HOST_DB_PORT) -U devuser -d devdb || \
	 psql -h localhost -p $(HOST_DB_PORT) -U $$(whoami) -d postgres

db-ready: ## Wait until DB is ready to accept connections
	@until pg_isready -h localhost -p $(HOST_DB_PORT) >/dev/null 2>&1; do \
		echo "waiting for postgres on :$(HOST_DB_PORT)..."; sleep 1; \
	done
	$(call OK,"Postgres is ready on :$(HOST_DB_PORT)")

migrate: ## Run Alembic migrations inside backend (upgrade HEADS; supports branches)
	@$(COMPOSE) exec -T $(SVC_BACKEND) sh -lc 'set -e; \
	  for d in $(BACKEND_DIR) /app; do \
	    if [ -f "$$d/alembic.ini" ]; then cd "$$d" && $(ALEMBIC_BIN) -c alembic.ini upgrade heads && exit 0; fi; \
	  done; \
	  echo "alembic.ini not found; skipping"; \
	  exit 0'
	$(call OK,"Alembic migrations applied (heads)")

# ---- Tools (MinIO) -----------------------------------------------------------
tools-up: ## Start MinIO and seed default buckets (cc-static, cc-media)
	$(COMPOSE_SAFE) --profile tools up -d $(SVC_MINIO)
	$(COMPOSE_SAFE) --profile tools run --rm minio-mc || $(call WARN,"Bucket seeding skipped")
	$(call OK,"MinIO ready -> http://localhost:9001")

tools-down: ## Stop MinIO tools (keeps data)
	$(COMPOSE_SAFE) --profile tools down || true

# ---- Convenience -------------------------------------------------------------
open: ## Open API docs in browser
	@PORT=$${HOST_HTTP_PORT:-$(HOST_HTTP_PORT)}; \
	xdg-open "http://localhost:$$PORT/docs" >/dev/null 2>&1 || open "http://localhost:$$PORT/docs"

fe-open: ## Open Frontend (Vite) in browser
	@xdg-open "http://localhost:3000" >/dev/null 2>&1 || open "http://localhost:3000"

smoke: ## Quick health checks (backend /alive, DB, frontend)
	@curl -fsS "http://localhost:$${HOST_HTTP_PORT:-$(HOST_HTTP_PORT)}/alive" >/dev/null && \
	$(call OK,"Backend /alive OK") || $(call ERR,"Backend /alive FAIL")
	@pg_isready -h localhost -p $${HOST_DB_PORT:-$(HOST_DB_PORT)} >/dev/null 2>&1 && \
	$(call OK,"Postgres ready on :$${HOST_DB_PORT:-$(HOST_DB_PORT)}") || $(call ERR,"Postgres not ready")
	@if curl -fsS "http://localhost:3000" >/dev/null 2>&1; then \
	$(call OK,"Frontend OK at :3000"); \
	elif curl -fsS "http://localhost:5173" >/dev/null 2>&1; then \
	$(call OK,"Frontend OK at :5173 (container internal `5173`, host `3000`)"); \
	else \
	$(call WARN,"Frontend not running at :3000 or :5173 (container internal `5173`, host `3000`)"); \
	fi

auth-smoke: ## Register → Login → Me using curl+jq (idempotent)
	@set -e; API="http://localhost:$${HOST_HTTP_PORT:-$(HOST_HTTP_PORT)}"; \
	 EMAIL="demo@example.com"; PASS="demo12345"; \
	 curl -s -X POST "$$API/api/auth/register" -H "Content-Type: application/json" \
	   -d "$$(jq -n --arg e "$$EMAIL" --arg p "$$PASS" --arg n "Demo" '{email:$$e,password:$$p,name:$$n}')" >/dev/null || true; \
	 TOKEN=$$(curl -s -X POST "$$API/api/auth/login" -H "Content-Type: application/json" \
	   -d "$$(jq -n --arg e "$$EMAIL" --arg p "$$PASS" '{email:$$e,password:$$p}')" | jq -r .access_token); \
	 test -n "$$TOKEN"; \
	 curl -fsS "$$API/api/auth/me" -H "Authorization: Bearer $$TOKEN" >/dev/null; \
	 $(call OK,"Auth flow OK")

# === Docker Hub release =======================================================
DOCKERHUB_USER   ?= stinkie
DOCKERHUB_REPO   ?= autorisen
PLATFORM         ?= linux/amd64

DATE_UTC  := $(shell date -u +%Y%m%d-%H%M)
GIT_SHA   := $(shell git rev-parse --short HEAD 2>/dev/null || echo dev)
VERSION   := $(if $(strip $(DOCKERHUB_VERSION)),$(strip $(DOCKERHUB_VERSION)),$(DATE_UTC)-$(GIT_SHA))

IMAGE      := $(DOCKERHUB_USER)/$(DOCKERHUB_REPO)

.PHONY: dh-config dh-login dh-build dh-push dh-release dh-run
dh-config: ## Show Docker Hub config that will be used
	@echo "IMAGE    : $(IMAGE)"
	@echo "VERSION  : $(VERSION)"
	@echo "PLATFORM : $(PLATFORM)"

dh-login: ## Docker Hub login (interactive)
	@docker login -u $(DOCKERHUB_USER)

dh-build: ## Build backend image for Docker Hub (tags: $(VERSION), latest)
	@echo "Building $(IMAGE):$(VERSION) (platform $(PLATFORM))..."
	docker build --platform=$(PLATFORM) \
	  -f backend/Dockerfile --target backend \
	  -t $(IMAGE):$(VERSION) -t $(IMAGE):latest \
	  .

dh-push: ## Push both tags to Docker Hub
	docker push $(IMAGE):$(VERSION)
	docker push $(IMAGE):latest
	@echo "Pushed: $(IMAGE):$(VERSION) and :latest"

dh-release: dh-build dh-push ## Build + push in one step
	@echo "✅ Docker Hub updated → https://hub.docker.com/r/$(DOCKERHUB_USER)/$(DOCKERHUB_REPO)/tags"

dh-run: ## Run the built image locally on :8000 (override ENV as needed)
	docker run --rm -e PORT=8000 -p 8000:8000 $(IMAGE):$(VERSION)

# === Heroku container deploy (staging → autorisen) ============================
HEROKU_APP_STG        ?= autorisen
HEROKU_PROC_TYPE      ?= web
HEROKU_IMAGE_WEB      := registry.heroku.com/$(HEROKU_APP_STG)/$(HEROKU_PROC_TYPE)
HEROKU_MIGRATE_CMD    ?=

heroku-whoami: ## Show currently logged-in Heroku account (or fail)
	@heroku auth:whoami

heroku-login: ## Open browser login (run OUTSIDE make if interactive blocks)
	@heroku auth:whoami >/dev/null 2>&1 || heroku login

heroku-container-login: ## Login to Heroku Container Registry
	@heroku container:login

heroku-set-stack: ## Ensure app stack is 'container' (one-time)
	@heroku stack:set container -a $(HEROKU_APP_STG) || true

heroku-tag-stg: heroku-ensure-image ## Tag $(IMAGE):$(VERSION) -> $(HEROKU_IMAGE_WEB)
	@docker tag $(IMAGE):$(VERSION) $(HEROKU_IMAGE_WEB)
	@$(call OK,"Tagged $(IMAGE):$(VERSION) -> $(HEROKU_IMAGE_WEB)")

heroku-pushimg-stg: heroku-container-login heroku-tag-stg ## Push image to Heroku registry
	@docker push $(HEROKU_IMAGE_WEB)
	@$(call OK,"Pushed image to $(HEROKU_IMAGE_WEB)")

heroku-release-stg: ## Release container on Heroku
	@heroku container:release $(HEROKU_PROC_TYPE) -a $(HEROKU_APP_STG)
	@$(call OK,"Released $(HEROKU_PROC_TYPE) on $(HEROKU_APP_STG)")

heroku-migrate-stg: ## Run DB migrations on staging (set HEROKU_MIGRATE_CMD)
	@if [ -n "$(HEROKU_MIGRATE_CMD)" ]; then \
	  echo "Running migrations: $(HEROKU_MIGRATE_CMD)"; \
	  heroku run -a $(HEROKU_APP_STG) -- $(HEROKU_MIGRATE_CMD) || true; \
	else \
	  echo "No HEROKU_MIGRATE_CMD set; skipping migrations"; \
	fi

heroku-deploy-stg: ## Deploy to Heroku staging using Docker image from this Makefile
	$(MAKE) dh-config
	$(MAKE) heroku-set-stack
	$(MAKE) heroku-pushimg-stg
	$(MAKE) heroku-release-stg
	$(MAKE) heroku-migrate-stg
	@echo "✅ Deployed to staging: https://$(HEROKU_APP_STG).herokuapp.com"

stg-release: ## Build to Docker Hub then deploy that image to Heroku staging
	$(MAKE) dh-release
	$(MAKE) heroku-deploy-stg

heroku-docker-login-ci: ## Docker login to Heroku registry using HEROKU_API_KEY (no browser)
	@if [ -z "$$HEROKU_API_KEY" ]; then \
	  echo "HEROKU_API_KEY not set; export it to use heroku-docker-login-ci" && exit 1; \
	fi
	@echo "$$HEROKU_API_KEY" | docker login --username=_ --password-stdin registry.heroku.com
	$(call OK,"Docker logged into registry.heroku.com via HEROKU_API_KEY")

heroku-ensure-image: ## Ensure $(IMAGE):$(VERSION) exists locally (pull from Hub if needed)
	@echo "Checking for $(IMAGE):$(VERSION) locally...";
	@if docker image inspect $(IMAGE):$(VERSION) >/dev/null 2>&1; then \
		echo "Found image $(IMAGE):$(VERSION)"; \
	elif docker pull $(IMAGE):$(VERSION) >/dev/null 2>&1; then \
		echo "Pulled image $(IMAGE):$(VERSION) from registry"; \
	else \
		echo "Image $(IMAGE):$(VERSION) not found remotely; building locally..."; \
		$(MAKE) dh-build; \
	fi

# ---- Heroku staging automation helpers ------------------------------------
HEROKU_DB_ADDON ?= heroku-postgresql:hobby-dev
HEROKU_REDIS_ADDON ?= heroku-redis:hobby-dev

heroku-stg-preview: ## Preview Heroku staging actions (no remote changes)
	@echo "Heroku staging preview for app: $(HEROKU_APP_STG)"
	@echo "Will ensure stack=container, ensure container registry login, and then push/release image (if confirmed)"
	@echo "-- Detected image: $(IMAGE):$(VERSION)"
	@echo "-- Heroku staging app: $(HEROKU_APP_STG)"
	@echo "-- Addons to provision: $(HEROKU_DB_ADDON) $(HEROKU_REDIS_ADDON)"
	@echo "To actually perform these actions run: make heroku-stg-apply CONFIRM=yes"

heroku-stg-apply: heroku-ensure-image ## Apply Heroku staging flow (destructive: will create app/addons/config - requires CONFIRM=yes)
	@if [ "$(CONFIRM)" != "yes" ]; then \
		echo "CONFIRM not set to 'yes' — aborting (dry-run)."; \
		echo "Run 'make heroku-stg-preview' to view planned actions, then 'make heroku-stg-apply CONFIRM=yes' to apply."; \
		exit 2; \
	fi
	@echo "Applying Heroku staging flow to app: $(HEROKU_APP_STG)";
	@heroku auth:whoami || (echo "Not logged into Heroku. Run 'heroku login' first" && exit 3)
	@heroku apps:info -a $(HEROKU_APP_STG) >/dev/null 2>&1 || (echo "Creating Heroku app $(HEROKU_APP_STG)" && heroku create $(HEROKU_APP_STG))
	@echo "NOTE: This Make target will NOT automatically provision addons to avoid plan mismatches.";
	@echo "If you need DB/Redis on Heroku, run these commands manually (review plan names first):";
	@echo "  heroku addons:create $(HEROKU_DB_ADDON) -a $(HEROKU_APP_STG)";
	@echo "  heroku addons:create $(HEROKU_REDIS_ADDON) -a $(HEROKU_APP_STG)";
	@echo "Continuing without auto-provisioning addons...";
	@echo "Previewing config vars from backend/.env.development (sanitized)."; \
	set -e; if [ -f backend/.env.development ]; then echo "---- backend/.env.development vars (preview) ----"; \
		grep -v '^\s*#' backend/.env.development | sed -E 's/(PASSWORD|SECRET|TOKEN|KEY|AWS|PGPASSWORD)=.*/\1=<REDACTED>/I' || true; \
		echo "---- end preview ----"; else echo "No backend/.env.development found; skipping preview"; fi
	@echo "Setting non-secret config vars from backend/.env.development to Heroku (only safe keys will be set)";
	@set -e; if [ -f backend/.env.development ]; then \
		echo "---- backend/.env.development -> heroku config (preview) ----"; \
		while IFS= read -r line || [ -n "$$line" ]; do \
			line=$$(printf '%s' "$$line" | sed -e 's/^[[:space:]]*//;s/[[:space:]]*$$//'); \
			[ -z "$$line" ] && continue; \
			case "$$line" in \#*) continue ;; esac; \
			key=$$(printf '%s' "$$line" | cut -d= -f1); \
			val=$$(printf '%s' "$$line" | sed -n 's/^[^=]*=//p'); \
			case "$$key" in \
				*PASSWORD*|*SECRET*|*TOKEN*|*KEY*|*AWS*|*PGPASSWORD*) \
					echo "SKIP (secret/empty): $$key" ;; \
				*) \
					cmd="heroku config:set \"$$key=$$val\" -a $(HEROKU_APP_STG)"; \
					if [ "$${APPLY_CONFIG:-no}" = "yes" ]; then \
						echo "APPLY: $$cmd"; eval $$cmd; \
					else \
						echo "DRY: $$cmd"; \
					fi ;; \
			esac; \
		done < backend/.env.development; \
		echo "---- end preview ----"; \
	else \
		echo "backend/.env.development missing; please set config vars manually"; \
	fi
	@echo "Pushing & releasing container image to Heroku (this can take a while)...";
	$(MAKE) heroku-container-login
	$(MAKE) heroku-tag-stg
	$(MAKE) heroku-pushimg-stg
	$(MAKE) heroku-release-stg
	@echo "Running migrations on staging (call heroku run if HEROKU_MIGRATE_CMD set)";
	@if [ -n "$(HEROKU_MIGRATE_CMD)" ]; then heroku run -a $(HEROKU_APP_STG) -- $(HEROKU_MIGRATE_CMD); else echo "No HEROKU_MIGRATE_CMD set; skipping migrations"; fi
	@echo "Staging deploy complete. Run 'make heroku-logs-stg' to tail logs and 'make stg-open' to open site.";

# ---- Python venv/dev deps ----------------------------------------------------
venv: ## Create .venv (python3)
	python3 -m venv .venv && . .venv/bin/activate && python -m pip install --upgrade pip

deps: venv ## Install dev dependencies
	. .venv/bin/activate && pip install -r requirements.txt || true

# ---- QoL: staging helpers ----------------------------------------------------
heroku-logs-stg: ## Tail Heroku logs (staging)
	heroku logs --tail -a $(HEROKU_APP_STG)

stg-open: ## Open staging site in browser
	@xdg-open "https://$(HEROKU_APP_STG).herokuapp.com" >/dev/null 2>&1 || open "https://$(HEROKU_APP_STG).herokuapp.com"

# ---- Docs: generate a Markdown usage guide from this Makefile ----------------
DOCS_DIR       ?= docs
USAGE_MD       ?= $(DOCS_DIR)/MAKE_USAGE.md

help-md: ## Generate docs/MAKE_USAGE.md from Makefile help comments
	@mkdir -p "$(DOCS_DIR)"
	@{ \
		echo "# 🛠️ Make Commands — Usage Guide"; \
		echo ""; \
		echo "This file is auto-generated from Makefile comments. Run \`make help-md\` to refresh."; \
		echo ""; \
		echo "## Quick Start"; \
		echo ""; \
		echo "make up            # build + start all services"; \
		echo "make logs          # tail all logs"; \
		echo "make smoke         # quick health checks"; \
		echo "make stg-release   # build → push (Docker Hub) → deploy (Heroku)"; \
		echo ""; \
		echo "## Commands"; \
		echo ""; \
		grep -E '^[a-zA-Z0-9_\-]+:.*?##' $(firstword $(MAKEFILE_LIST)) \
		  | sed -E 's/^([a-zA-Z0-9_\-]+):.*?## (.*)$$/- **\1** — \2/' \
		  | sort; \
		echo ""; \
		echo "---"; \
		echo "### Notes"; \
		echo "- Commands are documented inline in the Makefile using \`##\` comments."; \
		echo "- If something fails with env/ports, run \`make doctor\`."; \
	} > "$(USAGE_MD)"
	@echo "✔ Wrote $(USAGE_MD)"

# ---- Local env bootstrap -----------------------------------------------------
env-init: ## Create backend/.env.development with safe defaults (won't overwrite)
	@test -f backend/.env.development || { \
		echo "Creating backend/.env.development"; \
		JWT=$$($(PY) -c 'import secrets; print(secrets.token_hex(32))'); \
		cat > backend/.env.development <<-EOF
		JWT_SECRET_KEY=$$JWT
		MAIL_FROM=noreply@cape-control.com
		MAIL_PROVIDER=postmark
		MAIL_SERVER=smtp.postmarkapp.com
		MAIL_USER=<POSTMARK_SERVER_TOKEN>
		MAIL_PASSWORD=<POSTMARK_SERVER_TOKEN>
		MAIL_PORT=587
		MAIL_TLS=true
		REDIS_URL=redis://redis:6379/0
		EOF
	}

env-check: ## Validate required keys exist in backend/.env.development
	@set -e; p="backend/.env.development"; \
	if [ ! -f "$$p" ]; then echo "Missing: $$p"; exit 1; fi; \
	req="JWT_SECRET_KEY MAIL_FROM MAIL_SERVER MAIL_USER MAIL_PASSWORD MAIL_PORT REDIS_URL"; \
	miss=""; \
	for k in $$req; do \
	  v=$$(grep -E "^$${k}=" "$$p" | tail -n1 | cut -d= -f2- | tr -d '[:space:]'); \
	  [ -n "$$v" ] || miss="$$miss $$k"; \
	done; \
	if [ -n "$$miss" ]; then echo "Missing values:$$miss"; exit 2; else echo "env OK"; fi

mail-test: ## Send a test email using backend/.env.development
	@set -e; set -a; source backend/.env.development; set +a; \
	test -n "$$MAIL_TO" || { echo "Set MAIL_TO in backend/.env.development"; exit 2; }; \
	$(PY) - <<'PY'
	import os, smtplib
	from email.message import EmailMessage
	host=os.getenv("MAIL_SERVER"); port=int(os.getenv("MAIL_PORT","587"))
	user=os.getenv("MAIL_USER"); pwd=os.getenv("MAIL_PASSWORD")
	sender=os.getenv("MAIL_FROM"); to=os.getenv("MAIL_TO")
	m=EmailMessage(); m["From"]=sender; m["To"]=to; m["Subject"]="SMTP test ✔"
	m.set_content("Hello from autolocal via MailerSend SMTP (STARTTLS).")
	with smtplib.SMTP(host, port, timeout=30) as s:
	    s.ehlo(); s.starttls(); s.ehlo(); s.login(user, pwd); s.send_message(m)
	print("Sent OK")
	PY
