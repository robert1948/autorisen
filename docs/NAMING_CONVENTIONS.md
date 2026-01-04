# Naming Conventions (Single Source of Truth)

## A. Purpose

This document is **authoritative** for naming conventions across the CapeControl platform.

It synchronizes naming across **Figma**, **React (frontend)**, **Backend API**, and **PostgreSQL** so that the same concepts are discoverable, consistent, and traceable from design → implementation → data.

## B. Canonical Naming Principle

- Canonical concept names use **PascalCase** (e.g., `OnboardingChecklist`, `SunbirdWaterUsage`).
- All other naming formats are **derived** from the canonical name.
- The canonical name is the **single source of truth**; do not invent new names in downstream layers.

**Worked example (end-to-end)**

- Canonical Concept: `OnboardingChecklist`
- Figma Frame: `Onboarding/Checklist/OnboardingChecklistPage — Default [READY]`
- React Page: `OnboardingChecklistPage`
- Route: `/onboarding-checklist`
- API (resource plural, grouped by domain): `/api/onboarding/checklists`
- DB Table (schema + plural snake_case): `cc.onboarding_checklists`

## C. Figma Naming Conventions

**Pages** (exact names)

- `00_Cover`
- `01_Foundations`
- `02_Components`
- `03_Patterns`
- `04_Pages`
- `05_Flows`
- `06_Marketing`
- `99_Archive`

**Frames format**

`<Domain>/<Area>/<Concept>Page — <Variant> [<Status>]`

Examples:
- `Auth/Entry/LoginPage — Mobile [IN PROGRESS]`
- `Sunbird/Water/SunbirdWaterUsagePage — Desktop [READY]`

**Allowed status values**

- `[TODO]`
- `[IN PROGRESS]`
- `[READY]`
- `[LOCKED]`
- `[DEPRECATED]`

**Components**

- Components use **PascalCase** names.
- Component names **must match React component names exactly** (case-sensitive).

**Tokens**

- Tokens use **lowercase dot-notation**.
- Examples: `color.brand.primary`, `space.16`, `radius.8`.

## D. Frontend (React) Naming

**Pages**

- PascalCase.
- Must end with `Page`.
- Examples: `LoginPage`, `RegisterPage`, `SunbirdWaterUsagePage`.

**Components**

- PascalCase.
- No suffixes like `Component` or `Widget`.
- Examples: `TopNav`, `PricingTier`, `OnboardingChecklist`.

**Routes**

- `kebab-case`, derived from the Page name with the `Page` suffix removed.
- Examples:
  - `LoginPage` → `/login`
  - `RegisterPage` → `/register`
  - `SunbirdWaterUsagePage` → `/sunbird-water-usage`

## E. Backend API Naming

- All endpoints are prefixed with `/api`.
- Use **plural nouns** for resources.
- Use **domain-based grouping**.

Examples:
- `/api/auth/sessions`
- `/api/onboarding/checklists`
- `/api/sunbird/water/readings`
- `/api/sunbird/electricity/readings`

## F. Database Naming (PostgreSQL)

**Schemas**

- `cc`
- `sunbird_water`
- `sunbird_electricity`

**Tables**

- `snake_case`, plural.
- Include schema prefix where relevant (e.g., `cc.users`).

**Columns**

- `snake_case`.
- Foreign keys use `<table_singular>_id`.
- Timestamps:
  - `created_at`
  - `updated_at`
  - optional `deleted_at`

**Primary keys**

- UUID, column name `id`.

**Constraints and indexes**

- Primary key: `pk_<table>`
- Unique: `uq_<table>__<columns>`
- Foreign key: `fk_<table>__<column>__<reftable>`
- Index: `ix_<table>__<columns>`

## G. MVP Naming Matrix

| Figma Frame | React Page | Route | API Endpoint | DB Tables |
|---|---|---|---|---|
| `Auth/Entry/LoginPage — Mobile [READY]` | `LoginPage` | `/login` | `/api/auth/sessions` | `cc.users`, `cc.sessions` |
| `Auth/Entry/RegisterPage — Mobile [READY]` | `RegisterPage` | `/register` | `/api/auth/registrations` | `cc.users`, `cc.registrations` |
| `Onboarding/Flow/OnboardingPage — Default [READY]` | `OnboardingPage` | `/onboarding` | `/api/onboarding/checklists` | `cc.onboarding_checklists`, `cc.onboarding_steps` |
| `Core/App/DashboardPage — Default [READY]` | `DashboardPage` | `/dashboard` | `/api/dashboard/widgets` | `cc.dashboard_widgets` |
| `Billing/Plans/BillingPage — Default [READY]` | `BillingPage` | `/billing` | `/api/billing/invoices` | `cc.billing_accounts`, `cc.invoices` |
| `Sunbird/Water/SunbirdWaterUsagePage — Default [READY]` | `SunbirdWaterUsagePage` | `/sunbird-water-usage` | `/api/sunbird/water/readings` | `sunbird_water.readings` |
| `Sunbird/Electricity/SunbirdElectricityUsagePage — Default [READY]` | `SunbirdElectricityUsagePage` | `/sunbird-electricity-usage` | `/api/sunbird/electricity/readings` | `sunbird_electricity.readings` |

## H. Enforcement Rules

- All new pages, endpoints, tables, and Figma frames **must comply** with this document.
- Deviations require **explicit justification in PRs**.
- This document **must be updated before** introducing new naming patterns.
