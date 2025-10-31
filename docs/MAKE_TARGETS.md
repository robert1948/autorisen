# Make Targets

| Target | Description |
| --- | --- |
| `help` | List Make targets (auto-docs) |
| `venv` | Create a virtualenv in $(VENV) |
| `install` | Install project dependencies (uses $(REQ) if present) |
| `format` | Run code formatters (black/isort) |
| `lint` | Run ruff linter |
| `test` | Run tests (pytest) |
| `docker-build` | Build docker image (IMAGE=$(IMAGE)) |
| `docker-run` | Run docker image locally (exposes $(PORT)) |
| `docker-push` | Push local image tag to $(REGISTRY) (set REGISTRY=…) |
| `deploy-heroku` | Build/push/release to Heroku (retries on transient failures) |
| `heroku-deploy-stg` | Quick push/release to $(HEROKU_APP) |
| `heroku-logs` | Tail Heroku dyno logs |
| `heroku-run-migrate` | Run Alembic upgrade inside a one-off Heroku dyno |
| `github-update` | Fast-forward the current branch from origin |
| `clean` | Remove common build artifacts |
| `plan-validate` | Validate plan CSV with tools/validate_plan_csv.py |
| `plan-open` | Open plan & Codex project plan |
| `migrate-up` | Alembic upgrade head |
| `migrate-revision` | Create Alembic revision: make migrate-revision message="desc" |
| `sitemap-generate-dev` | Generate $(PUBLIC_DIR)/$(SITEMAP_XML) from $(SITEMAP_DEV_TXT) |
| `sitemap-generate-prod` | Generate $(PUBLIC_DIR)/$(SITEMAP_XML) from $(SITEMAP_PROD_TXT) |
| `verify-sitemap` | Verify routes from FILE=... at BASE=... |
| `verify-sitemap-dev` | Curl-check all dev routes |
| `verify-sitemap-prod` | Curl-check all prod routes |
| `crawl-local` | Run tools/crawl_sitemap.py against http://localhost:3000 |
| `crawl-dev` | Run crawler against dev.cape-control.com |
| `crawl-prod` | Run crawler against cape-control.com |
| `crawl` | Default crawl |
| `sitemap-svg` | Render sitemap mermaid to SVG |
| `agents-new` | Create a new agent scaffold: make agents-new name=<slug> |
| `agents-validate` | Validate agents registry |
| `agents-test` | Run agents unit tests |
| `agents-run` | Run an agent: make agents-run name=<slug> task="..." |
| `codex-check` | Verify Codex context files & VS Code settings |
| `codex-open` | Open Codex prompt and settings in VS Code |
| `codex-docs-lint` | Markdown lint all docs (installs markdownlint-cli if needed) |
| `codex-docs-fix` | Auto-fix Markdown lint issues |
| `codex-ci-validate` | Run pre-commit hooks (install if needed) |
| `codex-plan-diff` | Check plan sync |
| `codex-plan-apply` | Apply plan sync |
| `codex-test-heal` | Regenerate fixtures (best-effort) then pytest |
| `codex-test` | Run pytest with CI-safe defaults |
| `codex-test-cov` | Run pytest with coverage |
| `codex-test-dry` | Run pytest (allow failures; no venv bootstrap) |
| `codex-run` | Full Codex pass (docs lint, pre-commit, pytest) |
| `smoke-staging` | Health + CSRF discovery (OpenAPI) against $(STAGING_URL) |
| `smoke-local` | Health + CSRF probe against localhost backend |
| `csrf-probe-staging` | Direct CSRF probe (staging) |
| `csrf-probe-local` | Direct CSRF probe (local) |
| `codex-smoke` | Combined staging smoke & CSRF |
| `smoke-prod` | Quick production health (no CSRF probe) |
| `codex-test-strict` | Run pytest with warnings as errors |
| `dockerhub-login` | Login to Docker Hub (interactive) |
| `dockerhub-logout` | Logout from Docker Hub |
| `dockerhub-setup-builder` | Ensure Buildx 'multiarch-builder' is ready |
| `dockerhub-build` | Local single-arch build (no push) |
| `dockerhub-push` | Push local :$(SAFE_VERSION) and :latest |
| `dockerhub-build-push` | Convenience target: build (single-arch) then push |
| `dockerhub-release` | Multi-arch buildx + push (recommended) |
| `dockerhub-update-description` | PATCH repository description via Docker Hub API (needs DOCKERHUB_TOKEN) |
| `dockerhub-clean` | Prune dangling images |
| `playbooks-overview` | Rebuild docs/PLAYBOOKS_OVERVIEW.md |
| `playbook-overview` | Alias for playbooks-overview |
| `playbook-open` | Open docs/PLAYBOOKS_OVERVIEW.md in VS Code if available |
| `playbook-badge` | Print current playbooks % (from overview) |
| `playbook-new` | Create playbook: make playbook-new NUMBER=02 TITLE="X" OWNER="Robert" AGENTS="Codex, CapeAI" PRIORITY=P1 |
| `playbooks-check` | Validate required headers exist in all playbooks |
| `design-sync` | Aggregate design playbooks into JSON inventory |
| `design-validate` | Validate design playbooks (use PLAYBOOK=slug to scope) |
