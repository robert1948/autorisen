# CapeControl MVP — Pages & Routes Checklist

Derived strictly from SYSTEM_SPEC §2.5.
This is a checklist only (no UI details, no code scaffolding).

## Checklist

Columns:
- Route path: canonical path from SYSTEM_SPEC §2.5
- Auth requirement: public | auth | onboarding | app | help
- Data dependency: none | read-only | write
- Status: planned (only)

| Route path | Auth requirement | Data dependency | Status |
| --- | --- | --- | --- |
| `/` | public | none | planned |
| `/about` | public | none | planned |
| `/docs` | public | none | planned |
| `/login` | public | write | planned |
| `/register` | public | write | planned |
| `/reset-password` | public | write | planned |
| `/reset-password/confirm` | public | write | planned |
| `/register/step-1` | auth | write | planned |
| `/register/step-2` | auth | write | planned |
| `/verify-email/:token` | auth | write | planned |
| `/logout` | auth | write | planned |
| `/onboarding/welcome` | onboarding | write | planned |
| `/onboarding/profile` | onboarding | write | planned |
| `/onboarding/checklist` | onboarding | write | planned |
| `/onboarding/guide` | onboarding | read-only | planned |
| `/dashboard` | app | read-only | planned |
| `/settings` | app | read-only | planned |
| `/settings/profile` | app | write | planned |
| `/settings/security` | app | write | planned |
| `/settings/billing` | app | read-only | planned |
| `/help` | help | read-only | planned |
| `/help/knowledge-base` | help | read-only | planned |

## Notes (from SYSTEM_SPEC)
- Navigation is strictly linear: Public → Auth → Onboarding → App (SYSTEM_SPEC §2.5.7).
- Billing is display-only for MVP (SYSTEM_SPEC §2.5.4).
- Help is read-only (SYSTEM_SPEC §2.5.5).
