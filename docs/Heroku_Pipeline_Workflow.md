# Heroku Container Pipeline – Workflow (Autorisen → Production)

This repo deploys the FastAPI backend (and optionally the frontend) to Heroku’s container stack.

- **Staging app**: `autorisen`
- **Prod app**: (optional) `cape-control` (set when ready)
- All commands run from repo root on a machine with Docker + Heroku CLI logged in.

---

## 1) Build & Push (staging)

```bash
# Login once
heroku container:login

# Build locally (uses Dockerfile at project root)
docker build -t autorisen:local .

# Push & release to Heroku (staging)
heroku container:push web -a autorisen
heroku container:release web -a autorisen

.PHONY: heroku-domain heroku-ssl heroku-warm
heroku-domain:
heroku domains:add dev.cape-control.com -a autorisen || true
heroku domains -a autorisen

heroku-ssl:
heroku certs:auto:enable -a autorisen || true
heroku certs:auto -a autorisen
heroku certs -a autorisen

heroku-warm:
curl -sS https://dev.cape-control.com/api/health || true
