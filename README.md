# Autorisen (fresh)

FastAPI backend with /api/health, devcontainer, and CI/CD to Heroku.

## Local (devcontainer)

Start the backend locally:

```bash
uvicorn backend.src.app:app --host 0.0.0.0 --port 8000 --reload
```

## Heroku

Set GitHub Actions secrets:

- `HEROKU_API_KEY`
- `HEROKU_APP_NAME = autorisen`

### Deploying with the Heroku CLI (recommended quick flow)

1. Install & verify Heroku CLI:

```bash
heroku --version
heroku login
```

1. Create or attach to the Heroku app:

```bash
heroku create autorisen
# or attach to existing
heroku git:remote -a autorisen
```

2. Add a `Procfile` at the repository root to run the FastAPI app, for example:

```text
web: uvicorn backend.src.app:app --host=0.0.0.0 --port=${PORT}
```

3. Commit and push to Heroku:

```bash
git add Procfile
git commit -m "Add Procfile for Heroku"
git push heroku main
```

4. Environment variables & logs:

```bash
heroku config:set SECRET_KEY=... DATABASE_URL=...
heroku logs --tail
```

CI/CD note: The repo already expects `HEROKU_API_KEY` and `HEROKU_APP_NAME` to be set in GitHub Actions secrets for automated deployment.

## Agents Framework

- Create a local `.env.dev` (keep it out of version control) and export the placeholders below before running the agent make targets:
  - `GH_TOKEN=<github token with repo + workflow>`
  - `HEROKU_API_KEY=<Heroku API Key>`
  - `HEROKU_APP_NAME=autorisen`
- Agent specs live under `agents/<slug>/agent.yaml` with optional tests in `agents/<slug>/tests/`.
- Tool configuration templates are under `config/<env>/tools/` and are shared by the agents defined in the registry (`agents/registry.yaml`).
- Helpful targets:
  - `make agents-new name=<slug>` scaffolds a new agent folder with a starter spec.
  - `make agents-validate` runs `scripts/agents_validate.py` to ensure every agent listed in the registry meets the minimum schema.
  - `make agents-test` runs targeted pytest coverage for the local adapters (`tests/test_agents_tooling.py`).
- `make agents-run name=<slug> task="..."` invokes `scripts/agents_run.py` to surface adapter readiness (use `AGENTS_ENV` or `--env` to swap config sets).
- GitHub Actions runs `.github/workflows/agents-validate.yml` on PRs touching agent specs, tool configs, or the helper scripts to keep the registry healthy.

## ChatKit Integration (scaffold)

- Backend exposes `/api/chatkit/token` to mint short-lived client tokens (see `backend/src/modules/chatkit`).
- Configure ChatKit issuance via `CHATKIT_APP_ID`, `CHATKIT_SIGNING_KEY`, optional `CHATKIT_AUDIENCE`, `CHATKIT_ISSUER`, and `CHATKIT_TOKEN_TTL_SECONDS` env vars.
- `/api/chatkit/tools/{tool_name}` invokes backend adapters (onboarding/support/energy/money) and logs usage in `app_chat_events`.
- `/api/flows/run` executes orchestrated tool sequences using the shared ChatKit adapters (optionally bound to an agent slug/version).
- Flow runs are persisted (`flow_runs` table) so the UI can display history using the returned `run_id`.
- `/api/flows/onboarding/checklist` and `/api/flows/runs` power the onboarding progress card in the SPA.
- `/api/agents` provides CRUD endpoints for the agent registry (agents + versions).
- Agent registry UI allows creating agents, adding versions, and publishing the latest release.
- Manifest editor modal lets developers edit agent manifests and create new versions with preview/validation.
- SPA auth context provides login/register forms, stores tokens with auto refresh, and gates onboarding/developer sections.
- `/api/marketplace/agents` powers a public directory of published agents rendered on the landing page (detail modal fetches `/api/marketplace/agents/{slug}`).
- Marketplace modal can trigger `/api/flows/run` with an agent slug to preview tool output.
- Chat thread/event tables are defined via the Alembic migration `c1e0cc70f7a4_add_chatkit_tables.py` and SQLAlchemy models in `backend/src/db/models.py`.
- Frontend wraps the app with `ChatKitProvider` and includes a Support modal launcher in the top navigation.
- Landing page highlights Onboarding + Developer workbench experiences that launch ChatKit sessions via shared modal scaffolding.
- Developer section surfaces the agent registry and creation form backed by `/api/agents`.
- Replace the placeholder logic in `backend/src/modules/chatkit/service.py` and the client chat components with the real ChatKit SDK when ready.
- Set `VITE_CHATKIT_WIDGET_URL` to the hosted ChatKit Web SDK script so the modal can dynamically mount the official widget.
