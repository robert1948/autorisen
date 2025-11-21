# Make Targets Reference

Generated from the annotated recipes (`##` comments) in the Makefile as of **November 14, 2025**.

| Target | Description |
|---|---|
| `agents-new` | Create a new agent scaffold (`make agents-new name=<slug>`). |
| `agents-run` | Execute an agent with a provided task payload. |
| `agents-test` | Run agent tooling unit tests. |
| `agents-validate` | Validate the `agents/registry.yaml` configuration. |
| `chatkit-dev` | Launch the backend in WebSocket debug mode. |
| `clean` | Remove common build artifacts and caches. |
| `codex-agent-dev` | Run the AgentDeveloper Phase 2 workflow (DB migrations + tests). |
| `codex-agent-marketplace` | Scaffold marketplace infrastructure using Codex helpers. |
| `codex-check` | Verify Codex context files and VS Code settings. |
| `codex-ci-validate` | Run `pre-commit` hooks across the repository. |
| `codex-docs-fix` | Auto-fix Markdown lint issues via `markdownlint`. |
| `codex-docs-lint` | Lint Markdown files (installs `markdownlint-cli` if needed). |
| `codex-generate-agent` | Generate a new agent from Codex templates. |
| `codex-generate-tests` | Generate an expanded test suite with Codex helpers. |
| `codex-open` | Open Codex prompt and settings in VS Code. |
| `codex-plan-apply` | Apply `scripts/plan_sync.py --apply` to refresh docs. |
| `codex-plan-diff` | Run `scripts/plan_sync.py --check-only` to verify alignment. |
| `codex-run` | Perform the full Codex workflow (docs lint → pre-commit → pytest). |
| `codex-smoke` | Execute staging smoke plus CSRF probes in one step. |
| `codex-test` | Run pytest with the CI-safe environment overrides. |
| `codex-test-cov` | Run pytest with coverage output. |
| `codex-test-dry` | Run pytest allowing failures without bootstrapping the venv. |
| `codex-test-heal` | Regenerate fixtures (best-effort) and rerun pytest. |
| `codex-test-strict` | Run pytest treating all warnings as errors. |
| `crawl` | Default crawl; aliases to `crawl-local`. |
| `crawl-dev` | Crawl the deployed staging site (`https://dev.cape-control.com`). |
| `crawl-local` | Crawl the local frontend at `http://localhost:3000`. |
| `crawl-prod` | Crawl the production marketing site. |
| `csrf-probe-local` | Hit `/api/auth/csrf` on localhost and inspect headers. |
| `csrf-probe-staging` | Hit `/api/auth/csrf` on staging and inspect headers. |
| `deploy-heroku` | Build, push, and release containers to staging and production with retries, migrations, and health checks. |
| `docker-build` | Build the local Docker image (`$(IMAGE)`). |
| `docker-push` | Push `$(IMAGE)` to `$(REGISTRY)` (requires `REGISTRY`). |
| `docker-run` | Run `$(IMAGE)` locally on `$(PORT)`. |
| `dockerhub-build` | Build a single-arch Docker Hub image (no push). |
| `dockerhub-build-push` | Build then push the single-arch Docker Hub image. |
| `dockerhub-clean` | Prune dangling Docker images. |
| `dockerhub-login` | Log in to Docker Hub interactively. |
| `dockerhub-logout` | Log out from Docker Hub. |
| `dockerhub-push` | Push `:$(SAFE_VERSION)` and `:latest` tags to Docker Hub. |
| `dockerhub-release` | Perform a multi-arch Buildx build and push with extra tags. |
| `dockerhub-setup-builder` | Ensure the Buildx `multiarch-builder` exists and is active. |
| `dockerhub-update-description` | PATCH the Docker Hub repo description via API (needs `DOCKERHUB_TOKEN`). |
| `docs` | Open the documentation hub and quick reference files. |
| `docs-update` | Review the documentation update checklist. |
| `docs-workspace` | Open the documentation-focused VS Code workspace. |
| `format` | Run `black` and `isort` across the repo. |
| `github-update` | Fast-forward the current branch from `origin`. |
| `help` | Display the auto-generated target list. |
| `heroku-config-push` | Push the local `.env` to Heroku config vars (with confirmation). |
| `heroku-deploy-prod` | Push and release the container to production only. |
| `heroku-deploy-stg` | Push and release the container to staging only. |
| `heroku-logs` | Tail logs for `$(HEROKU_APP_NAME)`. |
| `heroku-run-migrate` | Run Alembic upgrade head on the Heroku app. |
| `heroku-shell` | Open a bash shell in the dyno. |
| `heroku-status` | List dynos and check the `/api/health` + `/api/version` endpoints. |
| `install` | Install Python dependencies (prefers `requirements.txt`). |
| `lint` | Run the Ruff linter. |
| `migrate-revision` | Create a new Alembic revision (`make migrate-revision message="desc"`). |
| `migrate-up` | Apply migrations locally via Alembic upgrade head. |
| `new-task-capsule` | Generate a Task Capsule markdown file (advanced helper also links plan rows when present). |
| `payment-test` | Exercise PayFast HTTP endpoints via curl. |
| `payments-checkout` | Emit a sample PayFast checkout payload script. |
| `plan-open` | Open the plan CSV and Markdown snapshot. |
| `plan-validate` | Validate the authoritative plan CSV. |
| `playbook-badge` | Read the current playbook completion percentage. |
| `playbook-new` | Create a new playbook from the template (number/title/owner required). |
| `playbook-open` | Open the playbook overview in VS Code. |
| `playbook-overview` | Alias for `playbooks-overview`. |
| `playbook-sync` | Sync the playbook tracker docs from CSV. |
| `playbooks-check` | Validate required headers exist in every playbook. |
| `playbooks-overview` | Regenerate `docs/PLAYBOOKS_OVERVIEW.md`. |
| `project-info` | Print project status, version, and top priorities. |
| `project-overview` | Generate `docs/PROJECT_OVERVIEW.md` from the plan CSV. |
| `sitemap-generate-dev` | Build `$(PUBLIC_DIR)/$(SITEMAP_XML)` from `$(SITEMAP_DEV_TXT)`. |
| `sitemap-generate-prod` | Build `$(PUBLIC_DIR)/$(SITEMAP_XML)` from `$(SITEMAP_PROD_TXT)`. |
| `sitemap-svg` | Render the Mermaid sitemap diagram to SVG. |
| `smoke-local` | Run local health + CSRF probes. |
| `smoke-prod` | Run a production health check (no CSRF probe). |
| `smoke-staging` | Run staging health checks and scan OpenAPI for CSRF endpoints. |
| `test` | Execute pytest (best-effort). |
| `test-agents` | Run agent-focused tests under `tests_enabled/agents`. |
| `venv` | Create the local virtual environment (`.venv`). |
| `verify-sitemap` | Verify all routes from a given sitemap file against a base URL. |
| `verify-sitemap-dev` | Verify the dev sitemap routes. |
| `verify-sitemap-prod` | Verify the production sitemap routes. |
| `websocket-test` | Perform WebSocket health and messaging checks. |
