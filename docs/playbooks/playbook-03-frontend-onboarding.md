# Playbook 03: Frontend Onboarding & Dashboard

**Owner**: Onboarding Maestro
**Supporting Agents**: UX Guide, Release Captain
**Status**: Planned
**Priority**: P1

---

## 1) Outcome

Deliver an intuitive, responsive frontend experience that connects authentication to onboarding and introduces the dashboard shell. This includes login, registration, guided onboarding, and the base dashboard structure integrated with the FastAPI backend.

**Definition of Done (DoD):**

* Login and registration flows functional and visually complete.
* Onboarding sequence (profile setup, guided steps, checklist) persists user progress to backend.
* Dashboard shell loads authenticated data from `/api/me`.
* Layout adapts for mobile and desktop; responsive nav (hamburger on mobile).
* UI polished to MVP standards (Tailwind + consistent design system).

---

## 2) Scope (In / Out)

**In Scope:**

* React components for Auth and Onboarding.
* API integration for login, registration, and `/me` endpoints.
* Dashboard base structure (sidebar, header, content region).
* State persistence (localStorage/sessionStorage).
* Responsive layout + accessibility pass.

**Out of Scope:**

* Full analytics integration.
* Multi-tenant dashboards or role-specific UIs.
* Post-onboarding AI guide flows.

---

## 3) Dependencies

**Upstream:**

* Playbook 02 – Backend Auth & Security (JWT + `/me` endpoint).
* Playbook 04 – DevOps CI/CD (build + deploy pipeline).

**Downstream:**

* Playbook 01 – MVP Launch (requires completed onboarding flow).
* Playbook 05 – Quality & Test Readiness (frontend smoke + snapshot tests).

---

## 4) Milestones

| Milestone | Description                                       | Owner              | Status        |
| --------- | ------------------------------------------------- | ------------------ | ------------- |
| M1        | Login + Register pages wired to backend           | Onboarding Maestro | ⏳ In Progress |
| M2        | Onboarding flow UI (steps, checklist) implemented | UX Guide           | 🔄 Pending    |
| M3        | Data persistence + API sync (backend integration) | Release Captain    | 🔄 Pending    |
| M4        | Dashboard shell structure complete                | Onboarding Maestro | 🔄 Pending    |
| M5        | Full smoke test on staging                        | Release Captain    | 🔄 Pending    |

---

## 5) Checklist (Executable)

* [x] Setup `client/src/components/auth/` structure.
* [x] Integrate API endpoints for `/login`, `/register`, `/me`.
* [ ] Implement onboarding checklist with persistent user progress.
* [ ] Add dashboard shell (sidebar + topbar layout).
* [ ] Verify mobile responsiveness and accessibility.
* [ ] Smoke test via staging build (`npm run build && npm run preview`).

---

## 6) Runbook / Commands

```bash
# Local dev server
npm run dev

# Build and preview staging
npm run build && npm run preview

# Lint and test
npm run lint && npm test
```

---

## 7) Risks & Mitigations

| Risk                                                | Mitigation                                               |
| --------------------------------------------------- | -------------------------------------------------------- |
| API mismatch between frontend and backend endpoints | Use `.env` variables and Swagger docs as contract source |
| Inconsistent onboarding progress saves              | Add retry + local caching fallback                       |
| Unhandled auth errors (token expiry)                | Centralize token refresh logic in Axios interceptor      |
| Layout breakage on mobile                           | Use Tailwind breakpoints + responsive design review      |

---

## 8) Links

* [`docs/PLAYBOOKS_OVERVIEW.md`](../PLAYBOOKS_OVERVIEW.md)
* [`client/src/components/auth/`](../../client/src/components/auth/)
* [`client/src/pages/onboarding/`](../../client/src/pages/onboarding/)
* [`client/src/pages/dashboard/`](../../client/src/pages/dashboard/)

---

## ✅ Next Actions

1. Complete login + register integration (M1).
2. Implement onboarding flow UI with backend persistence (M2–M3).
3. Build dashboard shell and run staging smoke (M4–M5).
4. Link runbook results back to Playbook #1 – MVP Launch for signoff.
