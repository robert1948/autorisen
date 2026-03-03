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

TASK_CAPSULE_DIR := docs/task-capsules
TASK_CAPSULE_TEMPLATE := docs/task-capsule-template.md
PROJECT_PLAN_CSV := docs/project-plan.csv


PYTHONPATH ?= $(CURDIR)
export PYTHONPATH


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
# Makefile — AutoLocal/CapeControl v0.2.5
# Production-ready FastAPI + React SaaS platform with enhanced ChatKit & Payment integration
# Updated: November 14, 2025
# =============================================================================

SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help

# ----------------------------------------------------------------------------- 
# Core vars
# -----------------------------------------------------------------------------
VENV := .venv
PY := $(VENV)/bin/python
PIP := $(PY) -m pip
REQ := requirements.txt

# App version (source of truth: client/package.json)
APP_VERSION_RAW := $(shell python3 -c "import json; print(json.load(open('client/package.json'))['version'])" 2>/dev/null)
APP_VERSION := $(if $(APP_VERSION_RAW),v$(APP_VERSION_RAW),unknown)


# Git SHA embedded into container images (for /api/version + certification)
GIT_SHA := $(shell git rev-parse HEAD 2>/dev/null || echo unknown)

# Build metadata (for /api/version)
BUILD_EPOCH := $(shell date +%s)
APP_BUILD_VERSION := $(shell cat VERSION 2>/dev/null || echo $(GIT_SHA))

IMAGE ?= capecontrol:local
PORT ?= 8000

HEROKU_APP      ?= capecraft
HEROKU_APP_NAME ?= $(HEROKU_APP)

# ----------------------------------------------------------------------------- 
# Safety gate: production operations require explicit opt-in
# ----------------------------------------------------------------------------- 
ALLOW_PROD ?= 0

.PHONY: require-prod
require-prod: ## Guard: require ALLOW_PROD=1 for production actions
	@if [ "$(ALLOW_PROD)" != "1" ]; then \
		echo "❌ Refusing production action (locked). Re-run with ALLOW_PROD=1 (only when explicitly instructed)."; \
		exit 2; \
	fi

# Domains
PROD_BASE_URL ?= https://cape-control.com
PROD_URL      ?= https://cape-control.com

# Docs inputs for sitemap
SITEMAP_PROD_TXT ?= docs/sitemap.prod.txt

# Output static sitemap (served by Vite from / if present)
PUBLIC_DIR ?= client/public
SITEMAP_XML ?= sitemap.xml

# Crawl
CRAWL_OUT ?= docs/crawl
CRAWL_TOOL ?= tools/crawl_sitemap.py

# Test DB (single source of truth)
TEST_DB_URL      ?= sqlite:////tmp/autolocal_test.db
TEST_PG_DB_URL   ?= postgresql://testuser:testpass@localhost:5434/testdb

# ----------------------------------------------------------------------------- 
# PHONY index (single, authoritative)
# -----------------------------------------------------------------------------
.PHONY: help project-info venv install format lint test docker-build docker-run docker-push \
	deploy deploy-heroku heroku-logs heroku-run-migrate \
	github-update clean plan-validate plan-open \
	migrate-up migrate-revision \
	sitemap-generate-prod verify-sitemap verify-sitemap-prod \
	crawl-local crawl-prod crawl sitemap-svg \
	agents-new agents-validate agents-test agents-run \
	codex-check codex-open codex-docs-lint codex-docs-fix codex-ci-validate \
	codex-plan-diff codex-plan-apply codex-test-heal codex-test codex-test-pg codex-test-cov codex-test-dry codex-run \
	smoke-local smoke-prod \
	payments-checkout websocket-test payment-test chatkit-dev \
	dockerhub-login dockerhub-logout dockerhub-setup-builder dockerhub-build dockerhub-push dockerhub-build-push \
	dockerhub-release dockerhub-update-description dockerhub-clean \
	playbooks-overview playbook-overview playbook-open playbook-badge playbook-new playbooks-check \
	design-sync design-validate

# ----------------------------------------------------------------------------- 
# Help (auto-docs)
# -----------------------------------------------------------------------------
help: ## List Make targets (auto-docs)
	@awk 'BEGIN {FS=":.*##"; printf "\n\033[1mMake targets\033[0m\n"} /^[a-zA-Z0-9_.-]+:.*##/ { printf "  \033[36m%-30s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

# =============================================================================
# 📖 DOCUMENTATION MANAGEMENT
# =============================================================================

docs: ## Open documentation hub and quick reference
	@echo "📚 Opening CapeControl Documentation Hub..."
	@if command -v code > /dev/null 2>&1; then \
		code docs/README.md; \
		code docs/quick-reference.md; \
	else \
		echo "📄 Documentation available at:"; \
		echo "  • docs/README.md (main hub)"; \
		echo "  • docs/quick-reference.md (commands)"; \
		echo "  • docs/deployment-environments.md (environments)"; \
		echo "  • docs/developer-setup-checklist.md (onboarding)"; \
	fi

docs-update: ## Update documentation after changes
	@echo "📝 Documentation update checklist:"
	@echo "  1. ✅ Update relevant .md files"
	@echo "  2. ✅ Test any command changes"
	@echo "  3. ✅ Commit with descriptive message"
	@echo "  4. ✅ Notify team via Slack/email"
	@echo ""
	@echo "📋 Quick update workflow:"
	@echo "  make docs           # Open documentation"
	@echo "  # Edit files..."
	@echo "  git add docs/"
	@echo "  git commit -m \"docs: update [specific change]\""
	@echo "  git push"

docs-workspace: ## Open VS Code workspace with documentation tasks
	@if [ -f .vscode/capecontrol.code-workspace ]; then \
		code .vscode/capecontrol.code-workspace; \
		echo "🚀 VS Code workspace opened with pre-configured tasks"; \
	else \
		echo "❌ VS Code workspace not found. Creating..."; \
		make docs; \
		echo "💡 Use 'code .vscode/capecontrol.code-workspace' after setup"; \
	fi

project-info: ## Show current project version and status information
	@echo ""
	@echo "\U0001f680 \033[1mAutoLocal/CapeControl Project Information\033[0m"
	@echo "\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501"
	@echo "\U0001f4ca Version: $(APP_VERSION)"
	@echo "\U0001f3af Focus: Stripe billing, usage metering, ops hardening"
	@echo ""
	@echo "\U0001f517 \033[34mKey Links:\033[0m"
	@echo "   \u2022 Production (Heroku: $(HEROKU_APP)): $(PROD_BASE_URL)"
	@echo "   \u2022 Docker Hub: stinkie/capecontrol:$(APP_VERSION)"
	@echo ""
	@$(PY) scripts/project_info.py
	@echo ""
	@git log --oneline -5 2>/dev/null || echo "\U0001f4dd Git history: Not available"
	@echo ""

ops-release-all: ## Sync plan, fix docs, show info, push to git, and release to Heroku & DockerHub
	@echo "🚀 Starting full release sequence..."
	@$(MAKE) codex-plan-apply
	@$(MAKE) codex-docs-fix || echo "⚠️  Docs linting had issues (auto-fix applied where possible). Continuing..."
	@$(MAKE) project-info
	@echo "📝 Git Status:"
	@git status --short
	@echo ""
	@echo "⚠️  Ready to push to GitHub and deploy to Heroku + DockerHub?"
	@echo "    Ensure all changes are committed."
	@echo "    This will:"
	@echo "    1. git push origin main"
	@echo "    2. make deploy (Capecraft production)"
	@echo "    3. make dockerhub-release"
	@echo ""
	@read -p "Press Enter to continue or Ctrl+C to cancel..." _
	@echo "📦 Pushing to GitHub..."
	@git push origin main
	@echo "🚀 Deploying to Heroku (Capecraft)..."
	@$(MAKE) deploy ALLOW_PROD=1
	@echo "🐳 Releasing to DockerHub..."
	@$(MAKE) dockerhub-release
	@echo "✅ Full release sequence completed!"

# ----------------------------------------------------------------------------- 
# Python env / dev tasks
# -----------------------------------------------------------------------------
venv: ## Create a virtualenv in $(VENV)
	@if [ -d "$(VENV)" ]; then \
		echo "Virtualenv $(VENV) already exists"; \
	else \
		python3 -m venv $(VENV); \
		echo "Created virtualenv $(VENV)"; \
	fi

doctor: ## Validate development environment prerequisites
	@echo "== Running Doctor Check =="
	@if [ ! -d "$(VENV)" ]; then echo "❌ Virtualenv missing. Run 'make venv'"; exit 1; fi
	@if [ ! -x "$(PY)" ]; then echo "❌ Python executable not found in venv"; exit 1; fi
	@echo "✅ Virtualenv found at $(VENV)"
	@$(PY) --version
	@echo "✅ Environment looks healthy"

install: venv ## Install project dependencies (uses $(REQ) if present)
	@echo "Installing dependencies..."
	@if [ -f "$(REQ)" ]; then \
		$(PIP) install -r $(REQ); \
	else \
		$(PIP) install -e . || true; \
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
# Enhanced WebSocket & Payment Development (v0.2.5)
# -----------------------------------------------------------------------------
websocket-test: ## Test WebSocket functionality with health monitoring
	@echo "Testing WebSocket service..."
	@$(VENV)/bin/python -c "\
import asyncio; \
import websockets; \
import json; \
from datetime import datetime; \
async def test_websocket(): \
    uri = 'ws://localhost:8000/ws/chat/test-user'; \
    try: \
        async with websockets.connect(uri) as websocket: \
            await websocket.send(json.dumps({'type': 'ping', 'timestamp': datetime.now().isoformat()})); \
            response = await websocket.recv(); \
            print('✅ WebSocket health check passed:', response); \
            await websocket.send(json.dumps({'type': 'message', 'content': 'Test message from Makefile'})); \
            response = await websocket.recv(); \
            print('✅ Message sending test passed:', response); \
    except Exception as e: \
        print('❌ WebSocket test failed:', str(e)); \
asyncio.run(test_websocket())"

payment-test: ## Test PayFast integration endpoints
	@echo "Testing PayFast payment endpoints..."
	@curl -s -X POST http://localhost:8000/api/payments/payfast/checkout \
		-H "Content-Type: application/json" \
		-d '{"amount": 100.00, "item_name": "Test Product", "return_url": "http://localhost:3000/success"}' \
		|| echo "❌ PayFast checkout test failed"
	@echo ""
	@curl -s http://localhost:8000/api/payments/methods || echo "❌ Payment methods test failed"

chatkit-dev: ## Start development mode with WebSocket debugging
	@echo "Starting ChatKit development mode with enhanced WebSocket debugging..."
	@ENV=dev DEBUG=true WEBSOCKET_DEBUG=true $(VENV)/bin/uvicorn backend.src.app:app \
		--host 0.0.0.0 --port 8000 --reload --log-level debug

# ----------------------------------------------------------------------------- 
# Docker (local) 
# -----------------------------------------------------------------------------
docker-build: ## Build docker image (IMAGE=$(IMAGE))
	@echo "Building docker image $(IMAGE)..."
	@for i in 1 2 3; do \
		if docker build --build-arg GIT_SHA=$(GIT_SHA) -t $(IMAGE) .; then \
			echo "Docker build succeeded on attempt $$i"; exit 0; \
		fi; \
		echo "Docker build failed (attempt $$i). Retrying in 5s..."; sleep 5; \
	done; \
	echo "Docker build failed after retries"; exit 1

docker-run: ## Run docker image locally (exposes $(PORT))
	@echo "Running docker image $(IMAGE) on port $(PORT)..."
	docker run --rm -p $(PORT):$(PORT) \
		--env PORT=$(PORT) \
		--env EMAIL_TOKEN_SECRET="$(EMAIL_TOKEN_SECRET)" \
		--env FROM_EMAIL="$(FROM_EMAIL)" \
		--env SMTP_USERNAME="$(SMTP_USERNAME)" \
		--env SMTP_PASSWORD="$(SMTP_PASSWORD)" \
		--env SMTP_HOST="$(SMTP_HOST)" \
		--env SMTP_PORT="$(SMTP_PORT)" \
		--env SMTP_TLS="$(SMTP_TLS)" \
		--env ENV=dev \
		$(IMAGE)

docker-push: ## Push local image tag to $(REGISTRY) (set REGISTRY=…)
	@if [ -z "$(REGISTRY)" ]; then \
		echo "Please set REGISTRY or use deploy-heroku for Heroku (set HEROKU_APP_NAME)."; exit 1; \
	fi
	@echo "Tagging and pushing to $(REGISTRY)/$(IMAGE)..."
	docker tag $(IMAGE) $(REGISTRY)/$(IMAGE)
	docker push $(REGISTRY)/$(IMAGE)

# ----------------------------------------------------------------------------- 
# Heroku container deploy (direct to Capecraft)
# Workflow: Local Docker → CI green → Deploy to Capecraft (production)
# Staging (autorisen) eliminated — use local Docker + Postgres for integration tests
# -----------------------------------------------------------------------------
deploy-heroku: deploy ## Alias: deploy to production (capecraft)

.PHONY: deploy verify-deploy test-backend build-client ship ship-log

# Where to write evidence logs (override: make ship-log EVIDENCE_DIR=/path)
EVIDENCE_DIR ?= /tmp

test-backend: ## Run backend tests (pytest)
	@set -euo pipefail; \
	./.venv/bin/python -m pytest -q

build-client: ## Install client deps and build
	@set -euo pipefail; \
	npm -C client ci --no-audit --fund=false; \
	npm -C client run build

ship: test-backend build-client deploy verify-deploy ## Test, build, deploy, and verify production
	@echo "ship complete"

ship-log: ## Run ship and tee output to a timestamped evidence log
	@set -euo pipefail; \
	TS="$$(date +%Y%m%d_%H%M%S)"; \
	LOG="$(EVIDENCE_DIR)/ship_capecraft_$${TS}.log"; \
	echo "[evidence] writing $$LOG"; \
	{ $(MAKE) ship ALLOW_PROD=1; } 2>&1 | tee "$$LOG"; \
	echo "[evidence] saved $$LOG"

deploy: require-prod docker-build ## Build/push/release to production (capecraft) with guardrails
	@scripts/deploy_guard.sh $(HEROKU_APP)
	@echo "🔐 Logging in to Heroku Container Registry..."
	@LOGIN_OK=0; \
	for i in 1 2 3; do \
		if heroku container:login >/dev/null 2>&1; then echo "✅ Login successful"; LOGIN_OK=1; break; fi; \
		echo "⚠️  Login failed (attempt $$i/3). Retrying in 5s..."; sleep 5; \
	done; \
	if [ "$$LOGIN_OK" -ne 1 ]; then echo "❌ Login failed after retries"; exit 1; fi
	@echo ""
	@echo "🚀 === DEPLOYING TO PRODUCTION ($(HEROKU_APP)) ==="
	@echo "🏷️  Tagging image for production registry..."
	docker tag $(IMAGE) registry.heroku.com/$(HEROKU_APP)/web
	@echo "📤 Pushing image to production registry..."
	@for i in 1 2 3; do \
		if docker push registry.heroku.com/$(HEROKU_APP)/web; then echo "✅ Push successful"; break; fi; \
		echo "⚠️  Push failed (attempt $$i/3). Retrying in 10s..."; sleep 10; \
		[ $$i -eq 3 ] && { echo "❌ Push failed after retries"; exit 1; } || true; \
	done
	@echo "🚀 Releasing container..."
	@for i in 1 2 3; do \
		if heroku container:release web --app $(HEROKU_APP); then echo "✅ Release successful"; break; fi; \
		echo "⚠️  Release failed (attempt $$i/3). Retrying in 10s..."; sleep 10; \
		[ $$i -eq 3 ] && { echo "❌ Release failed after retries"; exit 1; } || true; \
	done
	@echo "✅ Production deployment completed! App URL: $(PROD_BASE_URL)"

verify-deploy: ## Verify production release, version, and DB revision
	@set -euo pipefail; \
	export HEROKU_PAGER=cat; \
	timeout 30 heroku releases -a $(HEROKU_APP) | head -n 8; \
	PROD_BASE="$$(heroku apps:info -a $(HEROKU_APP) | awk -F': ' '/Web URL/{print $$2}' | tr -d ' ')"; \
	PROD_BASE="$${PROD_BASE%/}"; \
	echo "Production base: $$PROD_BASE"; \
	curl -sS -H "Cache-Control: no-cache" "$${PROD_BASE}/api/version?ts=$$(date +%s)" | python3 -m json.tool || true; \
	timeout 30 heroku pg:psql -a $(HEROKU_APP) -c "SELECT version_num FROM alembic_version;"

heroku-logs: ## Tail Heroku logs for $(HEROKU_APP)
	@echo "📋 Tailing logs for $(HEROKU_APP)..."
	heroku logs --tail --app $(HEROKU_APP)

heroku-shell: ## Open bash shell in Heroku container
	@echo "🐚 Opening shell in $(HEROKU_APP)..."
	heroku run bash --app $(HEROKU_APP)

heroku-run-migrate: ## Run database migrations on Heroku
	@echo "🗃️  Running migrations on $(HEROKU_APP)..."
	heroku run --app $(HEROKU_APP) -- python -m alembic -c backend/alembic.ini upgrade head

heroku-config-push: ## Push local .env to Heroku config (be careful!)
	@if [ ! -f .env ]; then echo "❌ .env file not found"; exit 1; fi
	@echo "⚠️  Pushing .env to Heroku config for $(HEROKU_APP)..."
	@read -p "Are you sure? This will overwrite Heroku config vars [y/N]: " confirm && [ "$$confirm" = "y" ] || exit 1
	heroku config:push --app $(HEROKU_APP)

heroku-status: ## Check Heroku app status and health
	@echo "🔍 Checking status of $(HEROKU_APP)..."
	heroku ps --app $(HEROKU_APP)
	@echo "🔍 Health check..."
	@curl -f -s $(PROD_BASE_URL)/api/health || echo "❌ Health check failed"
	@echo ""
	@curl -f -s $(PROD_BASE_URL)/api/version || echo "⚠️  Version endpoint not available"

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

plan-open: ## Open project plan sources (CSV + Markdown)
	@if command -v code >/dev/null 2>&1; then \
		code docs/autorisen_project_plan.csv docs/Master_ProjectPlan.md; \
	else \
		echo "Open docs/autorisen_project_plan.csv and docs/Master_ProjectPlan.md in your editor."; \
	fi

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

verify-sitemap-prod: ## Curl-check all prod routes
	@$(MAKE) verify-sitemap FILE="$(SITEMAP_PROD_TXT)" BASE="$(PROD_BASE_URL)"

# ----------------------------------------------------------------------------- 
# Crawl targets
# -----------------------------------------------------------------------------
crawl-local: ## Run tools/crawl_sitemap.py against http://localhost:3000
	$(PY) $(CRAWL_TOOL) --base-url http://localhost:3000 --outdir $(CRAWL_OUT) --label local

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
  docs/Heroku_Pipeline_Workflow.md \
  docs/codex/AgentDeveloperCodex.md

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

codex-agent-dev: ## Run AgentDeveloper Codex workflow (Phase 2 implementation)
	@echo "== AgentDeveloper Codex: Phase 2 Implementation =="
	@echo "Starting Task Execution System completion..."
	@set -e; \
	docker compose up -d db; \
	sleep 3; \
	cd backend; \
	ALEMBIC_DATABASE_URL="postgresql://devuser:devpass@localhost:5433/devdb" \
	DB_SSLMODE_REQUIRE=0 \
	python -m alembic revision --autogenerate -m "add_task_execution_system" || true; \
	ALEMBIC_DATABASE_URL="postgresql://devuser:devpass@localhost:5433/devdb" \
	DB_SSLMODE_REQUIRE=0 \
	python -m alembic upgrade head; \
	cd ..; \
	make codex-test; \
	echo "✅ AgentDeveloper Phase 2 setup complete"

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
	$(PIP) install -q -r "$(REQ)"; \
	$(PY) -m pytest -q

codex-test-pg: ## Run pytest against real Postgres (docker-compose.test.yml)
	@echo "== Starting test Postgres container =="
	@docker compose -f docker-compose.test.yml up -d --wait
	@echo "== Running pytest against Postgres =="
	@set -e; \
	$(TEST_ENV_EXPORT) \
	export DATABASE_URL="$(TEST_PG_DB_URL)"; \
	export ALEMBIC_DATABASE_URL="$(TEST_PG_DB_URL)"; \
	. "$(VENV)/bin/activate" 2>/dev/null || true; \
	$(PIP) install -q -r "$(REQ)"; \
	$(PY) -m alembic -c backend/alembic.ini upgrade head 2>/dev/null || true; \
	$(PY) -m pytest -q; \
	echo "== Stopping test containers =="; \
	docker compose -f docker-compose.test.yml down -v

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

# Codex-powered agent development
codex-generate-tests: ## Generate comprehensive test framework using Codex
	@echo "🤖 Codex Test Generator"
	@echo "Generating comprehensive test framework for agent system..."
	$(PY) scripts/codex_test_generator.py

codex-generate-agent: ## Generate new agent using Codex templates  
	@echo "🤖 Codex Agent Generator"
	@read -p "Agent name: " agent_name; \
	read -p "Agent description: " agent_desc; \
	echo "Generating agent: $$agent_name"
	@echo "Use GitHub Copilot to generate agent based on CapeAI Guide template"

codex-agent-marketplace: ## Generate marketplace infrastructure using Codex
	@echo "🏪 Codex Marketplace Generator"
	@echo "Use GitHub Copilot with MarketplaceCodex.md to generate marketplace"

test-agents: ## Run agent-specific tests
	@echo "🧪 Running Agent Tests"
	$(TEST_ENV_EXPORT) \
	pytest tests_enabled/agents/ -v || true

# ----------------------------------------------------------------------------- 
# Smoke & CSRF probes
# -----------------------------------------------------------------------------
smoke-local: ## Health + CSRF probe against localhost backend
	@echo "== Smoke test against http://localhost:$(PORT) =="
	@curl -fsS "http://localhost:$(PORT)/api/health" >/dev/null && echo "✓ /api/health OK" || { echo "✗ /api/health failed"; exit 1; }
	@$(MAKE) csrf-probe-local || true

csrf-probe-local: ## Direct CSRF probe (local)
	@echo "== CSRF probe (local) =="
	@set -e; \
	status=$$(curl -s -o /tmp/csrf_body.txt -D /tmp/csrf_headers.txt "http://localhost:$(PORT)/api/auth/csrf" -w "%{http_code}" || true); \
	echo "Status: $$status"; \
	if [ -f /tmp/csrf_headers.txt ] && grep -qi 'set-cookie' /tmp/csrf_headers.txt; then echo "✓ Set-Cookie present"; else echo "✗ No Set-Cookie"; fi; \
	[ -f /tmp/csrf_body.txt ] && cat /tmp/csrf_body.txt || true

smoke-prod: ## Quick production health + CSRF probe
	@echo "== Smoke test against $(PROD_BASE_URL) =="
	@curl -fsS "$(PROD_BASE_URL)/api/health" | jq . >/dev/null && echo "✓ /api/health OK" || { echo "✗ /api/health failed"; exit 1; }
	@set -e; \
	status=$$(curl -s -o /tmp/csrf_body.txt -D /tmp/csrf_headers.txt "$(PROD_BASE_URL)/api/auth/csrf" -w "%{http_code}" || true); \
	if grep -qi 'set-cookie' /tmp/csrf_headers.txt 2>/dev/null; then echo "✓ CSRF cookie present"; else echo "⚠️  No CSRF cookie"; fi

codex-smoke: smoke-prod ## Production smoke & CSRF

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
#   make dockerhub-release APP=capecontrol
#   make dockerhub-release APP=capecraft VERSION=v0.3.0
#   make dockerhub-release APP=capecontrol PLATFORMS=linux/amd64
#
# Notes:
# - Tags produced: :latest, :$(VERSION), :docker-<engine>, :git-<sha>
# - Requires Docker Buildx
# -----------------------------------------------------------------------------

# Config (override on CLI, e.g. make dockerhub-release APP=capecontrol)
DH_NAMESPACE ?= stinkie
APP          ?= capecontrol
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

# Derive versions/metadata (Docker Hub tagging)
DH_GIT_SHA     := $(shell git rev-parse --short HEAD 2>/dev/null || echo "nogit")
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
SAFE_SHA     := $(shell $(call SANITIZE,$(DH_GIT_SHA)))

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
# Task Capsule Generator (advanced)
# -----------------------------------------------------------------------------

.PHONY: new-task-capsule
new-task-capsule: ## Create a new Task Capsule file: make new-task-capsule ID=AUTH-004
	@if [ -z "$(ID)" ]; then \
		echo "❌ Missing ID. Usage: make new-task-capsule ID=AUTH-004"; exit 1; \
	fi
	@mkdir -p $(TASK_CAPSULE_DIR)
	@OUTPUT_FILE="$(TASK_CAPSULE_DIR)/TC-$(ID).md"; \
	if [ -f "$$OUTPUT_FILE" ]; then \
		echo "❌ Task Capsule already exists: $$OUTPUT_FILE"; exit 1; \
	fi; \
	if [ ! -f "$(TASK_CAPSULE_TEMPLATE)" ]; then \
		echo "❌ Template not found: $(TASK_CAPSULE_TEMPLATE)"; exit 1; \
	fi; \
	echo "📝 Creating Task Capsule from template..."; \
	TODAY=$$(date +%Y-%m-%d); \
	# Render template with ID + today
	sed -e "s/TC-____/TC-$(ID)/g" -e "s/<today>/$$TODAY/g" "$(TASK_CAPSULE_TEMPLATE)" > "$$OUTPUT_FILE"; \
	# Try to pull matching row from autorisen_project_plan.csv
	if [ -f "$(PROJECT_PLAN_CSV)" ]; then \
		ROW=$$(grep -m1 "^$(ID)," "$(PROJECT_PLAN_CSV)" || true); \
		if [ -n "$$ROW" ]; then \
			echo ""; \
			echo "🔗 Linking to $(PROJECT_PLAN_CSV) row for ID=$(ID)"; \
			TASK=$$(echo "$$ROW" | cut -d',' -f2); \
			OWNER=$$(echo "$$ROW" | cut -d',' -f3); \
			STATUS=$$(echo "$$ROW" | cut -d',' -f4); \
			PRIORITY=$$(echo "$$ROW" | cut -d',' -f5); \
			COMP_DATE=$$(echo "$$ROW" | cut -d',' -f6); \
			NOTES=$$(echo "$$ROW" | cut -d',' -f7); \
			ARTIFACTS=$$(echo "$$ROW" | cut -d',' -f8); \
			VERIFY=$$(echo "$$ROW" | cut -d',' -f9); \
			{ \
				echo ""; \
				echo "---"; \
				echo ""; \
				echo "## Linked Project Plan Row"; \
				echo ""; \
				echo "- **id**: $(ID)"; \
				echo "- **task**: $${TASK}"; \
				echo "- **owner**: $${OWNER}"; \
				echo "- **status**: $${STATUS}"; \
				echo "- **priority**: $${PRIORITY}"; \
				echo "- **completion_date**: $${COMP_DATE}"; \
				echo "- **notes**: $${NOTES}"; \
				echo "- **artifacts**: $${ARTIFACTS}"; \
				echo "- **verification_commands**: $${VERIFY}"; \
			} >> "$$OUTPUT_FILE"; \
		else \
			echo "ℹ No matching row for ID=$(ID) in $(PROJECT_PLAN_CSV)"; \
		fi; \
	else \
		echo "ℹ Project plan CSV not found: $(PROJECT_PLAN_CSV)"; \
	fi; \
	echo ""; \
	echo "✅ Task Capsule created:"; \
	echo "   $$OUTPUT_FILE"; \
	# Open in VS Code if available
	if command -v code >/dev/null 2>&1; then \
		echo "🚀 Opening in VS Code..."; \
		code "$$OUTPUT_FILE"; \
	fi; \
	echo ""; \
	echo "💡 To commit later:"; \
	echo "   git add $$OUTPUT_FILE && git commit -m 'docs: add task capsule TC-$(ID)'"


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
# NOTE: Staging (autorisen) eliminated. Deploy directly to capecraft.
# Use local Docker + Postgres (docker-compose.test.yml) for integration tests.

.PHONY: heroku-login heroku-config-prod \
heroku-smoke-prod heroku-logs-prod \
heroku-open-prod heroku-rollback


heroku-login:
	@heroku login
	@heroku container:login


heroku-config-prod: require-prod
	@heroku config:set -a $(HEROKU_APP) ENV=production RUN_DB_MIGRATIONS_ON_STARTUP=0 DISABLE_RECAPTCHA=false


heroku-smoke-prod:
	@curl -fsS $(PROD_URL)/api/health >/dev/null && echo "✓ prod health OK" || (echo "✗ prod health FAIL" && exit 1)
	@heroku logs --tail -a $(HEROKU_APP)


heroku-logs-prod:
	@heroku logs --tail -a $(HEROKU_APP)


heroku-open-prod:
	@heroku open -a $(HEROKU_APP)


# Usage: make heroku-rollback REL=v123
heroku-rollback: require-prod
	@if [ -z "$$REL" ]; then echo "Set REL=vNNN" && exit 1; fi
	@heroku rollback -a $(HEROKU_APP) $$REL

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
	command -v jq >/dev/null 2>&1 || { echo "❌ jq is required for mcp-smoke"; exit 127; }; \
	RESP=$$(curl -fsS "http://127.0.0.1:$(MCP_SMOKE_PORT)/api/ops/mcp/smoke"); \
	echo "$$RESP" | jq .; \
	echo "$$RESP" | jq -e '.ok == true' >/dev/null

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
DASHBOARD_PROD_URL ?= https://cape-control.com
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
	curl -sSf -o /dev/null "$(DASHBOARD_PROD_URL)/api/auth/csrf"; \
	code=$$?; echo $$code >/tmp/csrf.code
	-@set +e; \
	curl -sSf -o /dev/null "$(DASHBOARD_PROD_URL)/api/health"; \
	code=$$?; echo $$code >/tmp/health.code
	@echo "==> Updating dashboard badges…"
	@mkdir -p tools
	@chmod +x tools/update_dashboard.py || true
	@$(DASHBOARD_RUNTIME_ENV) $(PY) tools/update_dashboard.py \
		--dashboard "$(DASHBOARD_SUMMARY)" \
		--prod "$(DASHBOARD_PROD_URL)" \
		--local "$(DASHBOARD_LOCAL_URL)" \
		--pytest-exit "$$(cat /tmp/pytest.code || echo 1)" \
		--csrf-exit  "$$(tail -n1 /tmp/csrf.code  || echo 1)" \
		--health-exit "$$(tail -n1 /tmp/health.code || echo 1)"
	@echo "==> Dashboard refreshed: $(DASHBOARD_SUMMARY)"

dashboard-open:
	@${PY} -c 'import webbrowser, os; p=os.path.abspath("$(DASHBOARD_SUMMARY)"); print("Opening", p); webbrowser.open("file://" + p)'

# --- Fallback docs sync (no-op if real target not present) --------------------
# .PHONY: codex-docs
# codex-docs:
# 	@echo "[codex-docs] No-op fallback (replace with your real docs sync if needed)"

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
	@if [ -f docs/checklists/capecraft_implementation_guide.md ]; then \
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

capsule-status:
	@echo "CAPSULE: OPS-STATUS — Project Status Overview"
	@# here you’d run whatever scripts/checks Codex recommended

capsule-plan-sync:
	@echo "CAPSULE: OPS-PLAN-SYNC — Update Project Plan & Related Files"
	@# run scripts to regenerate docs or summaries

