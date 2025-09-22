# Local development with Docker and Heroku container deploy (no Actions triggered)

This document explains how to run Autorisen locally using Docker Compose, build and test images, and how to update the Heroku container without triggering GitHub Actions.

## Prerequisites

- Docker and Docker Compose installed
- Heroku CLI installed locally (for container pushes)
- Copy `.env.example` to `.env` and fill values before running

## Local development with Docker Compose

1. Prepare envs

```bash
cp .env.example .env
# Edit .env to set your DB credentials and other secrets
```

```bash
docker build -t autorisen:dev .
docker run --rm autorisen:dev pytest -q
```

1. Build and run services

```bash
# builds backend image (uses backend/Dockerfile target 'backend')
docker compose up --build
```

1. Run tests inside container

```bash
# build image first
docker build -t autorisen:dev .
# run tests
docker run --rm autorisen:dev pytest -q
```

### Avoiding host Postgres port conflict

- This repo maps Postgres to host port 5433 by default in `docker-compose.yml` ("5433:5432").
- If you want the default 5432 on host, change the mapping but ensure no host Postgres is running.

### Manual Heroku container deploy (safe, local)

```bash
# login to registry
heroku container:login
# build and push the web image to Heroku container registry
heroku container:push web -a <HEROKU_APP_NAME>
# release the image
heroku container:release web -a <HEROKU_APP_NAME>
# optionally view logs
heroku logs --tail -a <HEROKU_APP_NAME>
```

Important: Do not push commits to `main` if you want to avoid triggering Actions. The steps above use local CLI commands and the Heroku registry; they won't trigger GitHub Actions.

### Troubleshooting

- If `docker compose up` fails due to ports, change the port mapping in `docker-compose.yml` or stop the conflicting service.
- If Heroku rejects push, verify `HEROKU_API_KEY` and `HEROKU_APP_NAME` are correct.

