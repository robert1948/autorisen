# Deployment Log

| Date       | Release | Environment | Summary |
|------------|---------|-------------|---------|
| 2025-10-16 | v244    | Heroku prod | Rebuilt backend image with restored auth router, added structured login debug logs, confirmed root JSON health endpoint; smoke tests (`/`, `/api/health`, login flow`) succeeded. |

## Release Notes

### v244 — 2025-10-16

- Repaired FastAPI auth router to use the service layer after a regression.
- Added structured debug logging around the login flow for auditing.
- Introduced root JSON health endpoint to eliminate 404s on `/`.
- Performed cache-busting Docker rebuild, pushed to Heroku, and released via `heroku container:release web`.
- Post-deploy validation: `curl https://autorisen.herokuapp.com/` returns a JSON ok payload.
- Logs: Heroku shows `auth.login.*` entries on login attempts.

*Keep this log updated for every deployment. Include command references, image digests, and any follow-up actions.*
