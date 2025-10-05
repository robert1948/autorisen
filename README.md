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

## Agents Setup

Create a local `.env.dev` (keep it out of version control) with the following placeholders and export them before running agent make targets:

```
GH_TOKEN=<github token with repo + workflow>
HEROKU_API_KEY=<Heroku API Key>
HEROKU_APP_NAME=autorisen
```
