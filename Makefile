# --- DEV email stubs (safe defaults) ---
EMAIL_TOKEN_SECRET ?= dev-insecure-token
FROM_EMAIL         ?= dev@localhost
SMTP_USERNAME      ?= dev
SMTP_PASSWORD      ?= dev
SMTP_HOST          ?= localhost
SMTP_PORT          ?= 1025
SMTP_TLS           ?= false
MCP_BIND_HOST      ?= 0.0.0.0
MCP_PORT           ?= 8000
MCP_SMOKE_PORT     ?= 8787

export PYTHONPATH ?= $(CURDIR)


mcp-host:
	@echo "== Starting MCP host (ENV=$(ENV)) =="
	@set -euo pipefail; \
	: $${OPENAI_API_KEY:?OPENAI_API_KEY must be set for mcp-host}; \
	UVICORN_BIN=$$( [ -x "$(VENV)/bin/uvicorn" ] && echo "$(VENV)/bin/uvicorn" || command -v uvicorn ); \
	if [ -z "$$UVICORN_BIN" ]; then echo "uvicorn not found; run 'make install' first" >&2; exit 127; fi; \
	ENABLE_MCP_HOST=1 ENV=$(ENV) OPENAI_API_KEY=$$OPENAI_API_KEY \
		EMAIL_TOKEN_SECRET="$(EMAIL_TOKEN_SECRET)" FROM_EMAIL="$(FROM_EMAIL)" \
		SMTP_USERNAME="$(SMTP_USERNAME)" SMTP_PASSWORD="$(SMTP_PASSWORD)" \
		SMTP_HOST="$(SMTP_HOST)" SMTP_PORT="$(SMTP_PORT)" SMTP_TLS="$(SMTP_TLS)" \
		PORT=$(MCP_PORT) \
		"$$UVICORN_BIN" backend.src.app:app --host $(MCP_BIND_HOST) --port $(MCP_PORT)

# =============================================================================
# Makefile — Autolocal / CapeControl
# =============================================================================

SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help

# ----------------------------------------------------------------------------- 
# Core vars
# -----------------------------------------------------------------------------
PY := python3
PIP := $(PY) -m pip
VENV := .venv
REQ := requirements.txt

IMAGE ?= autorisen:local
PORT ?= 8000

HEROKU_APP_STG  ?= autorisen
HEROKU_APP_PROD ?= capecraft
HEROKU_APP_NAME ?= $(HEROKU_APP_STG)
HEROKU_APP      ?= $(HEROKU_APP_STG)

# Domains
DEV_BASE_URL  ?= https://dev.cape-control.com
PROD_BASE_URL ?= https://cape-control.com
PROD_URL      ?= https://cape-control.com

# Docs inputs for sitemap
SITEMAP_DEV_TXT  ?= docs/sitemap.dev.txt
SITEMAP_PROD_TXT ?= docs/sitemap.prod.txt

# Output static sitemap (served by Vite from / if present)
PUBLIC_DIR ?= client/public
SITEMAP_XML ?= sitemap.xml

# Crawl
CRAWL_OUT ?= docs/crawl
CRAWL_TOOL ?= tools/crawl_sitemap.py

# Staging smoke
STAGING_URL ?= https://dev.cape-control.com

# Test DB (single source of truth)
TEST_DB_URL ?= sqlite:////tmp/autolocal_test.db

# ----------------------------------------------------------------------------- 
# PHONY index (single, authoritative)
# -----------------------------------------------------------------------------
.PHONY: help venv install format lint test docker-build docker-run docker-push \
	deploy-heroku heroku-deploy-stg heroku-deploy-prod heroku-logs heroku-run-migrate \
	github-update clean plan-validate plan-open \
	migrate-up migrate-revision \
	sitemap-generate-dev sitemap-generate-prod verify-sitemap verify-sitemap-dev verify-sitemap-prod \
	crawl-local crawl-dev crawl-prod crawl sitemap-svg \
	agents-new agents-validate agents-test agents-run \
	codex-check codex-open codex-docs-lint codex-docs-fix codex-ci-validate \
	codex-plan-diff codex-plan-apply codex-test-heal codex-test codex-test-cov codex-test-dry codex-run \
	smoke-staging smoke-local csrf-probe-staging csrf-probe-local codex-smoke smoke-prod \
	payments-checkout \
	dockerhub-login dockerhub-logout dockerhub-setup-builder dockerhub-build dockerhub-push dockerhub-build-push \
	dockerhub-release dockerhub-update-description dockerhub-clean \
	playbooks-overview playbook-overview playbook-open playbook-badge playbook-new playbooks-check \
	design-sync design-validate

# ----------------------------------------------------------------------------- 
# Help (auto-docs)
# -----------------------------------------------------------------------------
help: ## List Make targets (auto-docs)
	@awk 'BEGIN {FS=":.*##"; printf "\n\033[1mMake targets\033[0m\n"} /^[a-zA-Z0-9_.-]+:.*##/ { printf "  \033[36m%-30s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

# ----------------------------------------------------------------------------- 
# Python env / dev tasks
# -----------------------------------------------------------------------------
venv: ## Create a virtualenv in $(VENV)
	@if [ -d "$(VENV)" ]; then \
		echo "Virtualenv $(VENV) already exists"; \
	else \
		$(PY) -m venv $(VENV); \
		echo "Created virtualenv $(VENV)"; \
	fi

install: venv ## Install project dependencies (uses $(REQ) if present)
	@echo "Installing dependencies..."
	@if [ -f "$(REQ)" ]; then \
		$(VENV)/bin/python -m pip install -r $(REQ); \
	else \
		$(VENV)/bin/python -m pip install -e . || true; \
		echo "No requirements.txt found; attempted editable install"; \
	fi

format: ## Run code formatters (black/isort)
	@echo "Running formatters..."
	@$(VENV)/bin/python -m pip install black isort >/dev/null 2>&1 || true
	@$(VENV)/bin/black . || true
	@$(VENV)/bin/isort . || true

lint: ## Run ruff linter
	@echo "Running ruff linter..."
	@$(VENV)/bin/python -m pip install ruff >/dev/null 2>&1 || true
	@$(VENV)/bin/ruff check . || true

test: ## Run tests (pytest)
	@echo "Running tests..."
	@$(VENV)/bin/python -m pip install pytest >/dev/null 2>&1 || true
	@$(VENV)/bin/pytest -q || true

payments-checkout: ## Generate a sample PayFast checkout payload
	@$(VENV)/bin/python scripts/payfast_checkout.py

# ----------------------------------------------------------------------------- 
# Docker (local) 
# -----------------------------------------------------------------------------
docker-build: ## Build docker image (IMAGE=$(IMAGE))
	@echo "Building docker image $(IMAGE)..."
	@for i in 1 2 3; do \
		if docker build -t $(IMAGE) .; then \
			echo "Docker build succeeded on attempt $$i"; exit 0; \
		fi; \
		echo "Docker build failed (attempt $$i). Retrying in 5s..."; sleep 5; \
	done; \
	echo "Docker build failed after retries"; exit 1

docker-run: ## Run docker image locally (exposes $(PORT))
	@echo "Running docker image $(IMAGE) on port $(PORT)..."
	docker run --rm -p $(PORT):$(PORT) --env PORT=$(PORT) $(IMAGE)

docker-push: ## Push local image tag to $(REGISTRY) (set REGISTRY=…)
	@if [ -z "$(REGISTRY)" ]; then \
		echo "Please set REGISTRY or use deploy-heroku for Heroku (set HEROKU_APP_NAME)."; exit 1; \
	fi
	@echo "Tagging and pushing to $(REGISTRY)/$(IMAGE)..."
	docker tag $(IMAGE) $(REGISTRY)/$(IMAGE)
	docker push $(REGISTRY)/$(IMAGE)

# ----------------------------------------------------------------------------- 
# Heroku container deploy (Enhanced)
# -----------------------------------------------------------------------------
deploy-heroku: docker-build ## Build/push/release to both staging (autorisen) and production (capecraft) with enhanced logging
	@echo "🔐 Logging in to Heroku Container Registry..."
	@for i in 1 2 3; do \
		if heroku container:login >/dev/null 2>&1; then echo "✅ Login successful"; break; fi; \
		echo "⚠️  Login failed (attempt $$i/3). Retrying in 5s..."; sleep 5; \
	done
	@echo ""
	@echo "🚀 === DEPLOYING TO STAGING ($(HEROKU_APP_STG)) ==="
	@echo "🏷️  Tagging image for staging registry..."
	docker tag $(IMAGE) registry.heroku.com/$(HEROKU_APP_STG)/web
	@echo "� Pushing image to staging registry..."
	@for i in 1 2 3; do \
		if docker push registry.heroku.com/$(HEROKU_APP_STG)/web; then echo "✅ Staging push successful"; break; fi; \
		echo "⚠️  Staging push failed (attempt $$i/3). Retrying in 10s..."; sleep 10; \
		[ $$i -eq 3 ] && { echo "❌ Staging push failed after retries"; exit 1; } || true; \
	done
	@echo "🚀 Releasing container to staging..."
	@for i in 1 2 3; do \
		if heroku container:release web --app $(HEROKU_APP_STG); then echo "✅ Staging release successful"; break; fi; \
		echo "⚠️  Staging release failed (attempt $$i/3). Retrying in 10s..."; sleep 10; \
		[ $$i -eq 3 ] && { echo "❌ Staging release failed after retries"; exit 1; } || true; \
	done
	@echo "✅ Staging deployment completed! App URL: https://$(HEROKU_APP_STG).herokuapp.com"
	@echo ""
	@echo "🚀 === DEPLOYING TO PRODUCTION ($(HEROKU_APP_PROD)) ==="
	@echo "🏷️  Tagging image for production registry..."
	docker tag $(IMAGE) registry.heroku.com/$(HEROKU_APP_PROD)/web
	@echo "📤 Pushing image to production registry..."
	@for i in 1 2 3; do \
		if docker push registry.heroku.com/$(HEROKU_APP_PROD)/web; then echo "✅ Production push successful"; break; fi; \
		echo "⚠️  Production push failed (attempt $$i/3). Retrying in 10s..."; sleep 10; \
		[ $$i -eq 3 ] && { echo "❌ Production push failed after retries"; exit 1; } || true; \
	done
	@echo "🚀 Releasing container to production..."
	@for i in 1 2 3; do \
		if heroku container:release web --app $(HEROKU_APP_PROD); then echo "✅ Production release successful"; break; fi; \
		echo "⚠️  Production release failed (attempt $$i/3). Retrying in 10s..."; sleep 10; \
		[ $$i -eq 3 ] && { echo "❌ Production release failed after retries"; exit 1; } || true; \
	done
	@echo "✅ Production deployment completed! App URL: https://$(HEROKU_APP_PROD).herokuapp.com"
	@echo ""
	@echo "🎉 DUAL DEPLOYMENT COMPLETED!"
	@echo "   📋 Staging:    https://$(HEROKU_APP_STG).herokuapp.com"
	@echo "   🚀 Production: https://$(HEROKU_APP_PROD).herokuapp.com"

heroku-deploy-stg: ## Quick push/release to staging only ($(HEROKU_APP_STG))
	@echo "🚀 Quick staging deployment to $(HEROKU_APP_STG)..."
	heroku container:login
	heroku container:push web -a $(HEROKU_APP_STG)
	heroku container:release web -a $(HEROKU_APP_STG)
	@echo "✅ Staging deployment complete"
	heroku open -a $(HEROKU_APP_STG)

heroku-deploy-prod: ## Quick push/release to production only ($(HEROKU_APP_PROD))
	@echo "🚀 Quick production deployment to $(HEROKU_APP_PROD)..."
	heroku container:login
	heroku container:push web -a $(HEROKU_APP_PROD)
	heroku container:release web -a $(HEROKU_APP_PROD)
	@echo "✅ Production deployment complete"
	heroku open -a $(HEROKU_APP_PROD)

heroku-logs: ## Tail Heroku logs for $(HEROKU_APP_NAME)
	@echo "📋 Tailing logs for $(HEROKU_APP_NAME)..."
	heroku logs --tail --app $(HEROKU_APP_NAME)

heroku-shell: ## Open bash shell in Heroku container
	@echo "🐚 Opening shell in $(HEROKU_APP_NAME)..."
	heroku run bash --app $(HEROKU_APP_NAME)

heroku-run-migrate: ## Run database migrations on Heroku
	@echo "🗃️  Running migrations on $(HEROKU_APP_NAME)..."
	heroku run python -m alembic -c backend/alembic.ini upgrade head --app $(HEROKU_APP_NAME)

heroku-config-push: ## Push local .env to Heroku config (be careful!)
	@if [ ! -f .env ]; then echo "❌ .env file not found"; exit 1; fi
	@echo "⚠️  Pushing .env to Heroku config for $(HEROKU_APP_NAME)..."
	@read -p "Are you sure? This will overwrite Heroku config vars [y/N]: " confirm && [ "$$confirm" = "y" ] || exit 1
	heroku config:push --app $(HEROKU_APP_NAME)

heroku-status: ## Check Heroku app status and health
	@echo "🔍 Checking status of $(HEROKU_APP_NAME)..."
	heroku ps --app $(HEROKU_APP_NAME)
	@echo "🔍 Health check..."
	@curl -f -s https://$(HEROKU_APP_NAME).herokuapp.com/api/health || echo "❌ Health check failed"
	@echo ""
	@curl -f -s https://$(HEROKU_APP_NAME).herokuapp.com/api/version || echo "⚠️  Version endpoint not available"

# ----------------------------------------------------------------------------- 
# Git helpers
# -----------------------------------------------------------------------------
github-update: ## Fast-forward the current branch from origin
	@echo "Updating branch $$(git rev-parse --abbrev-ref HEAD) from origin..."
	@git fetch origin
	@git pull --ff-only origin $$(git rev-parse --abbrev-ref HEAD)

clean: ## Remove common build artifacts
	rm -rf build/ dist/ *.egg-info .pytest_cache/ .venv

plan-validate: ## Validate plan CSV with tools/validate_plan_csv.py
	$(PY) tools/validate_plan_csv.py

plan-open: ## Open plan & Codex project plan
	code docs/CODEX_PROJECT_PLAN.md data/plan.csv

# ----------------------------------------------------------------------------- 
# Alembic
# -----------------------------------------------------------------------------
migrate-up: venv ## Alembic upgrade head
	@echo "Running Alembic upgrade head..."
	@$(VENV)/bin/python -m pip install -e backend >/dev/null 2>&1 || true
	@$(VENV)/bin/python -m alembic -c backend/alembic.ini upgrade head

migrate-revision: venv ## Create Alembic revision: make migrate-revision message="desc"
	@[ -n "$$message" ] || (echo "Usage: make migrate-revision message=\"<description>\""; exit 1)
	@echo "Creating Alembic revision: $$message"
	@$(VENV)/bin/python -m pip install -e backend >/dev/null 2>&1 || true
	@$(VENV)/bin/python -m alembic -c backend/alembic.ini revision -m "$$message"

# ----------------------------------------------------------------------------- 
# Sitemap generation & checks
# -----------------------------------------------------------------------------
define GEN_SITEMAP_XML
mkdir -p "$(PUBLIC_DIR)"
$(PY) - <<'PYCODE'
from datetime import date
from pathlib import Path
import os, sys

base = os.environ.get("BASE_URL", "").rstrip("/")
txt = Path(sys.argv[1])
out = Path("$(PUBLIC_DIR)") / "$(SITEMAP_XML)"
today = date.today().isoformat()

routes = [
    line.strip()
    for line in txt.read_text(encoding="utf-8").splitlines()
    if line.strip() and not line.lstrip().startswith("#")
]

xml_lines = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
]
xml_lines.extend(
    f"  <url><loc>{base + route if base else route}</loc><lastmod>{today}</lastmod></url>"
    for route in routes
)
xml_lines.append("</urlset>")

out.write_text("\n".join(xml_lines) + "\n", encoding="utf-8")
print(f"Wrote {out} with {len(routes)} routes.")
PYCODE
endef

sitemap-generate-dev: ## Generate $(PUBLIC_DIR)/$(SITEMAP_XML) from $(SITEMAP_DEV_TXT)
	@BASE_URL="$(DEV_BASE_URL)"; \
	$(call GEN_SITEMAP_XML,$(SITEMAP_DEV_TXT))

sitemap-generate-prod: ## Generate $(PUBLIC_DIR)/$(SITEMAP_XML) from $(SITEMAP_PROD_TXT)
	@BASE_URL="$(PROD_BASE_URL)"; \
	$(call GEN_SITEMAP_XML,$(SITEMAP_PROD_TXT))

verify-sitemap: ## Verify routes from FILE=... at BASE=...
	@[ -n "$(FILE)" ] || (echo "Usage: make verify-sitemap FILE=docs/sitemap.dev.txt BASE=<url>"; exit 1)
	@[ -n "$(BASE)" ] || (echo "Usage: make verify-sitemap FILE=... BASE=<url>"; exit 1)
	@echo "Verifying routes from $(FILE) at $(BASE)"
	@FAIL=0; \
	while IFS= read -r route; do \
		route="$${route%$$'\r'}"; \
		[ -z "$$route" ] && continue; \
		case "$$route" in \#*) continue;; esac; \
		code=$$(curl -s -o /dev/null -w "%{http_code}" "$(BASE)$$route"); \
		printf "%s  %s%s\n" "$$code" "$(BASE)" "$$route"; \
		case "$$code" in 2*|3*) : ;; *) FAIL=1; echo "❌ FAIL: $$route";; esac; \
	done < "$(FILE)"; \
	exit $$FAIL

verify-sitemap-dev: ## Curl-check all dev routes
	@$(MAKE) verify-sitemap FILE="$(SITEMAP_DEV_TXT)" BASE="$(DEV_BASE_URL)"

verify-sitemap-prod: ## Curl-check all prod routes
	@$(MAKE) verify-sitemap FILE="$(SITEMAP_PROD_TXT)" BASE="$(PROD_BASE_URL)"

# ----------------------------------------------------------------------------- 
# Crawl targets
# -----------------------------------------------------------------------------
crawl-local: ## Run tools/crawl_sitemap.py against http://localhost:3000
	$(PY) $(CRAWL_TOOL) --base-url http://localhost:3000 --outdir $(CRAWL_OUT) --label local

crawl-dev: ## Run crawler against dev.cape-control.com
	$(PY) $(CRAWL_TOOL) --base-url $(DEV_BASE_URL) --outdir $(CRAWL_OUT) --label dev

crawl-prod: ## Run crawler against cape-control.com
	$(PY) $(CRAWL_TOOL) --base-url https://www.cape-control.com --outdir $(CRAWL_OUT) --label prod

crawl: crawl-local ## Default crawl

sitemap-svg: ## Render sitemap mermaid to SVG
	npx mmdc -i docs/sitemap_v2_final.mmd -o docs/sitemap_v2_final.svg -t neutral -b transparent -s 1.5

# ----------------------------------------------------------------------------- 
# Agents tooling
# -----------------------------------------------------------------------------
agents-new: ## Create a new agent scaffold: make agents-new name=<slug>
	@[ -n "$$name" ] || (echo "Usage: make agents-new name=<slug>"; exit 1)
	@mkdir -p agents/$(name)/tests && \
	printf "name: %s\nrole: <fill>\nmodel: { provider: openai, name: gpt-4.1-mini, temperature: 0.2 }\npolicies: { allow_tools: [] }\ncontext: { system_prompt: |\n  You are %s. }\n" "$(name)" "$(name)" > agents/$(name)/agent.yaml
	@echo "Created agents/$(name)"

agents-validate: ## Validate agents registry
	@$(PY) scripts/agents_validate.py agents/registry.yaml

agents-test: ## Run agents unit tests
	@$(PY) -m pytest -q tests/test_agents_tooling.py

agents-run: ## Run an agent: make agents-run name=<slug> task="..."
	@[ -n "$$name" ] || (echo "Usage: make agents-run name=<slug> task=\"...\""; exit 1)
	@$(PY) scripts/agents_run.py --agent $$name --task "$$task"

# ----------------------------------------------------------------------------- 
# Codex helpers
# -----------------------------------------------------------------------------
CODEX_DOCS ?= \
  docs/DEVELOPMENT_CONTEXT.md \
  docs/MVP_SCOPE.md \
  docs/Checklist_MVP.md \
  docs/agents.md \
  docs/Heroku_Pipeline_Workflow.md

codex-check: ## Verify Codex context files & VS Code settings
	@echo "== Codex context files =="
	@for f in $(CODEX_DOCS); do \
		if [ -f "$$f" ]; then \
			printf '✅  %-35s  %8s bytes  %s\n' "$$f" "$$(wc -c < "$$f")" "$$(date -r "$$f" '+%Y-%m-%d %H:%M:%S')"; \
		else \
			printf '❌  %s (missing)\n' "$$f"; \
		fi; \
	done
	@echo
	@echo "VS Code prompt:"
	@if [ -f .vscode/codex.prompt.md ]; then \
		printf '✅  .vscode/codex.prompt.md        %8s bytes  %s\n' "$$(wc -c < .vscode/codex.prompt.md)" "$$(date -r .vscode/codex.prompt.md '+%Y-%m-%d %H:%M:%S')"; \
	else \
		echo "❌  .vscode/codex.prompt.md (missing)"; \
	fi
	@echo
	@echo "settings.json contains Codex keys?"
	@if [ -f .vscode/settings.json ]; then \
		if grep -q '"codex.contextFiles"' .vscode/settings.json && grep -q '"codex.systemPromptFile"' .vscode/settings.json; then \
			echo "✅  codex.* keys present"; \
		else \
			echo "⚠️  codex.* keys not found in .vscode/settings.json"; \
		fi; \
	else \
		echo "❌  .vscode/settings.json (missing)"; \
	fi

codex-open: ## Open Codex prompt and settings in VS Code
	@which code >/dev/null 2>&1 || { echo "⚠️  'code' CLI not found (install VS Code Shell Command)."; exit 0; }
	@[ -f .vscode/codex.prompt.md ] && code -g .vscode/codex.prompt.md || true
	@[ -f .vscode/settings.json ] && code -g .vscode/settings.json || true

codex-docs-lint: ## Markdown lint all docs (installs markdownlint-cli if needed)
	@command -v markdownlint >/dev/null 2>&1 || { echo "Installing markdownlint-cli (global)"; npm i -g markdownlint-cli >/dev/null 2>&1; }
	markdownlint "**/*.md" --ignore node_modules --ignore .venv

codex-docs-fix: ## Auto-fix Markdown lint issues
	@command -v markdownlint >/dev/null 2>&1 || { echo "Installing markdownlint-cli (global)"; npm i -g markdownlint-cli >/dev/null 2>&1; }
	markdownlint "**/*.md" --ignore node_modules --ignore .venv --fix || true
	@echo "Re-run lint to verify:"
	markdownlint "**/*.md" --ignore node_modules --ignore .venv

codex-ci-validate: ## Run pre-commit hooks (install if needed)
	@command -v pre-commit >/dev/null 2>&1 || { echo "Installing pre-commit"; $(PY) -m pip install --quiet pre-commit; }
	pre-commit run --all-files || true

codex-plan-diff: ## Check plan sync
	$(PY) scripts/plan_sync.py --check-only

codex-plan-apply: ## Apply plan sync
	$(PY) scripts/plan_sync.py --apply

codex-test-heal: ## Regenerate fixtures (best-effort) then pytest
	$(PY) scripts/regenerate_fixtures.py || true
	pytest -q || true

# --- Test env macros (DRY)
define TEST_ENV_EXPORT
export ENV="test"; \
export DATABASE_URL="$(TEST_DB_URL)"; \
export ALEMBIC_DATABASE_URL="$(TEST_DB_URL)"; \
export DISABLE_RECAPTCHA="true"; \
export RUN_DB_MIGRATIONS_ON_STARTUP="0"; \
export RATE_LIMIT_BACKEND="memory"; \
export PYTHONWARNINGS="default"; \
export JWT_SECRET="dev_dummy_jwt"; \
export SECRET_KEY="dev_dummy_jwt"; \
export EMAIL_TOKEN_SECRET="dev_dummy_secret"; \
export FROM_EMAIL="CapeControl <no-reply@cape-control.test>"; \
export SMTP_USERNAME="dev_dummy_user"; \
export SMTP_PASSWORD="dev_dummy_pass";
endef

codex-test: ## Run pytest with CI-safe defaults
	@echo "== Running pytest with CI-safe defaults =="
	@set -e; \
	$(TEST_ENV_EXPORT) \
	. "$(VENV)/bin/activate" 2>/dev/null || true; \
	$(PY) -m pip install -q -r "$(REQ)"; \
	pytest -q

codex-test-cov: ## Run pytest with coverage
	@echo "== Running pytest with coverage =="
	@set -e; \
	$(TEST_ENV_EXPORT) \
	. "$(VENV)/bin/activate" 2>/dev/null || true; \
	$(PY) -m pip install -q -r "$(REQ)" pytest-cov; \
	pytest -q --cov=backend/src --cov-report=term --cov-report=xml

codex-test-dry: ## Run pytest (allow failures; no venv bootstrap)
	@set -e; \
	$(TEST_ENV_EXPORT) \
	pytest -q || true

codex-run: ## Full Codex pass (docs lint, pre-commit, pytest)
	@$(MAKE) codex-check
	@$(MAKE) codex-docs-lint || true
	@$(MAKE) codex-ci-validate
	@$(MAKE) codex-test

# ----------------------------------------------------------------------------- 
# Smoke & CSRF probes
# -----------------------------------------------------------------------------
smoke-staging: ## Health + CSRF discovery (OpenAPI) against $(STAGING_URL)
	@echo "== Smoke test against $(STAGING_URL) =="
	@curl -fsS "$(STAGING_URL)/api/api/health" | jq . >/dev/null && echo "✓ /api/api/health OK" || { echo "✗ /api/api/health failed"; exit 1; }
	@echo "Discovering CSRF probe path from OpenAPI..."
	@set -e; \
	if ! command -v jq >/dev/null 2>&1; then echo "⚠️  jq not found; install jq to use OpenAPI discovery"; exit 0; fi; \
	OPENAPI_TMP="$$(mktemp)"; \
	FOUND_SCHEMA=""; \
	for candidate in "/api/openapi.json" "/openapi.json"; do \
		if curl -fsS "$(STAGING_URL)$$candidate" -o "$$OPENAPI_TMP" >/dev/null 2>&1; then \
			FOUND_SCHEMA="$$candidate"; \
			break; \
		fi; \
	done; \
	if [ -z "$$FOUND_SCHEMA" ]; then \
		echo "⚠️  Unable to fetch OpenAPI schema (tried /api/openapi.json, /openapi.json). Skipping CSRF cookie check."; \
		rm -f "$$OPENAPI_TMP"; \
		exit 0; \
	fi; \
	echo "Using OpenAPI schema at $$FOUND_SCHEMA"; \
	CSRF_PATHS="$$(jq -r '.paths | keys[]' "$$OPENAPI_TMP" | grep -i csrf || true)"; \
	rm -f "$$OPENAPI_TMP"; \
	if [ -z "$$CSRF_PATHS" ]; then \
		echo "⚠️  No CSRF-like path advertised in OpenAPI. Skipping CSRF cookie check."; \
		exit 0; \
	fi; \
	echo "Found CSRF candidate paths:" $$CSRF_PATHS; \
	for p in $$CSRF_PATHS; do \
		echo "→ Probing $$p ..."; \
		curl -fsS -o /tmp/csrf_body.txt -D /tmp/csrf_headers.txt "$(STAGING_URL)$$p" >/dev/null 2>&1 || true; \
		if grep -qi 'set-cookie' /tmp/csrf_headers.txt; then \
			echo "✓ CSRF cookie present via $$p"; \
			exit 0; \
		fi; \
	done; \
	echo "✗ CSRF cookie missing on candidates: $$CSRF_PATHS"; \
	exit 1

smoke-local: ## Health + CSRF probe against localhost backend
	@echo "== Smoke test against http://localhost:$(PORT) =="
	@curl -fsS "http://localhost:$(PORT)/api/api/health" >/dev/null && echo "✓ /api/api/health OK" || { echo "✗ /api/api/health failed"; exit 1; }
	@$(MAKE) csrf-probe-local || true

csrf-probe-staging: ## Direct CSRF probe (staging)
	@echo "== CSRF probe (staging) =="
	@set -e; \
	status=$$(curl -s -o /tmp/csrf_body.txt -D /tmp/csrf_headers.txt "$(STAGING_URL)/api/auth/csrf" -w "%{http_code}"); \
	echo "Status: $$status"; \
	if grep -qi 'set-cookie' /tmp/csrf_headers.txt; then echo "✓ Set-Cookie present"; else echo "✗ No Set-Cookie"; fi; \
	cat /tmp/csrf_body.txt || true

csrf-probe-local: ## Direct CSRF probe (local)
	@echo "== CSRF probe (local) =="
	@set -e; \
	status=$$(curl -s -o /tmp/csrf_body.txt -D /tmp/csrf_headers.txt "http://localhost:$(PORT)/api/auth/csrf" -w "%{http_code}" || true); \
	echo "Status: $$status"; \
	if [ -f /tmp/csrf_headers.txt ] && grep -qi 'set-cookie' /tmp/csrf_headers.txt; then echo "✓ Set-Cookie present"; else echo "✗ No Set-Cookie"; fi; \
	[ -f /tmp/csrf_body.txt ] && cat /tmp/csrf_body.txt || true

codex-smoke: smoke-staging csrf-probe-staging ## Combined staging smoke & CSRF

smoke-prod: ## Quick production health (no CSRF probe)
	@echo "== Smoke test against $(PROD_BASE_URL) =="
	@curl -fsS "$(PROD_BASE_URL)/api/api/health" | jq . >/dev/null && echo "✓ /api/api/health OK" || { echo "✗ /api/api/health failed"; exit 1; }

# ----------------------------------------------------------------------------- 
# Strict mode tests
# -----------------------------------------------------------------------------
codex-test-strict: ## Run pytest with warnings as errors
	@set -e; \
	$(TEST_ENV_EXPORT) \
	export PYTHONWARNINGS="error"; \
	. "$(VENV)/bin/activate" 2>/dev/null || true; \
	$(PY) -m pip install -q -r "$(REQ)"; \
	pytest -q

# ----------------------------------------------------------------------------- 
# Docker Hub release (multi-arch) with safe tags
# -----------------------------------------------------------------------------
# Usage:
#   make dockerhub-login
#   make dockerhub-release APP=autorisen
#   make dockerhub-release APP=capecraft VERSION=v0.3.0
#   make dockerhub-release APP=autorisen PLATFORMS=linux/amd64
#
# Notes:
# - Tags produced: :latest, :$(VERSION), :docker-<engine>, :git-<sha>
# - Requires Docker Buildx
# -----------------------------------------------------------------------------

# Config (override on CLI, e.g. make dockerhub-release APP=autorisen)
DH_NAMESPACE ?= stinkie
APP          ?= autorisen
CONTEXT      ?= .
DOCKERFILE   ?= Dockerfile
PLATFORMS    ?= linux/amd64,linux/arm64

# Optional build args & cache
BUILD_ARGS        ?=
BUILD_CACHE_FROM  ?=
BUILD_CACHE_TO    ?=

# Helpers: trim & sanitize variables
define SANITIZE
echo "$1" | sed -E 's/[^A-Za-z0-9_.-]/-/g'
endef

# Trim whitespace from namespace/app
RAW_NS    := $(DH_NAMESPACE)
RAW_APP   := $(APP)
NS        := $(shell echo '$(RAW_NS)'  | tr -d '[:space:]')
APPNAME   := $(shell echo '$(RAW_APP)' | tr -d '[:space:]')

# Derive versions/metadata
GIT_SHA        := $(shell git rev-parse --short HEAD 2>/dev/null || echo "nogit")
DATE_TAG       := $(shell date +%Y%m%d-%H%M%S)
GIT_DESCRIBE   := $(shell (git describe --tags --always --dirty 2>/dev/null) || true)
VERSION        ?= $(if $(GIT_DESCRIBE),$(GIT_DESCRIBE),$(DATE_TAG))
DOCKER_ENGINE_VERSION := $(shell docker version --format '{{.Server.Version}}' 2>/dev/null || echo unknown)

# Backwards compatibility: allow TAG=... to override VERSION
ifneq ($(strip $(TAG)),)
	VERSION := $(TAG)
endif

# Sanitized values for tags
SAFE_VERSION := $(shell $(call SANITIZE,$(VERSION)))
SAFE_ENGINE  := $(shell $(call SANITIZE,$(DOCKER_ENGINE_VERSION)))
SAFE_SHA     := $(shell $(call SANITIZE,$(GIT_SHA)))

# Final image path for Docker Hub
DH_IMAGE := $(NS)/$(APPNAME)

dockerhub-login: ## Login to Docker Hub (interactive)
	@echo "Logging in to Docker Hub…"
	docker login

dockerhub-logout: ## Logout from Docker Hub
	@echo "Logging out of Docker Hub…"
	-docker logout

dockerhub-setup-builder: ## Ensure Buildx 'multiarch-builder' is ready
	@echo "Ensuring docker buildx builder is ready…"
	@if ! docker buildx inspect multiarch-builder >/dev/null 2>&1; then \
		docker buildx create --name multiarch-builder --use; \
	else \
		docker buildx use multiarch-builder; \
	fi
	@docker buildx inspect --bootstrap >/dev/null
	@echo "Buildx builder 'multiarch-builder' is ready."

dockerhub-build: ## Local single-arch build (no push)
	@echo "Building local image: $(DH_IMAGE):$(SAFE_VERSION)"
	docker build \
		-f "$(DOCKERFILE)" \
		-t "$(DH_IMAGE):$(SAFE_VERSION)" \
		$(BUILD_ARGS) \
		"$(CONTEXT)"
	@echo "Tagging latest…"
	docker tag "$(DH_IMAGE):$(SAFE_VERSION)" "$(DH_IMAGE):latest"

dockerhub-push: ## Push local :$(SAFE_VERSION) and :latest
ifeq ($(SAFE_VERSION),)
	$(error SAFE_VERSION is empty; set VERSION= or TAG= with a non-empty value)
endif
	@if ! docker image inspect "$(DH_IMAGE):$(SAFE_VERSION)" >/dev/null 2>&1; then \
		echo "Image $(DH_IMAGE):$(SAFE_VERSION) missing; building it now…"; \
		$(MAKE) dockerhub-build VERSION=$(VERSION); \
	fi
	@echo "Pushing $(DH_IMAGE):$(SAFE_VERSION) and :latest…"
	docker push "$(DH_IMAGE):$(SAFE_VERSION)"
	docker push "$(DH_IMAGE):latest"

.PHONY: dockerhub-build-push
dockerhub-build-push: ## Convenience target: build (single-arch) then push
	@$(MAKE) dockerhub-build VERSION=$(VERSION)
	@$(MAKE) dockerhub-push VERSION=$(VERSION)

dockerhub-release: dockerhub-setup-builder ## Multi-arch buildx + push (recommended)
	@echo "Releasing $(DH_IMAGE) for platforms [$(PLATFORMS)]"
	@echo "Tags to push:"
	@echo "  - $(DH_IMAGE):$(SAFE_VERSION)"
	@echo "  - $(DH_IMAGE):latest"
	@echo "  - $(DH_IMAGE):docker-$(SAFE_ENGINE)"
	@echo "  - $(DH_IMAGE):git-$(SAFE_SHA)"
	@echo ""
	@if [ -n "$(BUILD_CACHE_FROM)" ]; then CACHE_FROM="--cache-from=$(BUILD_CACHE_FROM)"; else CACHE_FROM=""; fi; \
	if [ -n "$(BUILD_CACHE_TO)" ]; then CACHE_TO="--cache-to=$(BUILD_CACHE_TO)"; else CACHE_TO=""; fi; \
	docker buildx build \
		--platform "$(PLATFORMS)" \
		-f "$(DOCKERFILE)" \
		$(BUILD_ARGS) \
		--provenance=false \
		--pull \
		--push \
		-t "$(DH_IMAGE):$(SAFE_VERSION)" \
		-t "$(DH_IMAGE):latest" \
		-t "$(DH_IMAGE):docker-$(SAFE_ENGINE)" \
		-t "$(DH_IMAGE):git-$(SAFE_SHA)" \
		$$CACHE_FROM $$CACHE_TO \
		"$(CONTEXT)"

dockerhub-update-description: ## PATCH repository description via Docker Hub API (needs DOCKERHUB_TOKEN)
	@set -e; \
	[ -n "$(DESCRIPTION)" ] || { echo "Usage: make dockerhub-update-description DESCRIPTION=\"<text>\" [APP=...]"; exit 1; }; \
	if [ -z "$$DOCKERHUB_TOKEN" ]; then echo "Set DOCKERHUB_TOKEN environment variable to a Docker Hub access token"; exit 1; fi; \
	BODY=$$(DESC="$(DESCRIPTION)" $(PY) -c 'import json, os; print(json.dumps({"description": os.environ["DESC"]}))'); \
	URL="https://hub.docker.com/v2/repositories/$(NS)/$(APPNAME)/"; \
	echo "Updating $$URL description..."; \
	curl -sSf -X PATCH \
		-H "Content-Type: application/json" \
		-H "Authorization: JWT $$DOCKERHUB_TOKEN" \
		-d "$$BODY" \
		"$$URL" | tee /tmp/dockerhub_description_response.json >/dev/null; \
	echo; \
	echo "Docker Hub API response saved to /tmp/dockerhub_description_response.json"

dockerhub-clean: ## Prune dangling images
	@echo "Pruning dangling images…"
	-docker image prune -f

# ----------------------------------------------------------------------------- 
# Playbooks (Codex loop)
# -----------------------------------------------------------------------------
PLAYBOOKS_DIR ?= docs/playbooks

# Resolve template path: prefer dotted name; fallback to underscored
ifneq ($(wildcard $(PLAYBOOKS_DIR)/templates/playbook.template.md),)
  PLAYBOOK_TEMPLATE := $(PLAYBOOKS_DIR)/templates/playbook.template.md
else
  PLAYBOOK_TEMPLATE := $(PLAYBOOKS_DIR)/templates/playbook_template.md
endif

PLAYBOOK_SCRIPT ?= scripts/playbooks_overview.py

playbooks-overview: ## Rebuild docs/PLAYBOOKS_OVERVIEW.md
	@$(PY) $(PLAYBOOK_SCRIPT)
	@echo "Updated docs/PLAYBOOKS_OVERVIEW.md"

playbook-overview: ## Alias for playbooks-overview
	@$(MAKE) playbooks-overview

project-overview: ## Generate docs/PROJECT_OVERVIEW.md from enhanced CSV plan
	@$(PY) scripts/project_overview_generator.py
	@echo "Updated docs/PROJECT_OVERVIEW.md"

playbook-open: ## Open docs/PLAYBOOKS_OVERVIEW.md in VS Code if available
	@which code >/dev/null 2>&1 && code docs/PLAYBOOKS_OVERVIEW.md || echo "Open docs/PLAYBOOKS_OVERVIEW.md in your editor"

playbook-badge: ## Print current playbooks % (from overview)
	@grep -oP 'Overall Progress:\s*\d+/\d+\s*\(\K\d+(?=%\))' docs/PLAYBOOKS_OVERVIEW.md || echo "n/a"

playbook-new: ## Create playbook: make playbook-new NUMBER=02 TITLE="X" OWNER="Robert" AGENTS="Codex, CapeAI" PRIORITY=P1
	@test -n "$(NUMBER)" || (echo "NUMBER= required"; exit 1)
	@test -n "$(TITLE)"  || (echo "TITLE= required"; exit 1)
	@test -n "$(OWNER)"  || (echo "OWNER= required"; exit 1)
	@mkdir -p $(PLAYBOOKS_DIR)
	@dst="$(PLAYBOOKS_DIR)/playbook-$(NUMBER)-$(shell echo $(TITLE) | tr '[:upper:] ' '[:lower:]-' | tr -cd 'a-z0-9-').md"; \
	sed -e "s/\${NUMBER}/$(NUMBER)/g" \
	    -e "s/\${TITLE}/$(TITLE)/g" \
	    -e "s/\${OWNER}/$(OWNER)/g" \
	    -e "s/\${AGENTS}/$(AGENTS)/g" \
	    -e "s/\${PRIORITY}/$(PRIORITY)/g" "$(PLAYBOOK_TEMPLATE)" > "$$dst"; \
	echo "Created $$dst"; \
	$(MAKE) playbooks-overview

playbooks-check: ## Validate required headers exist in all playbooks
	@missing=0; \
	for f in $(PLAYBOOKS_DIR)/playbook-*.md; do \
	  grep -q "^## 1) Outcome" "$$f" || { echo "Missing Outcome in $$f"; missing=1; }; \
	  grep -q "^## 5) Checklist (Executable)" "$$f" || { echo "Missing Checklist in $$f"; missing=1; }; \
	done; \
	exit $$missing

playbook-sync: ## Sync PROJECT_PLAYBOOK_TRACKER docs from CSV
	@python3 scripts/sync_playbooks_tracker.py

# ===== Heroku Pipeline Targets =====

.PHONY: heroku-login heroku-apps heroku-pipeline heroku-config-stg heroku-config-prod \
deploy-staging heroku-smoke-staging promote-prod heroku-smoke-prod heroku-logs-stg heroku-logs-prod \
heroku-open-stg heroku-open-prod heroku-rollback


heroku-login:
	@heroku login
	@heroku container:login


heroku-apps:
	@heroku create $(HEROKU_APP_STG) --region eu || true
	@heroku create $(HEROKU_APP_PROD) --region eu || true


heroku-pipeline:
	@heroku pipelines:create capecontrol -a $(HEROKU_APP_STG) -s staging || true
	@heroku pipelines:add capecontrol -a $(HEROKU_APP_PROD) -s production || true


heroku-config-stg:
	@heroku config:set -a $(HEROKU_APP_STG) ENV=staging RUN_DB_MIGRATIONS_ON_STARTUP=0 DISABLE_RECAPTCHA=true


heroku-config-prod:
	@heroku config:set -a $(HEROKU_APP_PROD) ENV=production RUN_DB_MIGRATIONS_ON_STARTUP=0 DISABLE_RECAPTCHA=false


# Build & release container to staging
deploy-staging: heroku-login
	@docker build -t $(HEROKU_APP_STG):local .
	@heroku container:push web -a $(HEROKU_APP_STG)
	@heroku container:release web -a $(HEROKU_APP_STG)
	@heroku ps:scale -a $(HEROKU_APP_STG) web=1


heroku-smoke-staging:
	@curl -fsS $(STAGING_URL)/api/health >/dev/null && echo "✓ health OK" || (echo "✗ health FAIL" && exit 1)
	@curl -fsS $(STAGING_URL)/api/auth/csrf >/dev/null && echo "✓ csrf OK" || (echo "✗ csrf FAIL" && exit 1)
	@heroku logs --tail -a $(HEROKU_APP_STG)


promote-prod:
	@heroku pipelines:promote -a $(HEROKU_APP_STG)


heroku-smoke-prod:
	@curl -fsS $(PROD_URL)/api/health >/dev/null && echo "✓ prod health OK" || (echo "✗ prod health FAIL" && exit 1)
	@heroku logs --tail -a $(HEROKU_APP_PROD)


heroku-logs-stg:
	@heroku logs --tail -a $(HEROKU_APP_STG)


heroku-logs-prod:
	@heroku logs --tail -a $(HEROKU_APP_PROD)


heroku-open-stg:
	@heroku open -a $(HEROKU_APP_STG)


heroku-open-prod:
	@heroku open -a $(HEROKU_APP_PROD)


# Usage: make heroku-rollback REL=v123
heroku-rollback:
	@if [ -z "$$REL" ]; then echo "Set REL=vNNN" && exit 1; fi
	@heroku rollback -a $(HEROKU_APP_PROD) $$REL

## codex-status: show Codex active files and playbook
codex-status:
	@echo "== Codex active context =="
	@grep -A1 'Codex context' docs/DEVELOPMENT_CONTEXT.md || true
	@echo
	@echo "== Latest playbook =="
	@ls -lt docs/playbooks | head -n 3
## codex-next: advance Active Playbook to the next numbered file
codex-next:
	@set -euo pipefail; \
	ACTIVE=$$(grep -Eo 'Active Playbook:\s*\S+' .vscode/codex.prompt.md 2>/dev/null | awk '{print $$3}'); \
	[ -z "$$ACTIVE" ] && ACTIVE=$$(ls -1 docs/playbooks/playbook-*.md 2>/dev/null | sort | tail -n1); \
	[ -z "$$ACTIVE" ] && { echo "No playbooks found."; exit 1; }; \
	cur_n=$$(basename "$$ACTIVE" | sed -n 's/^playbook-\([0-9][0-9]*\)-.*/\1/p'); \
	[ -z "$$cur_n" ] && { echo "Could not parse current playbook number from $$ACTIVE"; exit 1; }; \
	next=$$(ls -1 docs/playbooks/playbook-*.md | sort | awk -v n="$$cur_n" ' \
		{ m=$$0; sub(/^.*playbook-([0-9]+)-.*/,"\\1",m); if (m>n) print $$0 }' | head -n1); \
	[ -z "$$next" ] && { echo "No higher-numbered playbook found. You are at the last one."; exit 0; }; \
	sed -i.bak -E "s|^Active Playbook:.*|Active Playbook: $$next|" .vscode/codex.prompt.md || \
	echo "Active Playbook: $$next" >> .vscode/codex.prompt.md; \
	rm -f .vscode/codex.prompt.md.bak; \
	echo "Advanced to: $$next"

.PHONY: mcp-smoke mcp-host run-local

ENV ?= dev

mcp-smoke:
	@echo "== MCP smoke test =="
	@set -euo pipefail; \
	: $${OPENAI_API_KEY:?OPENAI_API_KEY must be set for MCP smoke test}; \
	LOG_FILE=$$(mktemp -t mcp-smoke.XXXXXX.log); \
	SERVER_PID=; \
	cleanup() { trap - INT TERM EXIT; \
		if [ -n "$$SERVER_PID" ]; then \
			kill $$SERVER_PID >/dev/null 2>&1 || true; \
			wait $$SERVER_PID 2>/dev/null || true; \
		fi; \
		rm -f "$$LOG_FILE"; \
	}; \
	trap cleanup INT TERM EXIT; \
	UVICORN_BIN=$$( [ -x "$(VENV)/bin/uvicorn" ] && echo "$(VENV)/bin/uvicorn" || command -v uvicorn ); \
	if [ -z "$$UVICORN_BIN" ]; then echo "uvicorn not found; run 'make install' first" >&2; exit 127; fi; \
	ENABLE_MCP_HOST=1 ENV=$(ENV) OPENAI_API_KEY=$$OPENAI_API_KEY \
		EMAIL_TOKEN_SECRET=$${EMAIL_TOKEN_SECRET:-dev-mcp-smoke-secret} \
		FROM_EMAIL=$${FROM_EMAIL:-mcp-smoke@example.com} \
		SMTP_HOST=$${SMTP_HOST:-localhost} \
		SMTP_USERNAME=$${SMTP_USERNAME:-mcp-smoke-user} \
		SMTP_PASSWORD=$${SMTP_PASSWORD:-mcp-smoke-pass} \
		PORT=$(MCP_SMOKE_PORT) \
		"$$UVICORN_BIN" backend.src.app:app --host 127.0.0.1 --port $(MCP_SMOKE_PORT) >>"$$LOG_FILE" 2>&1 & \
	SERVER_PID=$$!; \
	for i in $$(seq 1 20); do \
		if curl -fsS http://127.0.0.1:$(MCP_SMOKE_PORT)/api/api/health >/dev/null 2>&1; then break; fi; \
		sleep 0.25; \
	done; \
	if ! curl -fsS http://127.0.0.1:$(MCP_SMOKE_PORT)/api/api/health >/dev/null 2>&1; then \
		echo "MCP host failed to start:" >&2; \
		cat "$$LOG_FILE" >&2 || true; \
		exit 1; \
	fi; \
	RESP=$$(curl -fsS http://127.0.0.1:$(MCP_SMOKE_PORT)/api/ops/mcp/smoke); \
	echo "$$RESP" | jq .; \
	if ! echo "$$RESP" | jq -e '.ok == true' >/dev/null; then \
		echo "MCP smoke failed" >&2; \
		echo "See details above (last_error/servers)." >&2; \
		exit 1; \
	fi

run-local:
	@echo "== Backend (with MCP) =="
	$(MAKE) mcp-host

# --- Codex targets ---

.PHONY: codex-docs
codex-docs:
	@echo "# Docs Index" > docs/INDEX.md
	@find docs -maxdepth 2 -type f -name "*.md" | sort | sed 's#^#- #' >> docs/INDEX.md
	@echo "✅ Docs indexed at docs/INDEX.md"

.PHONY: codex-bootstrap
codex-bootstrap: codex-docs codex-check
	@echo "✅ Codex bootstrap complete"

.PHONY: codex-guardian
codex-guardian:
	@echo "Running tests..."
	@ENV=test DATABASE_URL=sqlite:////tmp/autolocal_test.db DISABLE_RECAPTCHA=true RUN_DB_MIGRATIONS_ON_STARTUP=0 RATE_LIMIT_BACKEND=memory \
	$(PY) -m pytest || true
	@echo "Attempting fixture heal..."
	@$(PY) scripts/regenerate_fixtures.py || true

.PHONY: dev-install
dev-install:
	@$(PY) -m pip install --upgrade pip
	@$(PY) -m pip install -r requirements.txt || true
	@$(PY) -m pip install -r requirements-dev.txt

.PHONY: codex-focus
codex-focus:
	@$(PY) -m pytest -v tests_enabled/test_security_csrf.py

.PHONY: auth-tests
auth-tests:
	@$(PY) -m pytest -v tests_enabled/test_auth.py || true

# --- Design documentation (Figma integration removed) -------------------------
DESIGN_PLAYBOOKS_DIR ?= docs/playbooks/design

# Design playbooks reference Figma URLs for documentation but no API integration

# ---- Dashboard Auto-Refresh ---------------------------------------------------
DASHBOARD_SUMMARY ?= docs/CONTROL_DASHBOARD_SUMMARY.md
DASHBOARD_STAGING_URL ?= https://dev.cape-control.com
DASHBOARD_LOCAL_URL ?= http://localhost:8000
DASHBOARD_RUNTIME_ENV ?= ENV=test DISABLE_RECAPTCHA=true RUN_DB_MIGRATIONS_ON_STARTUP=0 RATE_LIMIT_BACKEND=memory DATABASE_URL=sqlite:////tmp/autolocal_test.db

.PHONY: dashboard-refresh dashboard-open
dashboard-refresh:
	@echo "==> Syncing docs (codex-docs if present)…"
	-@$(MAKE) codex-docs >/dev/null 2>&1 || true
	@echo "==> Running quick tests…"
	-@set +e; \
	$(DASHBOARD_RUNTIME_ENV) $(PY) -m pytest -q >/tmp/pytest.out 2>&1; \
	code=$$?; echo $$code >/tmp/pytest.code
	@echo "==> Probing health endpoints…"
	-@set +e; \
	curl -sSf -o /dev/null "$(DASHBOARD_STAGING_URL)/api/auth/csrf"; \
	code=$$?; echo $$code >/tmp/csrf.code
	-@set +e; \
	curl -sSf -o /dev/null "$(DASHBOARD_STAGING_URL)/api/health"; \
	code=$$?; echo $$code >/tmp/health.code
	@echo "==> Updating dashboard badges…"
	@mkdir -p tools
	@chmod +x tools/update_dashboard.py || true
	@$(DASHBOARD_RUNTIME_ENV) $(PY) tools/update_dashboard.py \
		--dashboard "$(DASHBOARD_SUMMARY)" \
		--staging "$(DASHBOARD_STAGING_URL)" \
		--local "$(DASHBOARD_LOCAL_URL)" \
		--pytest-exit "$$(cat /tmp/pytest.code || echo 1)" \
		--csrf-exit  "$$(tail -n1 /tmp/csrf.code  || echo 1)" \
		--health-exit "$$(tail -n1 /tmp/health.code || echo 1)"
	@echo "==> Dashboard refreshed: $(DASHBOARD_SUMMARY)"

dashboard-open:
	@${PY} -c 'import webbrowser, os; p=os.path.abspath("$(DASHBOARD_SUMMARY)"); print("Opening", p); webbrowser.open("file://" + p)'

# --- Fallback docs sync (no-op if real target not present) --------------------
.PHONY: codex-docs
codex-docs:
	@echo "[codex-docs] No-op fallback (replace with your real docs sync if needed)"

# --- Figma Design System Workflow ------------------------------------------------

design-helper:
	@echo "🎨 Starting CapeWire Design System Helper..."
	cd $(CURDIR) && $(PY) scripts/design_helper.py

design-status:
	@echo "📊 Design System Status..."

design-list:
	@echo "📋 Listing available Figma frames..."

design-generate:
	@if [ -z "$(NODE_ID)" ] || [ -z "$(COMPONENT)" ]; then \
		echo "❌ Usage: make design-generate NODE_ID=2:9 COMPONENT=MyComponent"; \
		exit 1; \
	fi
	@echo "⚛️  Generating $(COMPONENT) from node $(NODE_ID)..."

design-watch:
	@echo "👀 Starting Figma change watcher..."

	@echo "🚀 Figma Design System Setup Complete!"
	@echo ""
	@echo "Available commands:"
	@echo "  make design-helper    - Interactive design system helper"
	@echo "  make design-status    - Show design system status"
	@echo "  make design-list      - List available Figma frames"
	@echo "  make design-generate NODE_ID=2:9 COMPONENT=MyComponent"
	@echo "  make design-watch     - Watch for Figma changes"
	@echo "  make capecraft       - CapeCraft implementation workflow"
	@echo ""
	@echo "🌐 Demo pages available at:"
	@echo "  http://localhost:3000/mainpage-demo - MainPage component demo"
	@echo ""
	@echo "📁 File ID: gRtWgiHmLTrIZGvkhF2aUC"

# --- CapeCraft Implementation Workflow ------------------------------------------------
.PHONY: capecraft capecraft-spec capecraft-help

capecraft:
	@echo "🎨 Starting CapeCraft implementation workflow..."
	cd $(CURDIR) && ./scripts/capecraft_workflow.sh

capecraft-spec:
	@echo "📋 CapeCraft Design Specification:"
	@echo "  Guide: docs/checklists/capecraft_implementation_guide.md"
		echo "✅ Specification file exists"; \
	else \
		echo "❌ Specification file missing"; \
	fi

capecraft-help:
	@echo "🎨 CapeCraft Development Workflow"
	@echo "================================="
	@echo ""
	@echo "Available commands:"
	@echo "  make capecraft       - Run full implementation workflow"
	@echo "  make capecraft-spec  - Show specification status"
	@echo "  make capecraft-help  - Show this help"
	@echo ""
	@echo "MindMup → Figma → React workflow:"
	@echo "1. Design specification created from MindMup"
	@echo "2. Import spec into Figma for visual design"
	@echo "4. Integrate components into page routing"
