# CapeControl MVP — Pages & Routes Checklist

Derived strictly from SYSTEM_SPEC §2.5.
This is a checklist only (no UI details, no code scaffolding).

## Checklist

Columns:
- Route path: canonical path from SYSTEM_SPEC §2.5
- Auth requirement: public | auth | onboarding | app | help
- Data dependency: none | read-only | write
- Component Path: repo file path for the route page component
- Status: planned (only)

| Route path | Auth requirement | Data dependency | Component Path | Status |
| --- | --- | --- | --- | --- |
| `/` | public | none | `client/src/pages/mvp/MvpPages.tsx` (MvpLanding) | planned |
| `/about` | public | none | `client/src/pages/mvp/MvpPages.tsx` (MvpAbout) | planned |
| `/docs` | public | none | `client/src/pages/mvp/MvpPages.tsx` (MvpDocs) | planned |
| `/login` | public | write | `client/src/pages/mvp/MvpPages.tsx` (MvpLogin) | planned |
| `/register` | public | write | `client/src/pages/mvp/MvpPages.tsx` (MvpRegister) | planned |
| `/reset-password` | public | write | `client/src/pages/mvp/MvpPages.tsx` (MvpResetPassword) | planned |
| `/reset-password/confirm` | public | write | `client/src/pages/mvp/MvpPages.tsx` (MvpResetPasswordConfirm) | planned |
| `/register/step-1` | public | write | `client/src/pages/mvp/MvpPages.tsx` (MvpRegisterStep1) | planned |
| `/register/step-2` | public | write | `client/src/pages/mvp/MvpPages.tsx` (MvpRegisterStep2) | planned |
| `/verify-email/:token` | public | write | `client/src/pages/mvp/MvpPages.tsx` (MvpVerifyEmail) | planned |
| `/logout` | auth | write | `client/src/pages/mvp/MvpPages.tsx` (MvpLogout) | planned |
| `/onboarding/welcome` | onboarding | write | `client/src/pages/mvp/MvpPages.tsx` (MvpOnboardingWelcome) | planned |
| `/onboarding/profile` | onboarding | write | `client/src/pages/mvp/MvpPages.tsx` (MvpOnboardingProfile) | planned |
| `/onboarding/checklist` | onboarding | write | `client/src/pages/mvp/MvpPages.tsx` (MvpOnboardingChecklist) | planned |
| `/onboarding/guide` | onboarding | read-only | `client/src/pages/mvp/MvpPages.tsx` (MvpOnboardingGuide) | planned |
| `/dashboard` | app | read-only | `client/src/pages/mvp/MvpPages.tsx` (MvpDashboard) | planned |
| `/settings` | app | read-only | `client/src/pages/mvp/MvpPages.tsx` (MvpSettings) | planned |
| `/settings/profile` | app | write | `client/src/pages/mvp/MvpPages.tsx` (MvpSettingsProfile) | planned |
| `/settings/security` | app | write | `client/src/pages/mvp/MvpPages.tsx` (MvpSettingsSecurity) | planned |
| `/settings/billing` | app | read-only | `client/src/pages/mvp/MvpPages.tsx` (MvpSettingsBilling) | planned |
| `/help` | help | read-only | `client/src/pages/mvp/MvpPages.tsx` (MvpHelp) | planned |
| `/help/knowledge-base` | help | read-only | `client/src/pages/mvp/MvpPages.tsx` (MvpKnowledgeBase) | planned |

## Notes (from SYSTEM_SPEC)
- Navigation is strictly linear: Public → Auth → Onboarding → App (SYSTEM_SPEC §2.5.7).
- Billing is display-only for MVP (SYSTEM_SPEC §2.5.4).
- Help is read-only (SYSTEM_SPEC §2.5.5).
- Registration step routes and email verification are unauthenticated entry points (SYSTEM_SPEC §2.5.2).
