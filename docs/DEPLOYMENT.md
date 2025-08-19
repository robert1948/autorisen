# Deployment (Quick Start)
**Targets:** Local (Docker), Heroku Staging (`autorisen`), Heroku Production (`capecraft`).

## Local (Docker Compose)
```bash
docker compose up --build
# API at http://localhost:8000
```
**Env:** copy `.env.example` → `.env.dev` and set values (DB URL, SECRET_KEY, etc.).

## Heroku Staging
```bash
# Set buildpacks (python only, unless you serve static assets)
heroku buildpacks:clear -a autorisen
heroku buildpacks:add heroku/python -a autorisen

# Set runtime (pin Python)
echo "python-3.11.9" > runtime.txt

# Push via GitHub Actions or manual
git push heroku main

# Config vars
heroku config:set ENVIRONMENT=staging SECRET_KEY=... DATABASE_URL=... -a autorisen
```

## Database Migrations
```bash
# Local
alembic upgrade head

# Heroku
heroku run -a autorisen alembic upgrade head
```

## Rollback
- Revert to previous Heroku release:
```bash
heroku releases -a autorisen
heroku rollback vNN -a autorisen
```
