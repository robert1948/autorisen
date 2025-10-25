SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c

PY := python3
PIP := $(PY) -m pip
VENV := .venv
REQ := requirements.txt
IMAGE ?= autorisen:local
PORT ?= 8000
HEROKU_APP_NAME ?= autorisen

# Domains
DEV_BASE_URL  ?= https://dev.cape-control.com
PROD_BASE_URL ?= https://cape-control.com

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
HEROKU_APP  ?= autorisen

# Test DB (single source of truth)
TEST_DB_URL ?= sqlite:////tmp/autolocal_test.db

.PHONY: help venv install format lint test docker-build docker-run docker-push deploy-heroku github-update clean \
		plan-validate plan-open heroku-deploy-stg migrate-up migrate-revision \
		sitemap-generate-dev sitemap-generate-prod verify-sitemap-dev verify-sitemap-prod \
		verify-sitemap crawl-dev crawl-prod crawl-local crawl sitemap-svg \
		codex-check codex-open codex-docs-lint codex-docs-fix codex-ci-validate \
		codex-plan-diff codex-plan-apply codex-test-dry codex-test-heal codex-test codex-test-cov codex-run \
		smoke-staging smoke-local csrf-probe-staging csrf-probe-local heroku-logs heroku-run-migrate \
		dockerhub-update-description
		codex-test-strict codex-smoke smoke-prod

help:
	@echo "Available targets:"
	@echo "  make venv                     - create a virtualenv in $(VENV)"
	@echo "  make install                  - install project dependencies (uses $(REQ) if present)"
	@echo "  make format                   - run code formatters (black/isort)"
	@echo "  make lint                     - run linters (ruff)"
	@echo "  make test                     - run tests (pytest)"
	@echo "  make docker-build             - build docker image (IMAGE=$(IMAGE))"
	@echo "  make docker-run               - run docker image locally (exposes $(PORT))"
	@echo "  make deploy-heroku            - build/push/release to Heroku Container Registry (retries on transient failures)"
	@echo "  make heroku-deploy-stg        - quick push/release to $(HEROKU_APP)"
	@echo "  make heroku-logs              - tail dyno logs"
	@echo "  make heroku-run-migrate       - run Alembic upgrade on Heroku dyno"
	@echo "  make github-update            - fast-forward current branch from GitHub origin"
	@echo "  make clean                    - remove common build artifacts"
	@echo "  --- Sitemap / verification ---"
	@echo "  make sitemap-generate-dev     - generate client/public/$(SITEMAP_XML) from $(SITEMAP_DEV_TXT)"
	@echo "  make sitemap-generate-prod    - generate client/public/$(SITEMAP_XML) from $(SITEMAP_PROD_TXT)"
	@echo "  make verify-sitemap-dev       - curl-check all dev routes from $(SITEMAP_DEV_TXT) (BASE=$(DEV_BASE_URL))"
	@echo "  make verify-sitemap-prod      - curl-check all prod routes from $(SITEMAP_PROD_TXT) (BASE=$(PROD_BASE_URL))"
	@echo "  make crawl-dev|prod|local     - crawl site and save captures to $(CRAWL_OUT)"
	@echo "  --- Codex helpers ---"
	@echo "  make codex-check              - verify Codex context files & VS Code settings"
	@echo "  make codex-run                - docs lint, pre-commit, pytest with CI-safe env"
	@echo "  --- Smoke tests ---"
	@echo "  make smoke-staging            - health + OpenAPI CSRF discovery probe"
	@echo "  make smoke-local              - health + CSRF probe against localhost backend"
	@echo "  make csrf-probe-staging       - direct CSRF probe (accepts 200/204; checks Set-Cookie)"
	@echo "  make csrf-probe-local         - direct CSRF probe localhost"
	@echo "  make codex-smoke              - run both staging smoke + CSRF probe"
	@echo "  make smoke-prod               - health check against production domain"

venv:
	@if [ -d "$(VENV)" ]; then \
		echo "Virtualenv $(VENV) already exists"; \
	else \
		$(PY) -m venv $(VENV); \
		echo "Created virtualenv $(VENV)"; \
	fi

install: venv
	@echo "Installing dependencies..."
	@if [ -f "$(REQ)" ]; then \
		$(VENV)/bin/python -m pip install -r $(REQ); \
	else \
		$(VENV)/bin/python -m pip install -e . || true; \
		echo "No requirements.txt found; attempted editable install"; \
	fi

format:
	@echo "Running formatters..."
	@$(VENV)/bin/python -m pip install black isort >/dev/null 2>&1 || true
	@$(VENV)/bin/black . || true
	@$(VENV)/bin/isort . || true

lint:
	@echo "Running ruff linter..."
	@$(VENV)/bin/python -m pip install ruff >/dev/null 2>&1 || true
	@$(VENV)/bin/ruff check . || true

test:
	@echo "Running tests..."
	@$(VENV)/bin/python -m pip install pytest >/dev/null 2>&1 || true
	@$(VENV)/bin/pytest -q || true

# Docker targets ---------------------------------------------------------

docker-build:
	@echo "Building docker image $(IMAGE)..."
	@for i in 1 2 3; do \
		if docker build -t $(IMAGE) .; then \
			echo "Docker build succeeded on attempt $$i"; exit 0; \
		fi; \
		echo "Docker build failed (attempt $$i). Retrying in 5s..."; sleep 5; \
	done; \
	echo "Docker build failed after retries"; exit 1

docker-run:
	@echo "Running docker image $(IMAGE) on port $(PORT)..."
	docker run --rm -p $(PORT):$(PORT) --env PORT=$(PORT) $(IMAGE)

# Push to registry (generic). If you want to push to Heroku, set HEROKU_APP_NAME.
docker-push:
	@if [ -z "$(REGISTRY)" ]; then \
		echo "Please set REGISTRY or use deploy-heroku for Heroku (set HEROKU_APP_NAME)."; exit 1; \
	fi
	@echo "Tagging and pushing to $(REGISTRY)/$(IMAGE)..."
	docker tag $(IMAGE) $(REGISTRY)/$(IMAGE)
	docker push $(REGISTRY)/$(IMAGE)

# Heroku container deploy (with basic retries on login/push/release) -----

deploy-heroku: docker-build
	@if [ -z "$(HEROKU_APP_NAME)" ]; then \
		echo "Set HEROKU_APP_NAME environment variable to your Heroku app name"; exit 1; \
	fi
	@echo "Tagging image for Heroku registry..."
	docker tag $(IMAGE) registry.heroku.com/$(HEROKU_APP_NAME)/web
	@echo "Logging in to Heroku Container Registry..."
	@for i in 1 2 3; do \
		if heroku container:login >/dev/null 2>&1; then echo "Login OK"; break; fi; \
		echo "Login failed (attempt $$i). Retrying in 5s..."; sleep 5; \
	done
	@echo "Pushing image to Heroku registry..."
	@for i in 1 2 3; do \
		if docker push registry.heroku.com/$(HEROKU_APP_NAME)/web; then echo "Push OK"; break; fi; \
		echo "Push failed (attempt $$i). Retrying in 5s..."; sleep 5; \
		[ $$i -eq 3 ] && { echo "Push failed after retries"; exit 1; } || true; \
	done
	@echo "Releasing on Heroku..."
	@for i in 1 2 3; do \
		if heroku container:release web --app $(HEROKU_APP_NAME); then echo "Release OK"; break; fi; \
		echo "Release failed (attempt $$i). Retrying in 5s..."; sleep 5; \
		[ $$i -eq 3 ] && { echo "Release failed after retries"; exit 1; } || true; \
	done

heroku-deploy-stg:
	heroku container:login
	heroku container:push web -a $(HEROKU_APP)
	heroku container:release web -a $(HEROKU_APP)
	heroku open -a $(HEROKU_APP)

heroku-logs:
	heroku logs -t -a $(HEROKU_APP)

heroku-run-migrate:
	# Run Alembic upgrade inside a one-off dyno
	heroku run -a $(HEROKU_APP) "ENV=prod PYTHONWARNINGS=default alembic -c backend/alembic.ini upgrade head"

# Git helpers ------------------------------------------------------------

github-update:
	@echo "Updating branch $$(git rev-parse --abbrev-ref HEAD) from origin..."
	@git fetch origin
	@git pull --ff-only origin $$(git rev-parse --abbrev-ref HEAD)

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache/ .venv

plan-validate:
	python3 tools/validate_plan_csv.py

plan-open:
	code docs/CODEX_PROJECT_PLAN.md data/plan.csv

# Alembic ---------------------------------------------------------------

migrate-up: venv
	@echo "Running Alembic upgrade head..."
	@$(VENV)/bin/python -m pip install -e backend >/dev/null 2>&1 || true
	@$(VENV)/bin/python -m alembic -c backend/alembic.ini upgrade head

migrate-revision: venv
	@[ -n "$$message" ] || (echo "Usage: make migrate-revision message=\"<description>\""; exit 1)
	@echo "Creating Alembic revision: $$message"
	@$(VENV)/bin/python -m pip install -e backend >/dev/null 2>&1 || true
	@$(VENV)/bin/python -m alembic -c backend/alembic.ini revision -m "$$message"

# -----------------------------
# Sitemap generation & checks
# -----------------------------

define GEN_SITEMAP_XML
mkdir -p "$(PUBLIC_DIR)"
$(PY) - <<'PYCODE'
from datetime import date
from pathlib import Path
import os
import sys

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

sitemap-generate-dev:
	@BASE_URL="$(DEV_BASE_URL)"; \
	$(call GEN_SITEMAP_XML,$(SITEMAP_DEV_TXT))

sitemap-generate-prod:
	@BASE_URL="$(PROD_BASE_URL)"; \
	$(call GEN_SITEMAP_XML,$(SITEMAP_PROD_TXT))

verify-sitemap:
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

verify-sitemap-dev:
	@$(MAKE) verify-sitemap FILE="$(SITEMAP_DEV_TXT)" BASE="$(DEV_BASE_URL)"

verify-sitemap-prod:
	@$(MAKE) verify-sitemap FILE="$(SITEMAP_PROD_TXT)" BASE="$(PROD_BASE_URL)"

# --- Crawl targets ----------------------------------------------------

crawl-local: ## run tools/crawl_sitemap.py against http://localhost:3000
	$(PY) $(CRAWL_TOOL) --base-url http://localhost:3000 --outdir $(CRAWL_OUT) --label local

crawl-dev: ## run crawler against dev.cape-control.com
	$(PY) $(CRAWL_TOOL) --base-url $(DEV_BASE_URL) --outdir $(CRAWL_OUT) --label dev

crawl-prod: ## run crawler against cape-control.com
	$(PY) $(CRAWL_TOOL) --base-url https://www.cape-control.com --outdir $(CRAWL_OUT) --label prod

crawl: crawl-local ## default crawl

# -----------------------------
# Agents tooling (unchanged)
# -----------------------------

agents-new:
	@[ -n "$$name" ] || (echo "Usage: make agents-new name=<slug>"; exit 1)
	@mkdir -p agents/$(name)/tests && \
	printf "name: %s\nrole: <fill>\nmodel: { provider: openai, name: gpt-4.1-mini, temperature: 0.2 }\npolicies: { allow_tools: [] }\ncontext: { system_prompt: |\n  You are %s. }\n" "$(name)" "$(name)" > agents/$(name)/agent.yaml
	@echo "Created agents/$(name)"

agents-validate:
	@python3 scripts/agents_validate.py agents/registry.yaml

agents-test:
	@python3 -m pytest -q tests/test_agents_tooling.py

agents-run:
	@[ -n "$$name" ] || (echo "Usage: make agents-run name=<slug> task=\"...\""; exit 1)
	@python3 scripts/agents_run.py --agent $$name --task "$$task"

sitemap-svg:
	npx mmdc -i docs/sitemap_v2_final.mmd -o docs/sitemap_v2_final.svg -t neutral -b transparent -s 1.5

# --- Codex helpers ------------------------------------------------------------

CODEX_DOCS ?= \
  docs/DEVELOPMENT_CONTEXT.md \
  docs/MVP_SCOPE.md \
  docs/Checklist_MVP.md \
  docs/agents.md \
  docs/Heroku_Pipeline_Workflow.md

codex-check:
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

codex-open:
	@which code >/dev/null 2>&1 || { echo "⚠️  'code' CLI not found (install VS Code Shell Command)."; exit 0; }
	@[ -f .vscode/codex.prompt.md ] && code -g .vscode/codex.prompt.md || true
	@[ -f .vscode/settings.json ] && code -g .vscode/settings.json || true

codex-docs-lint:
	@command -v markdownlint >/dev/null 2>&1 || { echo "Installing markdownlint-cli (global)"; npm i -g markdownlint-cli >/dev/null 2>&1; }
	markdownlint "**/*.md" --ignore node_modules --ignore .venv

codex-docs-fix:
	@command -v markdownlint >/dev/null 2>&1 || { echo "Installing markdownlint-cli (global)"; npm i -g markdownlint-cli >/dev/null 2>&1; }
	markdownlint "**/*.md" --ignore node_modules --ignore .venv --fix || true
	@echo "Re-run lint to verify:"
	markdownlint "**/*.md" --ignore node_modules --ignore .venv

codex-ci-validate:
	@command -v pre-commit >/dev/null 2>&1 || { echo "Installing pre-commit"; python3 -m pip install --quiet pre-commit; }
	pre-commit run --all-files || true

codex-plan-diff:
	python3 scripts/plan_sync.py --check-only

codex-plan-apply:
	python3 scripts/plan_sync.py --apply

codex-test-heal:
	python3 scripts/regenerate_fixtures.py || true
	pytest -q || true

# -----------------------------
# Test env macros (DRY)
# -----------------------------
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

codex-test:
	@echo "== Running pytest with CI-safe defaults =="
	@set -e; \
	$(TEST_ENV_EXPORT) \
	. "$(VENV)/bin/activate" 2>/dev/null || true; \
	$(PY) -m pip install -q -r "$(REQ)"; \
	pytest -q

codex-test-cov:
	@echo "== Running pytest with coverage =="
	@set -e; \
	$(TEST_ENV_EXPORT) \
	. "$(VENV)/bin/activate" 2>/dev/null || true; \
	$(PY) -m pip install -q -r "$(REQ)" pytest-cov; \
	pytest -q --cov=backend/src --cov-report=term --cov-report=xml

codex-test-dry:
	@set -e; \
	$(TEST_ENV_EXPORT) \
	pytest -q || true

codex-run:
	@$(MAKE) codex-check
	@$(MAKE) codex-docs-lint || true
	@$(MAKE) codex-ci-validate
	@$(MAKE) codex-test

# --- Smoke & CSRF probes ------------------------------------------------

smoke-staging:
	@echo "== Smoke test against $(STAGING_URL) =="
	@curl -fsS "$(STAGING_URL)/api/health" | jq . >/dev/null && echo "✓ /api/health OK" || { echo "✗ /api/health failed"; exit 1; }
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

smoke-local:
	@echo "== Smoke test against http://localhost:$(PORT) =="
	@curl -fsS "http://localhost:$(PORT)/api/health" >/dev/null && echo "✓ /api/health OK" || { echo "✗ /api/health failed"; exit 1; }
	@$(MAKE) csrf-probe-local || true

csrf-probe-staging:
	@echo "== CSRF probe (staging) =="
	@set -e; \
	status=$$(curl -s -o /tmp/csrf_body.txt -D /tmp/csrf_headers.txt "$(STAGING_URL)/api/auth/csrf" -w "%{http_code}"); \
	echo "Status: $$status"; \
	if grep -qi 'set-cookie' /tmp/csrf_headers.txt; then echo "✓ Set-Cookie present"; else echo "✗ No Set-Cookie"; fi; \
	cat /tmp/csrf_body.txt || true

csrf-probe-local:
	@echo "== CSRF probe (local) =="
	@set -e; \
	status=$$(curl -s -o /tmp/csrf_body.txt -D /tmp/csrf_headers.txt "http://localhost:$(PORT)/api/auth/csrf" -w "%{http_code}" || true); \
	echo "Status: $$status"; \
	if [ -f /tmp/csrf_headers.txt ] && grep -qi 'set-cookie' /tmp/csrf_headers.txt; then echo "✓ Set-Cookie present"; else echo "✗ No Set-Cookie"; fi; \
	[ -f /tmp/csrf_body.txt ] && cat /tmp/csrf_body.txt || true

# Convenience combos
codex-smoke: smoke-staging csrf-probe-staging

# Optional: quick production health (no CSRF probe)
smoke-prod:
	@echo "== Smoke test against $(PROD_BASE_URL) =="
	@curl -fsS "$(PROD_BASE_URL)/api/health" | jq . >/dev/null && echo "✓ /api/health OK" || { echo "✗ /api/health failed"; exit 1; }

# --- Strict mode tests --------------------------------------------------

codex-test-strict:
	@set -e; \
	$(TEST_ENV_EXPORT) \
	export PYTHONWARNINGS="error"; \
	. "$(VENV)/bin/activate" 2>/dev/null || true; \
	$(PY) -m pip install -q -r "$(REQ)"; \
	pytest -q

# =============================================================================
# Makefile — Docker Hub (multi-arch) release with safe tags
# =============================================================================
# Usage:
#   make help
#   make dockerhub-login
#   make dockerhub-release APP=autorisen
#   make dockerhub-release APP=capecraft VERSION=v0.3.0
#   make dockerhub-release APP=autorisen PLATFORMS=linux/amd64
#
# Notes:
# - Tags produced: :latest, :$(VERSION), :docker-<engine>, :git-<sha>
# - All tags are sanitized to Docker's allowed charset [A-Za-z0-9_.-]
# - Requires Docker Buildx (created automatically if missing)
# =============================================================================

SHELL := /bin/bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c

# -----------------------------------------------------------------------------
# Config (override on CLI, e.g. make dockerhub-release APP=autorisen)
# -----------------------------------------------------------------------------
DH_NAMESPACE ?= stinkie
APP          ?= autorisen
CONTEXT      ?= .
DOCKERFILE   ?= Dockerfile
PLATFORMS    ?= linux/amd64,linux/arm64

# Optional build arguments and cache
BUILD_ARGS        ?=
BUILD_CACHE_FROM  ?=
BUILD_CACHE_TO    ?=

# -----------------------------------------------------------------------------
# Helpers: trim & sanitize variables
# -----------------------------------------------------------------------------
# SANITIZE keeps only characters valid for Docker refs: [A-Za-z0-9_.-]
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

# Sanitized values for tags
SAFE_VERSION := $(shell $(call SANITIZE,$(VERSION)))
SAFE_ENGINE  := $(shell $(call SANITIZE,$(DOCKER_ENGINE_VERSION)))
SAFE_SHA     := $(shell $(call SANITIZE,$(GIT_SHA)))

# Final image path
IMAGE := $(NS)/$(APPNAME)

# Default target
.DEFAULT_GOAL := help

# -----------------------------------------------------------------------------
# Info & Help
# -----------------------------------------------------------------------------
.PHONY: help show-vars
help:
	@echo ""
	@echo "Targets:"
	@echo "  dockerhub-login           Login to Docker Hub (interactive)"
	@echo "  dockerhub-logout          Logout from Docker Hub"
	@echo "  dockerhub-setup-builder   Ensure Buildx 'multiarch-builder' is ready"
	@echo "  dockerhub-build           Local single-arch build (no push)"
	@echo "  dockerhub-push            Push local :$(SAFE_VERSION) and :latest"
	@echo "  dockerhub-release         Multi-arch buildx + push (recommended)"
	@echo "  dockerhub-update-description  PATCH repository description via Docker Hub API"
	@echo "  dockerhub-clean           Prune dangling images"
	@echo "  release-autorisen         Shortcut for APP=autorisen"
	@echo "  release-capecraft         Shortcut for APP=capecraft"
	@echo ""
	@echo "Variables (override on CLI):"
	@echo "  DH_NAMESPACE=$(DH_NAMESPACE)  APP=$(APP)"
	@echo "  CONTEXT=$(CONTEXT)  DOCKERFILE=$(DOCKERFILE)"
	@echo "  PLATFORMS=$(PLATFORMS)"
	@echo "  VERSION=$(VERSION)  (sanitized -> $(SAFE_VERSION))"
	@echo "  DOCKER_ENGINE_VERSION=$(DOCKER_ENGINE_VERSION) (sanitized -> $(SAFE_ENGINE))"
	@echo "  GIT_SHA=$(GIT_SHA) (sanitized -> $(SAFE_SHA))"
	@echo "  BUILD_ARGS=$(BUILD_ARGS)"
	@echo "  BUILD_CACHE_FROM=$(BUILD_CACHE_FROM)"
	@echo "  BUILD_CACHE_TO=$(BUILD_CACHE_TO)"
	@echo ""
	@echo "Image:"
	@echo "  $(IMAGE)"
	@echo ""

show-vars:
	@$(MAKE) --no-print-directory help

# -----------------------------------------------------------------------------
# Auth
# -----------------------------------------------------------------------------
.PHONY: dockerhub-login dockerhub-logout
dockerhub-login:
	@echo "Logging in to Docker Hub…"
	docker login

dockerhub-logout:
	@echo "Logging out of Docker Hub…"
	-docker logout

# -----------------------------------------------------------------------------
# Buildx setup
# -----------------------------------------------------------------------------
.PHONY: dockerhub-setup-builder
dockerhub-setup-builder:
	@echo "Ensuring docker buildx builder is ready…"
	@if ! docker buildx inspect multiarch-builder >/dev/null 2>&1; then \
		docker buildx create --name multiarch-builder --use; \
	else \
		docker buildx use multiarch-builder; \
	fi
	@docker buildx inspect --bootstrap >/dev/null
	@echo "Buildx builder 'multiarch-builder' is ready."

# -----------------------------------------------------------------------------
# Local single-arch build/push (useful for quick tests)
# -----------------------------------------------------------------------------
.PHONY: dockerhub-build dockerhub-push
dockerhub-build:
	@echo "Building local image: $(IMAGE):$(SAFE_VERSION)"
	docker build \
		-f "$(DOCKERFILE)" \
		-t "$(IMAGE):$(SAFE_VERSION)" \
		$(BUILD_ARGS) \
		"$(CONTEXT)"
	@echo "Tagging latest…"
	docker tag "$(IMAGE):$(SAFE_VERSION)" "$(IMAGE):latest"

dockerhub-push:
	@echo "Pushing $(IMAGE):$(SAFE_VERSION) and :latest…"
	docker push "$(IMAGE):$(SAFE_VERSION)"
	docker push "$(IMAGE):latest"

# -----------------------------------------------------------------------------
# Multi-arch Release (recommended)
# -----------------------------------------------------------------------------
.PHONY: dockerhub-release
dockerhub-release: dockerhub-setup-builder
	@echo "Releasing $(IMAGE) for platforms [$(PLATFORMS)]"
	@echo "Tags to push:"
	@echo "  - $(IMAGE):$(SAFE_VERSION)"
	@echo "  - $(IMAGE):latest"
	@echo "  - $(IMAGE):docker-$(SAFE_ENGINE)"
	@echo "  - $(IMAGE):git-$(SAFE_SHA)"
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
		-t "$(IMAGE):$(SAFE_VERSION)" \
		-t "$(IMAGE):latest" \
		-t "$(IMAGE):docker-$(SAFE_ENGINE)" \
		-t "$(IMAGE):git-$(SAFE_SHA)" \
		$$CACHE_FROM $$CACHE_TO \
		"$(CONTEXT)"

	# -----------------------------------------------------------------------------
	# Update Docker Hub description (requires DOCKERHUB_TOKEN env var)
	# -----------------------------------------------------------------------------
	.PHONY: dockerhub-update-description
	dockerhub-update-description:
		@set -e; \
		[ -n "$(DESCRIPTION)" ] || { echo "Usage: make dockerhub-update-description DESCRIPTION=\"<text>\" [APP=...]"; exit 1; }; \
		if [ -z "$$DOCKERHUB_TOKEN" ]; then echo "Set DOCKERHUB_TOKEN environment variable to a Docker Hub access token"; exit 1; fi; \
		BODY=$$(DESC="$(DESCRIPTION)" python3 - <<'PYCODE'
	import json, os
	print(json.dumps({"description": os.environ["DESC"]}))
	PYCODE
	);
		URL="https://hub.docker.com/v2/repositories/$(NS)/$(APPNAME)/"; \
		echo "Updating $$URL description..."; \
		curl -sSf -X PATCH \
			-H "Content-Type: application/json" \
			-H "Authorization: JWT $$DOCKERHUB_TOKEN" \
			-d "$$BODY" \
			"$$URL" | tee /tmp/dockerhub_description_response.json >/dev/null; \
		echo; \
		echo "Docker Hub API response saved to /tmp/dockerhub_description_response.json"

# -----------------------------------------------------------------------------
# Shortcuts for common repos
# -----------------------------------------------------------------------------
.PHONY: release-autorisen release-capecraft
release-autorisen: ; $(MAKE) dockerhub-release APP=autorisen
release-capecraft: ; $(MAKE) dockerhub-release APP=capecraft

# -----------------------------------------------------------------------------
# Clean-up
# -----------------------------------------------------------------------------
.PHONY: dockerhub-clean
dockerhub-clean:
	@echo "Pruning dangling images…"
	-docker image prune -f

## --- Playbooks ---
.PHONY: playbooks-overview playbook-new playbooks-check

PLAYBOOKS_DIR ?= docs/playbooks
PLAYBOOK_TEMPLATE ?= $(PLAYBOOKS_DIR)/templates/playbook.template.md
PLAYBOOK_SCRIPT ?= scripts/playbooks_overview.py

playbooks-overview: ## Rebuild docs/PLAYBOOKS_OVERVIEW.md
	@$(PY) $(PLAYBOOK_SCRIPT)
	@echo "Updated docs/PLAYBOOKS_OVERVIEW.md"

playbook-new: ## Create a new playbook: make playbook-new NUMBER=02 TITLE="X" OWNER="Robert" AGENTS="Codex, CapeAI" PRIORITY=P1
	@test -n "$(NUMBER)" || (echo "NUMBER= required"; exit 1)
	@test -n "$(TITLE)"  || (echo "TITLE= required"; exit 1)
	@test -n "$(OWNER)"  || (echo "OWNER= required"; exit 1)
	@mkdir -p $(PLAYBOOKS_DIR)
	@dst="$(PLAYBOOKS_DIR)/playbook-$(NUMBER)-$(shell echo $(TITLE) | tr '[:upper:] ' '[:lower:]-' | tr -cd 'a-z0-9-').md"; \
	sed -e "s/\${NUMBER}/$(NUMBER)/g" \
	    -e "s/\${TITLE}/$(TITLE)/g" \
	    -e "s/\${OWNER}/$(OWNER)/g" \
	    -e "s/\${AGENTS}/$(AGENTS)/g" \
	    -e "s/\${PRIORITY}/$(PRIORITY)/g" $(PLAYBOOK_TEMPLATE) > $$dst; \
	echo "Created $$dst"; \
	$(MAKE) playbooks-overview

playbooks-check: ## Validate required headers exist in all playbooks
	@missing=0; \
	for f in $(PLAYBOOKS_DIR)/playbook-*.md; do \
	  grep -q "^## 1) Outcome" $$f || { echo "Missing Outcome in $$f"; missing=1; }; \
	  grep -q "^## 5) Checklist (Executable)" $$f || { echo "Missing Checklist in $$f"; missing=1; }; \
	done; \
	exit $$missing
