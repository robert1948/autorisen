# API Documentation – Autorisen (2025)
> Keep this in sync with the FastAPI OpenAPI schema. Add examples.
> Stack: Python 3.12, FastAPI 0.110.0, Heroku buildpack deployment

## Auth
- `POST /auth/register` – Create user/developer
- `POST /auth/login` – Obtain JWT
- `GET /auth/me` – Current profile (user/developer)
- Tokens: Bearer JWT in `Authorization` header

## Health & Meta
- `GET /health` – liveness
- `GET /version` – app version (optional)

## Analytics
- `POST /analytics/metric` – submit metric
- `GET /analytics/summary` – aggregate view

## Alerts
- `POST /alerts` – create alert
- `GET /alerts` – list alerts

## Conventions
- **Errors:** JSON `{ "detail": "..." }`
- **Pagination:** `?limit=&offset=` (where applicable)
- **Dates:** ISO 8601
