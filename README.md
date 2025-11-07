# CapeControl 251107A - Production Ready ✅

![Production Status](https://img.shields.io/badge/Production-Live-green?style=flat-square)
![Auth System](https://img.shields.io/badge/Auth_System-Complete-green?style=flat-square)
![Security](https://img.shields.io/badge/Security-Hardened-green?style=flat-square)
![Logo Assets](https://img.shields.io/badge/Logo_Assets-Optimized-green?style=flat-square)

FastAPI backend with production-grade security, React frontend with CapeControl authentication system, deployed on Heroku with container deployment.

🚀 **Live Application**: https://autorisen-dac8e65796e7.herokuapp.com

## 🔐 Authentication System (PRODUCTION READY)

Complete CapeControl authentication UI implementation with production-grade security:

### 🛡️ Production Security Features

- **CSRF Protection**: Enabled with token validation on all state-changing operations
- **Environment Security**: `ENV=prod`, `DEBUG=false` for production hardening
- **reCAPTCHA**: Enabled (`DISABLE_RECAPTCHA=false`) for bot protection
- **JWT Authentication**: Secure token-based authentication with proper validation
- **Input Validation**: Pydantic models with comprehensive data validation
- **HTTPS**: All endpoints secured with TLS encryption

### 🎯 Authentication Components

- **LoginPage** (`/auth/login`) - Email/password, social login, MFA integration
- **MFAChallenge** (`/auth/mfa`) - 6-digit code verification with timer/resend
- **MFAEnroll** (`/account/mfa-enroll`) - QR code setup for authenticator apps
- **Logo System** - Multi-size logos with favicon.ico and PWA manifest

### 🧪 Production Validation

✅ CSRF endpoints: `https://autorisen-dac8e65796e7.herokuapp.com/api/auth/csrf`  
✅ User registration with CSRF protection  
✅ JWT token authentication and validation  
✅ Protected endpoint security verification

### 🎨 Logo Assets

The system includes optimized logo variants:
- `favicon.ico` - Multi-size ICO for browsers
- `icons/logo-*.png` - 64x64, 128x128, 256x256, 512x512 variants
- `icons/apple-touch-icon.png` - iOS home screen
- `icons/android-chrome-*.png` - Android/PWA icons
- Smart `Logo` component automatically serves appropriate sizes

### 🧪 Testing Locally

```bash
cd client && npm run dev
```

Test URLs:
- http://localhost:3000/auth/login
- http://localhost:3000/auth/mfa  
- http://localhost:3000/account/mfa-enroll
- http://localhost:3000/test/logo (logo showcase)

FastAPI backend with /api/health, devcontainer, and CI/CD to Heroku.

## Playbooks

- Regenerate the overview table: `make playbook-overview`
- Open the overview in VS Code (requires the `code` CLI): `make playbook-open`
- New playbook from the template: `make playbook-new NUMBER=07 TITLE="New Initiative" OWNER="Name" AGENTS="Codex" PRIORITY=P2`

Keep `docs/PLAYBOOKS_OVERVIEW.md` in sync with status changes before merging.

## Local (devcontainer)

Start the backend locally:

```bash
uvicorn backend.src.app:app --host 0.0.0.0 --port 8000 --reload
```

## Heroku

Set GitHub Actions secrets:

- `HEROKU_API_KEY`
- `HEROKU_APP_NAME=autorisen`

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

1. Add a `Procfile` at the repository root to run the FastAPI app, for example:

   ```text
   web: uvicorn backend.src.app:app --host=0.0.0.0 --port=${PORT}
   ```

1. Commit and push to Heroku:

   ```bash
   git add Procfile
   git commit -m "Add Procfile for Heroku"
   git push heroku main
   ```

1. Environment variables & logs:

   ```bash
   heroku config:set SECRET_KEY=... DATABASE_URL=...
   heroku logs --tail
   ```

CI/CD note: The repo already expects `HEROKU_API_KEY` and `HEROKU_APP_NAME` to be set in GitHub Actions
secrets for automated deployment.

## Authentication providers

- **Email verification**
  - Backend: set `EMAIL_TOKEN_SECRET`, `FROM_EMAIL=contact@cape-control.com`, and the SMTP trio
    `SMTP_HOST`, `SMTP_USERNAME`, `SMTP_PASSWORD` (plus optional `SMTP_PORT`, `SMTP_USE_TLS`,
    `SMTP_USE_SSL`).
  - Routes: `POST /api/auth/verify/resend` (CSRF-protected) to resend the link and
    `GET /api/auth/verify?token=…` to complete verification.
  - Frontend: `/verify-email/:token` handles verification success/failure and offers a resend flow.
    Once verified the user is redirected to `/welcome?email_verified=1`. Unverified accounts receive a
    403 on login with the message “Email not verified. Check your inbox or resend.”

- **reCAPTCHA**
  - Backend: set `RECAPTCHA_SECRET` (leave unset alongside `DISABLE_RECAPTCHA=1` in non-enforced
    environments).
  - Frontend: set `VITE_RECAPTCHA_SITE_KEY`. Without it the UI issues a development bypass token that
    only works while `DISABLE_RECAPTCHA=1` or the secret is unset.

- **Google OAuth**
  - Backend: configure `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`.
  - Frontend: configure `VITE_GOOGLE_CLIENT_ID`. The SPA redirects to `/auth/callback` after Google
    returns an authorization code.

- **LinkedIn OAuth**
  - Backend: configure `LINKEDIN_CLIENT_ID` and `LINKEDIN_CLIENT_SECRET`.
  - Frontend: configure `VITE_LINKEDIN_CLIENT_ID`.

Both social providers share the same callback route: `/auth/callback`. The frontend exchanges the returned
code with `POST /api/auth/login/{provider}` which issues internal tokens and sets the refresh cookie.

### OAuth quick start

1. **Local env vars** – update `.env` with
   - `GOOGLE_CLIENT_ID/SECRET`,
     `GOOGLE_CALLBACK_URL=http://localhost:8000/api/auth/oauth/google/callback`
   - `LINKEDIN_CLIENT_ID/SECRET`,
     `LINKEDIN_CALLBACK_URL=http://localhost:8000/api/auth/oauth/linkedin/callback`
   - `FRONTEND_ORIGIN=http://localhost:5173`, `SESSION_COOKIE_SECURE=0`,
     `SESSION_COOKIE_SAMESITE=lax`
   - Frontend: `VITE_GOOGLE_CLIENT_ID`, `VITE_LINKEDIN_CLIENT_ID`, optional `VITE_API_BASE` (omit to
     use the Vite proxy).

1. **Provider redirect URIs** – allow both local and staging:
   - Google: `http://localhost:8000/api/auth/oauth/google/callback`,
     `https://dev.cape-control.com/api/auth/oauth/google/callback`
   - LinkedIn: `http://localhost:8000/api/auth/oauth/linkedin/callback`,
     `https://dev.cape-control.com/api/auth/oauth/linkedin/callback`

1. **Smoke tests (expect 302 to the provider login page)**

   ```bash
   # Local (requires backend running on :8000)
   curl -I "http://localhost:8000/api/auth/oauth/google/start?next=/dashboard" -L | head -n 10
   curl -I "http://localhost:8000/api/auth/oauth/linkedin/start?next=/dashboard" -L | head -n 10

   # Staging
   curl -I "https://dev.cape-control.com/api/auth/oauth/google/start?next=/dashboard" -L | head -n 10
   curl -I "https://dev.cape-control.com/api/auth/oauth/linkedin/start?next=/dashboard" -L | head -n 10
   ```

   Each command returns a 307 from our API followed by a 302 from Google/LinkedIn. Abort before the final
   consent page if run manually.

### Smoke tests

```bash
# Health check
curl -sS https://dev.cape-control.com/api/health

# Trigger a verification redirect (replace <TOKEN>)
curl -I "https://dev.cape-control.com/api/auth/verify?token=<TOKEN>"

# Resend a verification email (requires CSRF token header in real usage)
curl -X POST https://dev.cape-control.com/api/auth/verify/resend \
  -H 'Content-Type: application/json' \
  -H 'X-CSRF-Token: <csrf-token>' \
  -d '{"email":"user@example.com"}'
```

## Agents Framework

- Create a local `.env.dev` (keep it out of version control) before running the agent make targets.
  - Include:
    - `GH_TOKEN=<github token with repo + workflow>`
    - `HEROKU_API_KEY=<Heroku API Key>`
    - `HEROKU_APP_NAME=autorisen`
- Agent specs live under `agents/<slug>/agent.yaml` with optional tests in `agents/<slug>/tests/`.
- Tool configuration templates live in `config/<env>/tools/` and are shared by the agents listed in
  `agents/registry.yaml`.
- Helpful targets:
  - `make agents-new name=<slug>` scaffolds a starter agent folder.
  - `make agents-validate` runs `scripts/agents_validate.py` to enforce registry schema.
  - `make agents-test` runs targeted pytest coverage (`tests/test_agents_tooling.py`).
- Run `make agents-run name=<slug> task="..."` to exercise adapters (set `AGENTS_ENV` or `--env` for
  config swaps).
- GitHub Actions checks `.github/workflows/agents-validate.yml` on PRs touching specs, tool configs, or
  helper scripts.

## ChatKit Integration (scaffold)

- Backend exposes `/api/chatkit/token` to mint short-lived client tokens (see
  `backend/src/modules/chatkit`).
- Configure ChatKit issuance with `CHATKIT_APP_ID`, `CHATKIT_SIGNING_KEY`, and optional settings for
  `CHATKIT_AUDIENCE`, `CHATKIT_ISSUER`, and `CHATKIT_TOKEN_TTL_SECONDS`.
- `/api/chatkit/tools/{tool_name}` invokes onboarding/support/energy/money adapters and records events
  in `app_chat_events`.
- `/api/flows/run` executes orchestrated tool sequences (tie runs to an agent slug/version when needed).
- Flow runs persist in `flow_runs`, enabling the UI to surface history using the returned `run_id`.
- `/api/flows/onboarding/checklist` and `/api/flows/runs` feed the onboarding progress card in the SPA.
- `/api/agents` backs CRUD for the agent registry (agents and versions).
- Agent registry UI lets developers create agents, add versions, and publish the latest release.
- Manifest editor modal enables editing manifests, creating versions, and previewing validation output.
- SPA auth context manages login/register flows, token storage with auto refresh, and guarded onboarding
  and developer areas.
- `/api/marketplace/agents` serves the public directory (detail modal fetches
  `/api/marketplace/agents/{slug}`).
- Marketplace modal can invoke `/api/flows/run` with an agent slug to preview tool output.
- Chat thread and event tables originate from migration `c1e0cc70f7a4_add_chatkit_tables.py` and models in
  `backend/src/db/models.py`.
- Frontend wraps the app with `ChatKitProvider` and adds a Support modal launcher in the top navigation.
- Landing page highlights onboarding and developer workbench experiences that spin up ChatKit sessions via
  shared modals.
- Developer section surfaces the agent registry and creation form powered by `/api/agents`.
- Replace placeholder logic in `backend/src/modules/chatkit/service.py` and client chat components. Swap in
  the real ChatKit SDK when ready.
- Set `VITE_CHATKIT_WIDGET_URL` to the hosted ChatKit Web SDK script so the modal can mount the official
  widget.
