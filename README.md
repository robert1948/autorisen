# CapeControl (fresh)

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

1. Add a `Procfile` at the repository root to run the FastAPI app, for example:

```text
web: uvicorn backend.src.app:app --host=0.0.0.0 --port=${PORT}
```

1. Commit and push to Heroku:

```bash
git add Procfile
git commit -m "Add Procfile for Heroku"
git push heroku main
```

1. Environment variables & logs:

```bash
heroku config:set SECRET_KEY=... DATABASE_URL=...
heroku logs --tail
```

CI/CD note: The repo already expects `HEROKU_API_KEY` and `HEROKU_APP_NAME` to be set in GitHub Actions secrets for automated
deployment.

## Agents Framework

- Create a local `.env.dev` (keep it out of version control) before running the agent make targets.
  - Include:
    - `GH_TOKEN=<github token with repo + workflow>`
    - `HEROKU_API_KEY=<Heroku API Key>`
    - `HEROKU_APP_NAME=autorisen`
- Agent specs live under `agents/<slug>/agent.yaml` with optional tests in `agents/<slug>/tests/`.
- Tool configuration templates live in `config/<env>/tools/` and are shared by the agents listed in `agents/registry.yaml`.
- Helpful targets:
  - `make agents-new name=<slug>` scaffolds a starter agent folder.
  - `make agents-validate` runs `scripts/agents_validate.py` to enforce registry schema.
  - `make agents-test` runs targeted pytest coverage (`tests/test_agents_tooling.py`).
- Run `make agents-run name=<slug> task="..."` to exercise adapters (set `AGENTS_ENV` or `--env` for config swaps).
- GitHub Actions checks `.github/workflows/agents-validate.yml` on PRs touching specs, tool configs, or helper scripts.

## ChatKit Integration (scaffold)

- Backend exposes `/api/chatkit/token` to mint short-lived client tokens (see `backend/src/modules/chatkit`).
- Configure ChatKit issuance with `CHATKIT_APP_ID`, `CHATKIT_SIGNING_KEY`, and optional settings for
   `CHATKIT_AUDIENCE`, `CHATKIT_ISSUER`, and `CHATKIT_TOKEN_TTL_SECONDS`.
- `/api/chatkit/tools/{tool_name}` invokes onboarding/support/energy/money adapters and records events in
   `app_chat_events`.
- `/api/flows/run` executes orchestrated tool sequences (tie runs to an agent slug/version when needed).
- Flow runs persist in `flow_runs`, enabling the UI to surface history using the returned `run_id`.
- `/api/flows/onboarding/checklist` and `/api/flows/runs` feed the onboarding progress card in the SPA.
- `/api/agents` backs CRUD for the agent registry (agents and versions).
- Agent registry UI lets developers create agents, add versions, and publish the latest release.
- Manifest editor modal enables editing manifests, creating versions, and previewing validation output.
- SPA auth context manages login/register flows, token storage with auto refresh, and guarded onboarding/developer areas.
- `/api/marketplace/agents` serves the public directory (detail modal fetches `/api/marketplace/agents/{slug}`).
- Marketplace modal can invoke `/api/flows/run` with an agent slug to preview tool output.
- Chat thread and event tables originate from migration `c1e0cc70f7a4_add_chatkit_tables.py` and models in
   `backend/src/db/models.py`.
- Frontend wraps the app with `ChatKitProvider` and adds a Support modal launcher in the top navigation.
- Landing page highlights onboarding and developer workbench experiences that spin up ChatKit sessions via shared modals.
- Developer section surfaces the agent registry and creation form powered by `/api/agents`.
- Replace placeholder logic in `backend/src/modules/chatkit/service.py` and client chat components.
   Swap in the real ChatKit SDK when ready.
- Set `VITE_CHATKIT_WIDGET_URL` to the hosted ChatKit Web SDK script so the modal can mount the official widget.
