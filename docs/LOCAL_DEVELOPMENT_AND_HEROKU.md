# Local development and Heroku Container deployment

This document explains how to run the autorisen project locally with Docker Compose and how to push a container to Heroku's Container Registry.

## 1. Local development (Docker Compose)

### Local prerequisites

- Docker and Docker Compose installed
- PostgreSQL client (`psql`) installed (optional but useful)
- A local `.env` file with database credentials (copy from `.env.example`)

### Quick checklist

1. Copy example env file and edit values:

```bash
cp .env.example .env
# Edit .env to set POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD or set DATABASE_URL
```

1. Recommended `.env` values for local compose usage:

```text
POSTGRES_DB=autorisen_dev
POSTGRES_USER=dev_user
POSTGRES_PASSWORD=dev_password
DATABASE_URL=postgresql://dev_user:dev_password@db:5432/autorisen_dev
```

1. Start the stack:

```bash
docker compose up --build
```

1. Verify services:

- Frontend: <http://localhost:5173>
- Backend: <http://localhost:8000> (health: `/api/health`)
- Postgres (host port 5433) if needed: `psql -h localhost -p 5433 -U dev_user autorisen_dev`

### Local notes

- The Compose setup uses `db` as the Postgres host. The top-level Postgres host port is mapped to host `5433` to avoid collisions with a local Postgres running on `5432`.
- If you prefer to use a host Postgres instance, set `DATABASE_URL` in your `.env` to point at `host.docker.internal:5432` and ensure your host Postgres accepts connections from Docker and the user/password match.

---

## 2. Basic local Postgres setup (without compose)

Install Postgres (example for Ubuntu):

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo -u postgres createuser dev_user || true
sudo -u postgres createdb -O dev_user autorisen_dev || true
sudo -u postgres psql -c "ALTER USER dev_user WITH PASSWORD 'dev_password';"
```

---

## 3. Deploying to Heroku (Container Registry)

### Heroku prerequisites

- Heroku CLI installed and you're logged in: `heroku login`
- You must be a Heroku app owner or have access to the target app (e.g., `autorisen`)

Build, push and release container (no CI required):

```bash
# Login to the Heroku container registry
heroku container:login

# Build and push (web process)
heroku container:push web -a autorisen

# Release the pushed image
heroku container:release web -a autorisen

# Tail logs and open the app
heroku logs -a autorisen --tail
heroku open -a autorisen
```

### Heroku notes

- If you want CI to deploy, ensure the GitHub repository has these secrets set: `HEROKU_API_KEY`, `HEROKU_APP_NAME` (or `HEROKU_APP_PROD` / `HEROKU_APP_STAGING`), and `HEROKU_EMAIL`. Without them the deploy job in CI will be skipped.

---

## 4. Avoid triggering GitHub Actions for this documentation update

When committing documentation changes that should not trigger Actions, include `[skip ci]` or `[ci skip]` in the commit message.

Example:

```bash
git add docs/LOCAL_DEVELOPMENT_AND_HEROKU.md
git commit -m "docs: add local dev + heroku container guide [skip ci]"
git push
```

---

## 5. Troubleshooting

- If the backend returns 500s, check logs:

```bash
docker compose logs backend --tail=200
```

- Check environment variables are set in `.env` and Docker Compose environment.
- If Heroku deploy fails due to secrets missing, add them in GitHub repo settings or deploy via the Heroku CLI locally.

---

If you'd like, I can also:

- Add a short `docs/README.md` index and link this file.
- Open a small PR with these changes instead of pushing to `main`.
