.PHONY: deps predeploy heroku-login heroku-push heroku-release heroku-deploy heroku-logs \
        smoke smoke-local up down clean rebuild logs be-logs fe-logs ps tools psql

# Set the Heroku app name, override at call time:
#   HEROKU_APP=my-app make heroku-deploy
HEROKU_APP ?= autorisen

# Prefer a custom HOST if provided, else default to Heroku subdomain
HOST ?=
SMOKE_HOST = $(if $(HOST),$(HOST),$(HEROKU_APP).herokuapp.com)

# -------------------------
# Python deps (local dev)
# -------------------------
deps:
	python -m pip install -r requirements.txt || true
	python -m pip install -r backend/requirements.txt || true

# -------------------------
# Pre-deployment gate
# -------------------------
predeploy:
	bash scripts/predeploy_gate.sh

# -------------------------
# Heroku (Container Deploy)
# -------------------------
heroku-login:
	heroku container:login

heroku-push: heroku-login
	heroku container:push web -a $(HEROKU_APP)

heroku-release:
	heroku container:release web -a $(HEROKU_APP)

heroku-deploy: predeploy heroku-push heroku-release
	@echo "✅ Deployed to Heroku app $(HEROKU_APP)"

heroku-logs:
	heroku logs --tail -a $(HEROKU_APP)

# -------------------------
# Smoke tests
# -------------------------

# Cloud smoke: tries /api/health, /health, and /; prints status codes and succeeds on first 200
smoke:
	@echo "🔎 Smoking: https://$(SMOKE_HOST)"
	@set -e; \
	for path in /api/health /health /; do \
	  code=$$(curl -sS -o /dev/null -w "%{http_code}" "https://$(SMOKE_HOST)$$path"); \
	  echo "→ GET $$path -> $$code"; \
	  if [ "$$code" = "200" ]; then \
	    echo "✅ Healthy at $$path"; \
	    exit 0; \
	  fi; \
	done; \
	echo "❌ Not healthy at /api/health or /health (see codes above)"; \
	exit 1

# Local smoke: checks your dev stack at http://localhost:8000
smoke-local:
	@echo "🔎 Smoking local: http://localhost:8000"
	@set -e; \
	for path in /api/health /health /; do \
	  code=$$(curl -sS -o /dev/null -w "%{http_code}" "http://localhost:8000$$path"); \
	  echo "→ GET $$path -> $$code"; \
	  if [ "$$code" = "200" ]; then \
	    echo "✅ Healthy locally at $$path"; \
	    exit 0; \
	  fi; \
	done; \
	echo "❌ Local API not healthy at /api/health or /health (see codes above)"; \
	exit 1

# -------------------------
# Local Development (Docker Compose)
# -------------------------
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

# Start optional tools (pgAdmin + Redis Commander)
tools:
	docker compose --profile tools up -d

# psql shortcut into the dev Postgres
psql:
	PGPASSWORD=$${POSTGRES_PASSWORD} psql -h 127.0.0.1 -p 5433 -U $${POSTGRES_USER} -d $${POSTGRES_DB}
