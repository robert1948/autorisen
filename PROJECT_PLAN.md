# Project Plan

Last updated: 2025-09-22

This file is the canonical project plan derived from the interactive session. It mirrors the saved todo list and is intended to be a single source-of-truth for tracking progress.

## How to use

- The tasks below are expressed with an ID, title, description, and acceptance criteria.
- To update progress, edit this file (or use the repo's task tracking) and update the `Status:` line for the task.
- The agent also maintains an in-memory todo list; to reconcile, say "sync plan" and I'll update both the file and the managed todo list.

## Preconditions (required locally)

- Docker & Docker Compose installed and available on PATH.
- Node (for `npx markdownlint-cli`) and Python 3 available on PATH.
- `pg_isready` or `psql` available for DB readiness checks.

## Tasks

1. Validate docs & run linter
   - Status: Completed
   - Description: Run `markdownlint-cli` across `docs/` and the repo, fix any remaining high-priority markdown issues (MD025, MD022, MD012, MD031, MD040, MD046).
   - Files to check: `docs/DEVELOPMENT_CONTEXT.md`, `docs/*.md`, `README.md`, `Makefile` help text.
   - Acceptance criteria:
     - `docs/DEVELOPMENT_CONTEXT.md` is lint-clean for MD025/MD022.
     - No accidental code fences or duplicate H1s remain.
     - All fixes are minimal and non-destructive.
   - Verify with:

     ```bash
     npx markdownlint-cli "docs/DEVELOPMENT_CONTEXT.md" -f node_modules/markdownlint-cli/rules --disable MD036
     ```

2. Sweep repo for `5173` clarifier
   - Status: not-started
   - Description: Search the repo for occurrences of `5173` and append the clarifier text `(container internal 5173, host 3000)` where appropriate in docs and help text.
   - Files to update may include: `docs/*`, `Makefile`, `README.md`, and any examples.
   - Acceptance criteria: every human-facing reference to `5173` explains the container-vs-host mapping.

3. Verify `docker-compose.yml` network config
   - Status: not-started
   - Description: Confirm `frontend.environment.VITE_API_BASE` is container-internal (`http://backend:8000`) and that service names resolve in the Compose network. Test from the frontend container that `http://backend:8000/api/status` returns 200.
   - Acceptance: container-to-container API calls succeed and Vite proxy no longer shows ECONNREFUSED in logs.

4. Audit and fix client API usage
   - Status: not-started
   - Description: Ensure client code uses `import.meta.env.VITE_API_BASE` with safe fallbacks and does not contain hardcoded `localhost:8001` addresses.
   - Files to inspect: `client/src/api/*.js`, `client/src/pages/*.jsx`.
   - Acceptance: repo search for `localhost:8001` returns zero results; dev proxy works via relative `/api` when appropriate.

5. Add Heroku deploy helper & Makefile target
   - Status: not-started
   - Description: Create `scripts/deploy_heroku_container.sh` and a `Makefile` target `heroku-deploy` that document commands to build and push a container to Heroku (only create scripts; do NOT invoke Heroku CLI or change remote settings).
   - Acceptance: helper script exists, is executable, and documented; no Heroku credentials used or committed.

6. Add local smoke/integration tests
   - Status: not-started
   - Description: Create a small `scripts/smoke_local.sh` (or `tests/smoke_test.sh`) that performs the Makefile smoke checks automatically (backend health, Postgres ready, frontend reachable). Add a `make smoke` improvement if needed to call the script.
   - Acceptance: `./scripts/smoke_local.sh` returns non-zero on failures and zero on success; tests are simple and safe for local dev.

7. Update quickstart & README consistency
   - Status: not-started
   - Description: Ensure `docs/DEVELOPMENT_CONTEXT.md`, `README.md`, and `Makefile` help text are consistent (same ports, commands, `make dev-up`, `make migrate`, `make smoke`).
   - Acceptance: quickstart steps in `README.md` and `docs/DEVELOPMENT_CONTEXT.md` match and include port clarifier for Vite.

8. Run compose bring-up and validate services
   - Status: not-started
   - Description: Bring the stack up locally with `make dev-up` / `docker compose up -d`, then run smoke tests and collect logs for frontend/backend to confirm healthy state.
   - Acceptance: backend responds at `http://localhost:8000/api/status`, frontend served at `http://localhost:3000`, DB `pg_isready` on host port `5433`.

9. Document risks, edge cases, and rollback steps
   - Status: not-started
   - Description: Write `docs/DEVELOPMENT_RISKS.md` listing known risks (Heroku settings unchanged requirement, port conflicts, env file mismatches) and include rollback/revert steps.
   - Acceptance: file created and referenced from `DEVELOPMENT_CONTEXT.md` or `README.md`.

10. Final report & handoff
    - Status: not-started
    - Description: Produce a concise completion report mapping each user requirement to the implemented changes and validation results. Include run commands and exact steps the user must run to deploy to Heroku manually (no automation).
    - Acceptance: report added as `docs/DEVELOPMENT_CHANGELOG.md` and shared in the chat.

---

## Quick commands

View the plan file:

```bash
cat PROJECT_PLAN.md
```

Run the markdown linter (recommended before merging doc edits):

```bash
npx markdownlint-cli "docs/**/*.md" -f node_modules/markdownlint-cli/rules --disable MD036 || true
```

To ask the agent to sync the in-memory todo list with this on-disk plan, run:

```bash
# Tell the assistant in chat: "sync plan"
```

If you want me to make this file a different name or add owners/estimates, tell me and I'll update it.
