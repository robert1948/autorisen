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

.PHONY: help venv install format lint test build docker-build docker-run docker-push deploy-heroku github-update clean \
		plan-validate plan-open heroku-deploy-stg migrate-up migrate-revision \
		sitemap-generate-dev sitemap-generate-prod verify-sitemap-dev verify-sitemap-prod \
		verify-sitemap crawl-dev crawl-prod crawl-local crawl

help:
	@echo "Available targets:"
	@echo "  make venv                     - create a virtualenv in $(VENV)"
	@echo "  make install                  - install project dependencies (uses $(REQ) if present)"
	@echo "  make format                   - run code formatters (black/isort)"
	@echo "  make lint                     - run linters (ruff)"
	@echo "  make test                     - run tests (pytest)"
	@echo "  make docker-build             - build docker image (IMAGE=$(IMAGE))"
	@echo "  make docker-run               - run docker image locally (exposes $(PORT))"
	@echo "  make deploy-heroku            - build/push/release to Heroku Container Registry"
	@echo "  make github-update            - fast-forward current branch from GitHub origin"
	@echo "  make clean                    - remove common build artifacts"
	@echo "  --- Sitemap / verification ---"
	@echo "  make sitemap-generate-dev     - generate client/public/$(SITEMAP_XML) from $(SITEMAP_DEV_TXT)"
	@echo "  make sitemap-generate-prod    - generate client/public/$(SITEMAP_XML) from $(SITEMAP_PROD_TXT)"
	@echo "  make verify-sitemap-dev       - curl-check all dev routes from $(SITEMAP_DEV_TXT) (BASE=$(DEV_BASE_URL))"
	@echo "  make verify-sitemap-prod      - curl-check all prod routes from $(SITEMAP_PROD_TXT) (BASE=$(PROD_BASE_URL))"
	@echo "  make verify-sitemap           - curl-check routes using FILE=<txt> BASE=<url> (manual)"
	@echo "  make crawl-dev                - run tools/crawl_sitemap.py against $(DEV_BASE_URL)"
	@echo "  make crawl-prod               - run tools/crawl_sitemap.py against $(PROD_BASE_URL)"
	@echo "  make crawl-local              - run tools/crawl_sitemap.py against http://localhost:3000"

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

# Docker targets
docker-build:
	@echo "Building docker image $(IMAGE)..."
	docker build -t $(IMAGE) .

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

# Heroku container deploy (requires heroku CLI and HEROKU_APP_NAME env var)
deploy-heroku: docker-build
	@if [ -z "$(HEROKU_APP_NAME)" ]; then \
		echo "Set HEROKU_APP_NAME environment variable to your Heroku app name"; exit 1; \
	fi
	@echo "Tagging image for Heroku registry..."
	docker tag $(IMAGE) registry.heroku.com/$(HEROKU_APP_NAME)/web
	@echo "Logging in to Heroku Container Registry (make sure HEROKU_API_KEY is exported or you are logged in)..."
	@heroku container:login >/dev/null 2>&1 || true
	@echo "Pushing image to Heroku registry..."
	docker push registry.heroku.com/$(HEROKU_APP_NAME)/web
	@echo "Releasing on Heroku..."
	heroku container:release web --app $(HEROKU_APP_NAME)

github-update:
	@echo "Updating branch $$(git rev-parse --abbrev-ref HEAD) from origin..."
	@origin_url="$$(git remote get-url origin)"; \
	if [ "$$origin_url" != "https://github.com/robert1948/autorisen.git" ]; then \
		echo "Origin remote is '$$origin_url' (expected https://github.com/robert1948/autorisen.git)"; \
		exit 1; \
	fi
	@git fetch origin
	@git pull --ff-only origin $$(git rev-parse --abbrev-ref HEAD)

heroku-deploy-stg:
	heroku container:login
	heroku container:push web -a autorisen
	heroku container:release web -a autorisen
	heroku open -a autorisen

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache/ .venv

plan-validate:
	python3 tools/validate_plan_csv.py

plan-open:
	code docs/CODEX_PROJECT_PLAN.md data/plan.csv

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

# Helper to turn a plain list (docs/sitemap.*.txt) into XML under client/public/sitemap.xml
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

# Generate sitemap.xml for DEV from docs/sitemap.dev.txt
sitemap-generate-dev:
	@BASE_URL="$(DEV_BASE_URL)"; \
	$(call GEN_SITEMAP_XML,$(SITEMAP_DEV_TXT))

# Generate sitemap.xml for PROD from docs/sitemap.prod.txt
sitemap-generate-prod:
	@BASE_URL="$(PROD_BASE_URL)"; \
	$(call GEN_SITEMAP_XML,$(SITEMAP_PROD_TXT))

# Verify all routes in a given list FILE exist (2xx/3xx) at BASE
# Usage: make verify-sitemap FILE=docs/sitemap.dev.txt BASE=$(DEV_BASE_URL)
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
CRAWL_OUT ?= docs/crawl
CRAWL_TOOL ?= tools/crawl_sitemap.py

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
.PHONY: agents-new agents-validate agents-test agents-run

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

# Add/adjust the list to match the Codex context files you expect:
CODEX_DOCS ?= \
  docs/DEVELOPMENT_CONTEXT.md \
  docs/MVP_SCOPE.md \
  docs/Checklist_MVP.md \
  docs/agents.md \
  docs/Heroku_Pipeline_Workflow.md

.PHONY: codex-check codex-open

## codex-check: Show presence, size, and last-modified for Codex context + settings
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

## codex-open: Open the Codex prompt and settings in VS Code (best effort)
codex-open:
	@which code >/dev/null 2>&1 || { echo "⚠️  'code' CLI not found (install VS Code Shell Command)."; exit 0; }
	@[ -f .vscode/codex.prompt.md ] && code -g .vscode/codex.prompt.md || true
	@[ -f .vscode/settings.json ] && code -g .vscode/settings.json || true

# ---- Codex agent targets -------------------------------------------------

.PHONY: codex-docs-lint codex-docs-fix codex-ci-validate \
        codex-plan-diff codex-plan-apply \
        codex-test-dry codex-test-heal

# Lint markdown and apply fixes
codex-docs-lint:
	@command -v markdownlint >/dev/null 2>&1 || { echo "Installing markdownlint-cli (global)"; npm i -g markdownlint-cli >/dev/null 2>&1; }
	markdownlint "**/*.md" --ignore node_modules --ignore .venv

codex-docs-fix:
	@command -v markdownlint >/dev/null 2>&1 || { echo "Installing markdownlint-cli (global)"; npm i -g markdownlint-cli >/dev/null 2>&1; }
	markdownlint "**/*.md" --ignore node_modules --ignore .venv --fix || true
	@echo "Re-run lint to verify:"
	markdownlint "**/*.md" --ignore node_modules --ignore .venv

# Run pre-commit against all files (soft-fail allowed in CI workflow)
codex-ci-validate:
	@command -v pre-commit >/dev/null 2>&1 || { echo "Installing pre-commit"; python3 -m pip install --quiet pre-commit; }
	pre-commit run --all-files || true

# Detect and reconcile drift between CSV plan and MD plan
codex-plan-diff:
	python3 scripts/plan_sync.py --check-only

codex-plan-apply:
	python3 scripts/plan_sync.py --apply

# Pytest "dry" run and optional healing (fixture regen)
codex-test-dry:
	pytest -q || true

codex-test-heal:
	python3 scripts/regenerate_fixtures.py || true
	pytest -q || true

.PHONY: codex-test
codex-test:  ## Run backend pytest the same way CI will (quiet, deterministic env)
	@echo "== Running pytest with CI-safe defaults =="
	ENV=test \
	DATABASE_URL=sqlite:////tmp/autolocal_test.db \
	ALEMBIC_DATABASE_URL=sqlite:////tmp/autolocal_test.db \
	DISABLE_RECAPTCHA=true \
	RUN_DB_MIGRATIONS_ON_STARTUP=0 \
	RATE_LIMIT_BACKEND=memory \
	PYTHONWARNINGS=default \
	. $(VENV)/bin/activate 2>/dev/null || true; \
	$(PY) -m pip install -q -r $(REQ); \
	pytest -q

.PHONY: codex-test-cov
codex-test-cov:  ## Run pytest with coverage (xml+term)
	@echo "== Running pytest with coverage =="
	ENV=test \
	DATABASE_URL=sqlite:////tmp/autolocal_test.db \
	ALEMBIC_DATABASE_URL=sqlite:////tmp/autolocal_test.db \
	DISABLE_RECAPTCHA=true \
	RUN_DB_MIGRATIONS_ON_STARTUP=0 \
	RATE_LIMIT_BACKEND=memory \
	PYTHONWARNINGS=default \
	. $(VENV)/bin/activate 2>/dev/null || true; \
	$(PY) -m pip install -q -r $(REQ) pytest-cov; \
	pytest -q --cov=backend/src --cov-report=term --cov-report=xml

STAGING_URL ?= https://dev.cape-control.com
HEROKU_APP  ?= autorisen

.PHONY: smoke-staging
smoke-staging:  ## Hit health + CSRF endpoints on staging
	@echo "== Smoke test against $(STAGING_URL) =="
	@curl -fsS $(STAGING_URL)/api/health | jq . >/dev/null && echo "✓ /api/health OK"
	@curl -fsS -D- -o /dev/null $(STAGING_URL)/api/auth/csrf >/tmp/csrf_headers.txt && echo "✓ /api/auth/csrf OK"
	@grep -qi 'set-cookie' /tmp/csrf_headers.txt && echo "✓ CSRF cookie present" || (echo "✗ CSRF cookie missing"; exit 1)
