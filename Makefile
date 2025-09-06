# ---------------------------------
# Makefile — Autorisen
# ---------------------------------
# Usage examples:
#   make up
#   make deploy-health HEROKU_APP=autorisen OPEN_LOGS=1
#   make smoke HOST=custom.domain.com
#   make heroku-deploy HEROKU_APP=capecraft
#
# Variables you can override per call:
#   HEROKU_APP=autorisen HOST=  USE_LOCAL=0  HEALTH_STRICT=0  OPEN_LOGS=0  CREATE_TAG=1
# ---------------------------------

.PHONY: deps predeploy up down clean rebuild logs be-logs fe-logs ps tools psql \
	update-git cleanup smoke smoke-local update-docs heroku-login heroku-push \
	heroku-release heroku-deploy heroku-logs heroku-open deploy-health devlog \
	check fmt lint typecheck prune env db-migrate db-upgrade db-downgrade db-seed \
	db-dump db-restore db-init smoke-int-local

# ---------------------------------
# Config
# ---------------------------------
HEROKU_APP ?= autorisen     # Override at call time
HOST ?=                      # Optional custom domain (e.g., api.example.com)
SMOKE_HOST = $(if $(HOST),$(HOST),$(HEROKU_APP).herokuapp.com)

# ---------------------------------
# Python deps (local dev)
# ---------------------------------
deps:
	python -m pip install -r requirements.txt || true
	python -m pip install -r backend/requirements.txt || true

# ---------------------------------
# Pre-deployment gate
# ---------------------------------
predeploy:
	@echo "🧪 Running predeploy gate script (if present)"
	@if [ -f scripts/predeploy_gate.sh ]; then \
		bash scripts/predeploy_gate.sh; \
	else \
		echo "ℹ️  scripts/predeploy_gate.sh not found; skipping gate"; \
	fi

# ---------------------------------
# Local Development (Docker Compose)
# ---------------------------------
up:
	docker compose up -d

down:
	docker compose down --remove-orphans

clean:
	@read -p "⚠️  This will REMOVE ALL VOLUMES and wipe data. Continue? (y/N) " ans; \
	if [ "$$ans" = "y" ] || [ "$$ans" = "Y" ]; then \
		docker compose down -v --remove-orphans; \
	else \
		echo "❌ Aborted clean."; \
	fi

rebuild:
	docker compose build --no-cache

logs:
	docker compose logs -f --tail=200

be-logs:
	docker compose logs -f backend

fe-logs:
	docker compose logs -f frontend

ps:
	docker compose ps

devlog: logs

# Optional tools profile (pgAdmin, Redis Commander, etc.)
tools:
	docker compose --profile tools up -d

# psql shortcut into the dev Postgres (expects host 5433 -> container 5432 mapping)
psql:
	PGPASSWORD=$${POSTGRES_PASSWORD} psql -h 127.0.0.1 -p 5433 -U $${POSTGRES_USER} -d $${POSTGRES_DB}

# Initialize database tables (runs app.init_db inside backend container)
db-init:
	@echo "🗄️  Initializing database tables via app.init_db"
	@docker compose exec -T backend python -c 'import app.init_db as m' || (echo "❌ db-init failed" && exit 1)
	@echo "✅ db-init complete"

# ---------------------------------
# Git helper (skip CI)
# ---------------------------------
update-git:
	@git status -sb
	@echo "🔄 Staging all changes..."
	git add .
	@echo "✍️  Committing (with [skip ci])..."
	git commit -m "chore: update local changes [skip ci]" || true
	@echo "⬆️  Pushing to GitHub (origin main)..."
	git push origin main
	@echo "✅ Update pushed (CI skipped)."

# ---------------------------------
# Cleanup (safe)
# ---------------------------------
cleanup:
	bash scripts/cleanup.sh $(PWD) || true

# ---------------------------------
# Smoke checks
# ---------------------------------
smoke:
	@echo "🔎 Remote smoke check: https://$(SMOKE_HOST)/api/health/status"
	@curl -fsS "https://$(SMOKE_HOST)/api/health/status" -m 10 -H 'Accept: application/json' >/dev/null && echo "✅ Health OK"

smoke-local:
	@echo "🔎 Local smoke check: http://127.0.0.1:8000/api/health/status"
	@curl -fsS "http://127.0.0.1:8000/api/health/status" -m 10 -H 'Accept: application/json' >/dev/null && echo "✅ Health OK"

# Minimal local smoke for integrations (CRM lead)
smoke-int-local:
	@echo "🔎 Local integrations smoke: POST /api/v1/integrations/crm/leads"
	@curl -fsS -m 10 -H 'content-type: application/json' \
	  -d '{"name":"Smoke Lead","email":"smoke@example.com","source":"smoke","metadata":{"k":"v"}}' \
	  http://127.0.0.1:8000/api/v1/integrations/crm/leads \
	  | sed 's/.*/✅ OK (lead created)/' || (echo "❌ Integrations smoke failed" && exit 1)

# ---------------------------------
# Docs timestamp updater
# ---------------------------------
update-docs:
	@echo "📝 Updating docs/STATUS.md timestamp"
	@mkdir -p docs
	@DATE=$$(date -u +"%Y-%m-%d %H:%M:%S UTC"); \
	{ \
		echo "# Deployment Status"; \
		echo ""; \
		echo "- App: $(HEROKU_APP)"; \
		echo "- Timestamp: $$DATE"; \
		echo ""; \
	} > docs/STATUS.md
	@echo "📝 Wrote docs/STATUS.md"

# ---------------------------------
# Heroku container deploy helpers
# ---------------------------------
heroku-login:
	@echo "🔐 Heroku container login"
	heroku container:login

heroku-push:
	@echo "📦 Pushing container image to Heroku ($(HEROKU_APP))"
	heroku container:push web -a $(HEROKU_APP)

heroku-release:
	@echo "🚀 Releasing image on Heroku ($(HEROKU_APP))"
	heroku container:release web -a $(HEROKU_APP)

# Full deploy (login → push → release)
heroku-deploy: heroku-login heroku-push heroku-release
	@echo "✅ Heroku deploy complete for $(HEROKU_APP)"

heroku-logs:
	@echo "📜 Tailing Heroku logs for $(HEROKU_APP) (Ctrl+C to exit)"
	heroku logs --tail -a $(HEROKU_APP)

heroku-open:
	@echo "🌐 Opening https://$(SMOKE_HOST)"
	heroku open -a $(HEROKU_APP)

# ---------------------------------
# Unified health → docs → git → (gate) → deploy
# ---------------------------------
# Usage:
#   make deploy-health HEROKU_APP=my-app            # Remote health check (default)
#   make deploy-health USE_LOCAL=1                  # Use local health check instead of remote
#   make deploy-health HOST=custom.domain.com       # Override remote host
#   make deploy-health HEALTH_STRICT=1              # Fail fast if health fails
#   make deploy-health OPEN_LOGS=1                  # Tail Heroku logs after deploy
#   make deploy-health CREATE_TAG=0                 # Disable git tag creation
deploy-health:
	@echo "🚦 Starting gated deploy pipeline (health → docs → git → heroku)"
	@echo "   Options: USE_LOCAL=$(USE_LOCAL) HEALTH_STRICT=$(HEALTH_STRICT) OPEN_LOGS=$(OPEN_LOGS) CREATE_TAG=$(CREATE_TAG)"
	{ \
	  # 1) Health check
	  if [ "$(USE_LOCAL)" = "1" ]; then \
	    echo "🔍 Running local health check"; \
	    $(MAKE) smoke-local; HC=$$?; \
	  else \
	    echo "🔍 Running remote health check against https://$(SMOKE_HOST)"; \
	    $(MAKE) smoke; HC=$$?; \
	  fi; \
	  if [ $$HC -ne 0 ]; then \
	    echo "❌ Health check failed"; \
	    if [ "$(HEALTH_STRICT)" = "1" ]; then \
	      echo "⛔ Aborting deploy due to failed health (set HEALTH_STRICT=0 to continue without deploy)."; \
	      exit 1; \
	    else \
	      echo "⚠️  Proceeding without deploy (will still update docs & commit)."; \
	      SKIP_DEPLOY=1; \
	    fi; \
	  else \
	    echo "✅ Health check passed"; \
	  fi; \
	  # 2) Update docs
	  $(MAKE) update-docs; \
	  # 3) Commit & push docs (if changed)
	  echo "🔄 Staging documentation changes"; \
	  git add docs || true; \
	  BRANCH=$$(git rev-parse --abbrev-ref HEAD); \
	  COMMIT_MSG="chore: docs timestamp update (pre deploy)"; \
	  if git diff --cached --quiet; then \
	    echo "ℹ️  No doc changes to commit"; \
	  else \
	    echo "✍️  Committing: $$COMMIT_MSG"; \
	    git commit -m "$$COMMIT_MSG" || true; \
	  fi; \
	  echo "⬆️  Pushing branch $$BRANCH"; \
	  git push origin $$BRANCH; \
	  # 4) Optional deploy (gate + heroku)
	  if [ "$$SKIP_DEPLOY" = "1" ]; then \
	    echo "🚫 Deployment skipped due to failed health."; \
	    exit 0; \
	  fi; \
	  $(MAKE) predeploy || exit 1; \
	  $(MAKE) heroku-deploy HEROKU_APP=$(HEROKU_APP) || exit 1; \
	  # 5) Optional tagging
	  if [ "$(CREATE_TAG)" != "0" ]; then \
	    DATE=$$(date -u +%Y%m%d-%H%M); SHA=$$(git rev-parse --short HEAD); \
	    TAG=$${TAG_NAME:-deploy-$(HEROKU_APP)-$$DATE-$$SHA}; \
	    if git tag | grep -q "^$$TAG$$"; then \
	      echo "🏷  Tag $$TAG already exists (skipping)"; \
	    else \
	      git tag -a $$TAG -m "Deploy to $(HEROKU_APP) $$DATE ($$SHA)"; \
	      git push origin $$TAG; \
	      echo "🏷  Created & pushed tag $$TAG"; \
	    fi; \
	  else \
	    echo "🏷  Tag creation disabled (CREATE_TAG=0)"; \
	  fi; \
	  # 6) Optional log tail
	  if [ "$(OPEN_LOGS)" = "1" ]; then \
	    echo "📜 Tailing Heroku logs (Ctrl+C to exit)..."; \
	    heroku logs --tail -a $(HEROKU_APP); \
	  fi; \
	  echo "✅ Deploy-health pipeline complete for $(HEROKU_APP)"; \
	}

# ---------------------------------
# Quality-of-life: checks & formatting (safe if tools missing)
# ---------------------------------
check:
	@echo "🔎 Running checks (fmt, lint, typecheck, tests)"
	$(MAKE) fmt || true
	$(MAKE) lint || true
	$(MAKE) typecheck || true
	pytest -q || true

fmt:
	@black backend/ || true

lint:
	@ruff check backend/ || flake8 backend/ || true

typecheck:
	@mypy backend/ || true

prune:
	@echo "🧹 Docker prune (system + volumes)"
	-docker system prune -f
	-docker volume prune -f

env:
	@echo "🔧 Required environment (if using psql target):"
	@echo "  POSTGRES_DB=$${POSTGRES_DB:-<missing>}"
	@echo "  POSTGRES_USER=$${POSTGRES_USER:-<missing>}"
	@echo "  POSTGRES_PASSWORD=$${POSTGRES_PASSWORD:-<missing>}"

# ---------------------------------
# DB workflow (optional; safe no-ops if Alembic/scripts absent)
# ---------------------------------
db-migrate:
	@if [ -f alembic.ini ]; then \
		alembic -c backend/migrations/alembic.ini revision --autogenerate -m "auto"; \
	else \
		echo "ℹ️  alembic.ini not found; skipping db-migrate"; \
	fi

db-upgrade:
	@if [ -f alembic.ini ]; then \
		alembic -c backend/migrations/alembic.ini upgrade head; \
	else \
		echo "ℹ️  alembic.ini not found; skipping db-upgrade"; \
	fi

db-downgrade:
	@if [ -f alembic.ini ]; then \
		alembic -c backend/migrations/alembic.ini downgrade -1; \
	else \
		echo "ℹ️  alembic.ini not found; skipping db-downgrade"; \
	fi

db-seed:
	@if [ -f backend/scripts/seed.py ]; then \
		python backend/scripts/seed.py; \
	else \
		echo "ℹ️  backend/scripts/seed.py not found; skipping db-seed"; \
	fi

db-dump:
	@echo "💾 Dumping local DB to ./db_dump.sql"
	@PGPASSWORD=$${POSTGRES_PASSWORD} pg_dump -h 127.0.0.1 -p 5433 -U $${POSTGRES_USER} -d $${POSTGRES_DB} > db_dump.sql

db-restore:
	@echo "📥 Restoring ./db_dump.sql to local DB"
	@PGPASSWORD=$${POSTGRES_PASSWORD} psql -h 127.0.0.1 -p 5433 -U $${POSTGRES_USER} -d $${POSTGRES_DB} < db_dump.sql

# Convenience: run Alembic upgrade using local Postgres via docker-compose env
.PHONY: db-upgrade-local db-downgrade-local db-upgrade-in-container db-stamp-head-local db-stamp-rev-local
db-upgrade-local:
	@if [ -f alembic.ini ]; then \
		export DATABASE_URL="postgresql://$${POSTGRES_USER:-autorisen}:$${POSTGRES_PASSWORD:-postgres}@127.0.0.1:5433/$${POSTGRES_DB:-autorisen}"; \
		alembic -c backend/migrations/alembic.ini upgrade head; \
	else \
		echo "ℹ️  alembic.ini not found; skipping"; \
	fi

db-downgrade-local:
	@if [ -f alembic.ini ]; then \
		export DATABASE_URL="postgresql://$${POSTGRES_USER:-autorisen}:$${POSTGRES_PASSWORD:-postgres}@127.0.0.1:5433/$${POSTGRES_DB:-autorisen}"; \
		alembic -c backend/migrations/alembic.ini downgrade -1; \
	else \
		echo "ℹ️  alembic.ini not found; skipping"; \
	fi

db-upgrade-in-container:
	@if [ -f alembic.ini ]; then \
		docker compose exec backend /opt/venv/bin/alembic -c backend/migrations/alembic.ini upgrade head || echo "ℹ️  Could not run alembic inside container"; \
	else \
		echo "ℹ️  alembic.ini not found; skipping"; \
	fi

# Show current Alembic revision in the running backend container
.PHONY: db-current-in-container db-heads-in-container
db-current-in-container:
	@if [ -f alembic.ini ]; then \
		docker compose exec backend /opt/venv/bin/alembic -c backend/migrations/alembic.ini current; \
	else \
		echo "ℹ️  alembic.ini not found; skipping"; \
	fi

# List Alembic head revisions in the running backend container
db-heads-in-container:
	@if [ -f alembic.ini ]; then \
		docker compose exec backend /opt/venv/bin/alembic -c backend/migrations/alembic.ini heads; \
	else \
		echo "ℹ️  alembic.ini not found; skipping"; \
	fi

# Stamp local DB to the latest head (useful if tables already exist)
db-stamp-head-local:
	@if [ -f alembic.ini ]; then \
		export DATABASE_URL="postgresql://$${POSTGRES_USER:-autorisen}:$${POSTGRES_PASSWORD:-postgres}@127.0.0.1:5433/$${POSTGRES_DB:-autorisen}"; \
		alembic stamp head; \
	else \
		echo "ℹ️  alembic.ini not found; skipping"; \
	fi

# Stamp local DB to a specific revision: make db-stamp-rev-local REV=add_audit_logs_table
db-stamp-rev-local:
	@if [ -z "$(REV)" ]; then \
		echo "❌ Provide REV=name e.g., make db-stamp-rev-local REV=add_audit_logs_table"; exit 1; \
	fi; \
	if [ -f alembic.ini ]; then \
		export DATABASE_URL="postgresql://$${POSTGRES_USER:-autorisen}:$${POSTGRES_PASSWORD:-postgres}@127.0.0.1:5433/$${POSTGRES_DB:-autorisen}"; \
		alembic stamp $(REV); \
	else \
		echo "ℹ️  alembic.ini not found; skipping"; \
	fi
