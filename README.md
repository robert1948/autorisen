# Autorisen (fresh)

FastAPI backend with /api/health, devcontainer, and CI/CD to Heroku.

## Local (devcontainer)
uvicorn backend.src.app:app --host 0.0.0.0 --port 8000 --reload

## Heroku
Set GitHub Actions secrets:
- HEROKU_API_KEY
- HEROKU_APP_NAME = autorisen
