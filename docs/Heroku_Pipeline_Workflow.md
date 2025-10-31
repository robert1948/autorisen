# Heroku Pipeline Workflow
Staging app: autorisen → smoke test → promote to prod when green.
Health checks: /api/health, /api/auth/csrf
Logs: heroku logs --tail -a autorisen -n 100
