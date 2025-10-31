# Design Playbook 04 — Profile & Settings

**Owner:** Product Design
**Figma Link:** [CapeWire — Profile & Settings](https://www.figma.com/design/HK7SbPtB0uJxeCUDVcrbzM/CapeWire?node-id=1-74&mode=design)
**Status:** ⚪ Pending
**Purpose:** Track the upcoming profile management experience so the engineering plan lines up with the CapeWire mocks before work starts.

---

## 1) Flow Overview

- Logged-in user opens the Profile & Settings area from the dashboard header.
- Profile tab exposes contact details, organization info, and role-specific fields.
- Security tab covers password reset, MFA enrollment, and session management.
- API tab (stretch) surfaces personal API tokens and activity logs.

## 2) Component Map

| Figma Component | React Component | File Path | Status |
|---|---|---|---|
| Profile Overview Header | `<AuthContext />` consumer (future `<ProfileHeader />`) | `client/src/features/auth/AuthContext.tsx` | ⚪ Data available – UI pending |
| Account Details Form (planned) | `<ProfileSettingsForm />` (planned) | `client/src/pages/profile/ProfileSettings.tsx` | ⚪ Not implemented |
| Security Controls (planned) | `<SecuritySettingsPanel />` (planned) | `client/src/pages/profile/Security.tsx` | ⚪ Not implemented |
| API Token List (planned) | `<ApiTokenTable />` (planned) | `client/src/pages/profile/ApiTokens.tsx` | ⚪ Not implemented |
| Danger Zone (Deactivate) | Auth service helpers | `client/src/lib/authApi.ts` | ⚪ Requires endpoint support |

## 3) Routes & API Endpoints

- FE route (planned): `/profile` with sub-tabs for `/profile/security` and `/profile/api`.
- Existing API dependencies: `GET /api/auth/me`, `POST /api/auth/logout`, `POST /api/auth/password/reset`.
- Planned API work: `PATCH /api/auth/me`, `POST /api/auth/mfa/setup`, `DELETE /api/auth/tokens/{id}`.

## 4) Acceptance Criteria

- [ ] Profile form mirrors Figma layout with two-column responsive collapse at 768px.
- [ ] Security tab implements password reset and future MFA CTA per spec.
- [ ] API tokens tab (if in scope) shows token name, scope, last used, and revoke action.
- [ ] All destructive actions require confirmation modal matching the danger-zone frame.

## 5) Sync & Validation Commands

```bash
make design-sync FIGMA_BOARD=https://www.figma.com/design/HK7SbPtB0uJxeCUDVcrbzM/CapeWire?node-id=1-74
make design-validate PLAYBOOK=profile-settings
```

## 6) Decisions Log

- 2025-10-30: Defer UI build until auth service exposes PATCH `/api/auth/me` to avoid stubs.
- 2025-10-30: Reuse auth context for optimistic updates; fallback to full refetch after save.

## 7) Links

- Auth context + state: `client/src/features/auth/AuthContext.tsx`
- Auth service helpers: `client/src/lib/authApi.ts`
- Auth backend: `backend/src/modules/auth/`
- Proposed profile pages (create when starting work): `client/src/pages/profile/`
