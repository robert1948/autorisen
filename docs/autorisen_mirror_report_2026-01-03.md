# autorisen staging mirror report (capecraft → autorisen)

Date: 2026-01-03

## Audit trail

- Commands + outputs (includes some potentially sensitive operational details): `/tmp/autorisen_mirror_audit/audit_2026-01-03.log`
- Config snapshots (contain secrets; do not commit/share):
  - `/tmp/capecraft.env`
  - `/tmp/autorisen.env`
  - `/tmp/autorisen.final.env`

## Pre-flight summary (read-only)

- capecraft web URL: https://capecraft-65eeb6ddf78b.herokuapp.com/
- autorisen web URL: https://autorisen-dac8e65796e7.herokuapp.com/

## Add-ons (autorisen before/after)

- capecraft: `heroku-postgresql:essential-0`
- autorisen: `heroku-postgresql:essential-0` (no missing add-on types detected)

## Domains

- capecraft custom domains:
  - `cape-control.com`
  - `www.cape-control.com`
- autorisen custom domains (pre-change):
  - `dev.cape-control.com`

Note: `dev.cape-control.com` is under the same parent domain as production, which can create cookie/session cross-talk if any cookies are scoped to `.cape-control.com`.

## Config vars (high-level)

- capecraft and autorisen already share most key names.
- Risky integration keys observed (examples): OAuth (Google/LinkedIn), payments (PayFast/Stripe), SMTP/email, webhooks, AWS storage credentials.

### autorisen overrides applied

- Set staging identity and origins:
  - `ENV=staging`, `APP_ENV=staging`
  - `PUBLIC_BASE_URL=https://autorisen-dac8e65796e7.herokuapp.com`
  - `APP_ORIGIN` and `FRONTEND_ORIGIN` aligned to autorisen URL
  - `ALLOWED_HOSTS` and `CORS_ORIGINS` constrained to autorisen URL + localhost
- Disabled email:
  - `EMAIL_ENABLED=0`
- Disabled reCAPTCHA for staging:
  - `DISABLE_RECAPTCHA=1`
- Disabled auto-migrations on boot:
  - `RUN_DB_MIGRATIONS_ON_STARTUP=0`
- Payments safety:
  - `PAYFAST_MODE=sandbox`
  - Unset PayFast merchant secrets and Stripe secrets on autorisen
- Rotated internal auth/email secrets on autorisen:
  - `SECRET_KEY`, `JWT_SECRET`, `EMAIL_TOKEN_SECRET` (values redacted)

## Database

Planned: schema-only (migrations) on autorisen without restoring production data.

## Workers / schedulers

Planned: scale non-web dynos to 0 (if present).

## Verification

Planned:
- `GET /api/health`
- `GET /api/version`
- `GET /api/auth/csrf` (if enabled)

