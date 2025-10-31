# Design Playbook 01 — Auth Flow

**Owner:** Robert (UX + Eng)
**Figma Link:** [CapeWire — Auth Flow](https://www.figma.com/design/HK7SbPtB0uJxeCUDVcrbzM/CapeWire?node-id=1-56&mode=design)
**Status:** 🟡 In Sync
**Purpose:** Keep the authentication journey aligned between the CapeWire Figma board and the React + FastAPI implementation.

---

## 1) Flow Overview

Login → Register → Email Verification (optional) → Onboarding → Dashboard redirect

## 2) Component Map

| Figma Component | React Component | File Path | Status |
|---|---|---|---|
| Login & Register Surfaces | `<AuthForms />` | `client/src/features/auth/AuthForms.tsx` | 🟡 Needs microcopy alignment |
| Auth Gate | `<AuthGate />` | `client/src/features/auth/AuthGate.tsx` | ✅ Synced |
| Password Meter | `<PasswordMeter />` | `client/src/components/PasswordMeter.tsx` | ✅ Synced |
| reCAPTCHA Widget | `<Recaptcha />` | `client/src/components/Recaptcha.tsx` | ✅ Synced |
| Onboarding Stepper | `<Customer /> / <Developer />` | `client/src/pages/onboarding/` | ⏳ Review |

## 3) Routes & API Endpoints

- FE routes: `/login`, `/register`, `/verify-email`, `/forgot-password`, `/onboard`
- BE endpoints: `GET /api/auth/csrf`, `POST /api/auth/login`, `POST /api/auth/register`, `POST /api/auth/logout`, `GET /api/auth/me`, `POST /api/auth/resend-verification`

## 4) Acceptance Criteria

- [ ] CSRF token fetched before any mutating request
- [ ] Error states mirror Figma copy for invalid email, password, and reCAPTCHA failures
- [ ] Password meter thresholds and tooltips match the design spec
- [ ] Verified users land on the onboarding route before dashboard access when `is_first_session`

## 5) Sync & Validation Commands

```bash
make design-sync FIGMA_BOARD=https://www.figma.com/design/HK7SbPtB0uJxeCUDVcrbzM/CapeWire
make design-validate PLAYBOOK=auth-flow
```

## 6) Decisions Log

- 2025-10-30: Adopt CSRF fetch on boot via `GET /api/auth/csrf` and store in `AuthContext`.
- 2025-10-30: Consolidate login/register forms into `<AuthForms />` to share validation.

## 7) Links

- React auth module: `client/src/features/auth/`
- Shared auth components: `client/src/components/`
- FastAPI auth router: `backend/src/modules/auth/`
- CSRF helpers: `backend/src/modules/auth/csrf.py`
