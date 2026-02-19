# CapeControl MVP — Pages & Routes Checklist

Derived strictly from SYSTEM_SPEC §2.5.
Updated: 2026-02-19.
This is a checklist only (no UI details, no code scaffolding).

## Checklist

Columns:
- Route path: canonical path from SYSTEM_SPEC §2.5
- Auth requirement: public | guest-only | auth | onboarding | app | help
- Data dependency: none | read-only | write
- Component Path: repo file path for the route page component
- Status: implemented | scaffold | planned | redirect

### Public Pages

| Route path | Auth | Data | Component Path | Status |
| --- | --- | --- | --- | --- |
| `/` | public | none | `client/src/pages/Home.tsx` | implemented |
| `/about` | public | none | `client/src/pages/mvp/MvpPages.tsx` (MvpAbout) | scaffold |
| `/docs` | public | none | `client/src/pages/mvp/MvpPages.tsx` (MvpDocs) | scaffold |
| `/home` | public | none | `client/src/components/HomePage.tsx` | implemented |
| `/how-it-works` | public | none | `client/src/pages/About.tsx` | implemented |
| `/subscribe` | public | none | `client/src/pages/Subscribe.tsx` | implemented |
| `/developers` | public | none | `client/src/pages/DeveloperInfo.tsx` | implemented |
| `/customer-terms` | public | none | `client/src/pages/CustomerInfo.tsx` | implemented |
| `/terms-and-conditions` | public | none | `client/src/pages/TermsAndConditions.tsx` | implemented |
| `/developer-terms` | public | none | `client/src/pages/DeveloperTerms.tsx` | implemented |
| `/demo` | public | none | `client/src/pages/Welcome.tsx` | implemented |

### Auth Pages (guest-only via RequireMvpGuest)

| Route path | Auth | Data | Component Path | Status |
| --- | --- | --- | --- | --- |
| `/login` | guest-only | write | `client/src/pages/mvp/MvpPages.tsx` (MvpLogin) | scaffold |
| `/register` | guest-only | write | `client/src/pages/mvp/MvpPages.tsx` (MvpRegister) | scaffold |
| `/register/step-1` | guest-only | write | `client/src/pages/mvp/MvpPages.tsx` (MvpRegisterStep1) | scaffold |
| `/register/step-2` | guest-only | write | `client/src/pages/mvp/MvpPages.tsx` (MvpRegisterStep2) | scaffold |
| `/reset-password` | guest-only | write | `client/src/pages/mvp/MvpPages.tsx` (MvpResetPassword) | scaffold |
| `/reset-password/confirm` | guest-only | write | `client/src/pages/mvp/MvpPages.tsx` (MvpResetPasswordConfirm) | scaffold |
| `/verify-email/:token` | public | write | redirect → `/auth/verify-email/:token` | redirect |

### Auth Pages (canonical)

| Route path | Auth | Data | Component Path | Status |
| --- | --- | --- | --- | --- |
| `/auth/login` | public | write | `client/src/pages/auth/LoginPage.tsx` | implemented |
| `/auth/register` | public | write | `client/src/pages/auth/Register.tsx` | implemented |
| `/auth/forgot-password` | public | write | `client/src/pages/auth/ForgotPassword.tsx` | implemented |
| `/auth/reset-password` | public | write | `client/src/pages/auth/ResetPassword.tsx` | implemented |
| `/auth/callback` | public | write | `client/src/pages/auth/SocialCallbackPage.tsx` | implemented |
| `/auth/verify-email/:token` | public | write | `client/src/pages/auth/VerifyEmail.tsx` | implemented |
| `/auth/mfa` | public | write | `client/src/pages/auth/MFAChallenge.tsx` | implemented |
| `/account/mfa-enroll` | auth | write | `client/src/pages/auth/MFAEnroll.tsx` | implemented |

### Onboarding (RequireAuth)

| Route path | Auth | Data | Component Path | Status |
| --- | --- | --- | --- | --- |
| `/onboarding/welcome` | auth | write | `client/src/pages/onboarding/Welcome.tsx` | implemented |
| `/onboarding/profile` | auth | write | `client/src/pages/onboarding/Profile.tsx` | implemented |
| `/onboarding/checklist` | auth | write | `client/src/pages/onboarding/Checklist.tsx` | implemented |
| `/onboarding/trust` | auth | write | `client/src/pages/onboarding/Trust.tsx` | implemented |

### App Pages (RequireAuth + RequireOnboarding)

| Route path | Auth | Data | Component Path | Status |
| --- | --- | --- | --- | --- |
| `/app` | app | — | `AppEntryRedirect` → `/app/dashboard` | redirect |
| `/app/dashboard` | app | read-only | `client/src/pages/app/DashboardPage.tsx` | implemented |
| `/app/projects/new` | app | write | `client/src/pages/app/CreateProjectPage.tsx` | implemented |
| `/app/projects/:projectId` | app | read-only | `client/src/pages/app/ProjectDetailPage.tsx` | implemented |
| `/app/settings` | app | read-only | `client/src/pages/app/Settings.tsx` | implemented |
| `/app/agents` | app | read-only | `client/src/pages/app/Agents.tsx` (feature-flagged) | implemented |
| `/app/developer` | app | read-only | `client/src/pages/app/Developer.tsx` (feature-flagged) | implemented |
| `/app/chat` | app | write | `client/src/pages/app/ChatConsole.tsx` (feature-flagged) | implemented |
| `/app/chat/:threadId` | app | write | `client/src/pages/app/ChatConsole.tsx` (feature-flagged) | implemented |
| `/app/billing` | app | read-only | `client/src/pages/app/Billing.tsx` (feature-flagged) | implemented |
| `/app/checkout` | app | write | `client/src/pages/app/Checkout.tsx` (feature-flagged) | implemented |
| `/app/checkout/success` | app | read-only | `client/src/pages/app/CheckoutSuccess.tsx` (feature-flagged) | implemented |
| `/app/checkout/cancel` | app | read-only | `client/src/pages/app/CheckoutCancel.tsx` (feature-flagged) | implemented |
| `/app/marketplace` | app | read-only | `client/src/pages/app/Marketplace.tsx` | implemented |
| `/app/sunbird-pilot` | app | read-only | `client/src/pages/app/SunbirdPilotMobile.tsx` (feature-flagged) | implemented |

### App Onboarding (RequireAuth + RequireOnboarding + feature flag)

| Route path | Auth | Data | Component Path | Status |
| --- | --- | --- | --- | --- |
| `/app/onboarding` | app | read-only | `client/src/pages/onboarding/OnboardingGuidePage.tsx` | implemented |
| `/app/onboarding/checklist` | app | write | `client/src/pages/onboarding/OnboardingChecklistPage.tsx` | implemented |
| `/app/onboarding/profile` | app | write | `client/src/pages/onboarding/OnboardingProfilePage.tsx` | implemented |
| `/app/onboarding/customer` | app | write | `client/src/pages/onboarding/OnboardingCustomerPage.tsx` | implemented |
| `/app/onboarding/developer` | app | write | `client/src/pages/onboarding/OnboardingDeveloperPage.tsx` | implemented |

### MVP App Pages (RequireMvpAuth)

| Route path | Auth | Data | Component Path | Status |
| --- | --- | --- | --- | --- |
| `/dashboard` | app | — | redirect → `/app/dashboard` | redirect |
| `/settings` | app | read-only | `client/src/pages/mvp/MvpPages.tsx` (MvpSettings) | scaffold |
| `/settings/profile` | app | write | `client/src/pages/mvp/MvpPages.tsx` (MvpSettingsProfile) | scaffold |
| `/settings/security` | app | write | `client/src/pages/mvp/MvpPages.tsx` (MvpSettingsSecurity) | scaffold |
| `/settings/billing` | app | read-only | `client/src/pages/mvp/MvpPages.tsx` (MvpSettingsBilling) | scaffold |
| `/logout` | app | write | `client/src/pages/mvp/MvpPages.tsx` (MvpLogout) | scaffold |

### Help Pages (public)

| Route path | Auth | Data | Component Path | Status |
| --- | --- | --- | --- | --- |
| `/help` | public | read-only | `client/src/pages/mvp/MvpPages.tsx` (MvpHelp) | scaffold |
| `/help/knowledge-base` | public | read-only | `client/src/pages/mvp/MvpPages.tsx` (MvpKnowledgeBase) | scaffold |

### Legacy Redirects

| Route path | Redirects to |
| --- | --- |
| `/signup` | `/auth/register` |
| `/forgot-password` | `/auth/forgot-password` |
| `/agents` | `/app/agents` |
| `/developer` | `/app/developer` |
| `/billing` | `/app/billing` |
| `/checkout` | `/app/checkout` |
| `/chat` | `/app/chat` |
| `/chat/:threadId` | `/app/chat/:threadId` |
| `/marketplace` | `/app/marketplace` |
| `/welcome` | `/demo` |
| `/onboarding/guide` | `/onboarding/welcome` |
| `/onboarding/customer` | `/app/onboarding/customer` |
| `/onboarding/developer` | `/app/onboarding/developer` |
| `/landing-legacy` | `HomePage` (direct render) |

## Route Summary

| Category | Total | Implemented | Scaffold | Redirect |
|---|---|---|---|---|
| Public | 11 | 10 | 1 | 0 |
| Auth (guest-only MVP) | 7 | 0 | 6 | 1 |
| Auth (canonical) | 8 | 8 | 0 | 0 |
| Onboarding | 4 | 4 | 0 | 0 |
| App | 15 | 15 | 0 | 0 |
| App Onboarding | 5 | 5 | 0 | 0 |
| MVP App | 6 | 0 | 5 | 1 |
| Help | 2 | 0 | 2 | 0 |
| Legacy Redirects | 14 | — | — | 14 |
| **Total** | **72** | **42** | **14** | **16** |

## Notes (from SYSTEM_SPEC)
- Navigation is strictly linear: Public → Auth → Onboarding → App (SYSTEM_SPEC §2.5.7).
- Registration prompts must follow the interest-triggered policy (SYSTEM_SPEC §2.5.3).
- Billing is display-only for MVP (SYSTEM_SPEC §2.5.4).
- Help is read-only (SYSTEM_SPEC §2.5.5).
- Registration step routes and email verification are unauthenticated entry points (SYSTEM_SPEC §2.5.2).
- `/logout` is an action route (not a full page) per SYSTEM_SPEC §2.5.2.
- Two parallel onboarding flows exist: MVP (`/onboarding/*`) and canonical (`/app/onboarding/*`).
  Consolidation recommended when feature flags are removed.
- OAuth callback (`/auth/callback`) handles both Google and LinkedIn social login returns.
- SPA fallback blocks `.php`, `.asp`, `.cgi`, `.env`, and other non-SPA extensions with 404.
