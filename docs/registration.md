# Registration Flow

This MVP implements a two-step registration wizard that adapts to **Customer** and **Developer** roles.

## Backend

- New fields on `users` capture first/last name, role, company, and verification state.
- Profiles are stored in `user_profiles` (`JSONB` on Postgres) to keep role-specific metadata
 flexible.
- `POST /api/auth/register/step1` validates passwords, verifies reCAPTCHA, and issues a short-lived
 `temp_token`.
- `POST /api/auth/register/step2` accepts the `temp_token`, persists the user/profile, and sends a welcome email stub.
 Returns a 7-day access token.
- `POST /api/auth/analytics/track` logs lightweight analytics events (step views, submissions, errors, completion).
- Auth endpoints are protected by SlowAPI rate limits (configurable via `RATE_LIMIT_PER_MIN`).

### Environment variables

```bash
SECRET_KEY=<required>
DATABASE_URL=postgresql+psycopg://devuser:devpass@localhost:5433/devdb
EMAIL_API_KEY=<optional>
REDIS_URL=redis://localhost:6379/0
RECAPTCHA_SECRET=<required in production>
DISABLE_RECAPTCHA=true # convenient for local development
RATE_LIMIT_PER_MIN=10
```

Create and activate a virtualenv, install dependencies, and run migrations from the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
python -m alembic -c backend/alembic.ini upgrade head
```

Start the API:

```bash
python -m uvicorn backend.src.app:app --reload --host 0.0.0.0 --port 8000
```

## Frontend

- React + Vite wizard with React Hook Form + Zod validation mirrors backend constraints.
- Shared password policy and role-specific sections (customer company profile vs. developer skills/availability).
- Google reCAPTCHA component falls back to a local bypass when no site key is provided.
- Successful completion stores tokens via the existing `AuthContext` and redirects to `/onboarding/customer` or `/onboarding/developer`.

### Frontend environment

```bash
VITE_API_BASE=http://localhost:8000/api
VITE_RECAPTCHA_SITE_KEY=<site key>
```

Install dependencies and launch the dev server:

```bash
cd client
npm install
npm run dev
```

## Manual test checklist

1. Load `/register`, choose a role, fill out step 1 (verify password hints + reCAPTCHA).
1. Complete step 2 with role-specific fields.
1. Confirm the backend creates rows in `users` and `user_profiles` and returns tokens.
1. Verify rate limiting by issuing >10 rapid `/api/auth/*` calls (should return HTTP 429).
1. Toggle `DISABLE_RECAPTCHA=false` with valid secrets to validate failures are surfaced.
1. Check `analytics_events` table captures `step_view`, `step_submit`, and `complete` events.
