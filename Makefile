SHELL := /bin/bash
PY := python3
PIP := $(PY) -m pip
VENV := .venv
REQ := requirements.txt
IMAGE ?= autorisen:local
PORT ?= 8000

.PHONY: help venv install format lint test build docker-build docker-run docker-push deploy-heroku clean plan-validate plan-open heroku-deploy-stg

help:
	@echo "Available targets:"
	@echo "  make venv            - create a virtualenv in $(VENV)"
	@echo "  make install         - install project dependencies (uses $(REQ) if present)"
	@echo "  make format          - run code formatters (black/isort)"
	@echo "  make lint            - run linters (ruff)"
	@echo "  make test            - run tests (pytest)"
	@echo "  make docker-build    - build docker image (IMAGE=$(IMAGE))"
	@echo "  make docker-run      - run docker image locally (exposes $(PORT))"
	@echo "  make deploy-heroku   - build/push/release to Heroku Container Registry (requires HEROKU_APP_NAME and heroku CLI)"
	@echo "  make clean           - remove common build artifacts"

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

.PHONY: agents-new agents-validate agents-test agents-run

agents-new:
	@[ -n "$$name" ] || (echo "Usage: make agents-new name=<slug>"; exit 1)
	@mkdir -p agents/$(name)/tests && \
	printf "name: %s\nrole: <fill>\nmodel: { provider: openai, name: gpt-4.1, temperature: 0.2 }\npolicies: { allow_tools: [] }\ncontext: { system_prompt: |\n  You are %s. }\n" "$(name)" "$(name)" > agents/$(name)/agent.yaml
	@echo "Created agents/$(name)"

agents-validate:
	@python3 scripts/agents_validate.py agents/registry.yaml

agents-test:
	@python3 -m pytest -q tests/test_agents_tooling.py

agents-run:
	@[ -n "$$name" ] || (echo "Usage: make agents-run name=<slug> task=\"...\""; exit 1)
	@python3 scripts/agents_run.py --agent $$name --task "$$task"
