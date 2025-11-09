# Design Playbook 02 — Dashboard Layout

**Owner:** Robert (UX + Eng)
**Figma Link:** [Dashboard Layout](https://www.figma.com/design/gRtWgiHmLTrIZGvkhF2aUC/Untitled?node-id=0-1&p=f&t=fqyTV6VUfkaTGa5a-0)
**Status:** � Migrating to new board
**Purpose:** Translate the authenticated CapeControl dashboard frames into the live React shell while keeping telemetry and marketplace surfaces aligned.

---

## 1) Flow Overview

- Authenticated customer lands inside the dashboard shell gated by `<AuthGate />`.
- Hero summary shows platform health, version, and environment metadata.
- Experience cards surface onboarding progress, workbench access, and historical activity.
- Developer portal and marketplace sections expand below the fold.

## 2) Component Map

| Figma Component | React Component | File Path | Status |
|---|---|---|---|
| Dashboard Shell Layout | `<Home />` (authed sections) | `client/src/pages/Home.tsx` | 🔵 Needs layout parity |
| Global Navigation Bar | `<TopNav />` | `client/src/components/nav/TopNav.tsx` | ✅ Synced |
| Health Status Badge | `<Home />` (hero status block) | `client/src/pages/Home.tsx` | 🟡 Hook up real uptime copy |
| Experience Card — Onboarding Chat | `<OnboardingChat />` | `client/src/features/chat/OnboardingChat.tsx` | ✅ Synced |
| Experience Card — Agent Workbench | `<AgentWorkbench />` | `client/src/features/dev/AgentWorkbench.tsx` | ✅ Synced |
| Experience Card — Onboarding History | `<OnboardingHistory />` | `client/src/features/chat/OnboardingHistory.tsx` | 🟡 Needs timeline polish |
| Developer Registry Panel | `<AgentRegistryPanel />` | `client/src/features/dev/AgentRegistryPanel.tsx` | 🟡 Update empty state visuals |
| Marketplace Preview Rail | `<MarketplaceShowcase />` | `client/src/features/marketplace/MarketplaceShowcase.tsx` | 🟡 Expand data slots |
| Support Chat Modal | `<ChatModal />` | `client/src/components/chat/ChatModal.tsx` | 🔵 Align modal chrome |

## 3) Routes & API Endpoints

- FE routes: `/` (AuthGate-protected sections) → planned `/dashboard` alias once routing splits.
- API dependencies: `GET /api/health`, `GET /api/agents`, `POST /api/agents`, `GET /api/marketplace/agents`, `GET /api/flows/runs`.
- State: dashboard data hydrated through `client/src/lib/api.ts` helpers.

## 4) Acceptance Criteria

- [ ] Dashboard hero mirrors Figma spacing, typography, and badge state.
- [ ] Grid cards collapse to single column under 1024px as per responsive spec.
- [ ] Agent registry empty and loading states match design copy and iconography.
- [ ] Marketplace rail surfaces at least three published agents or shows the designed fallback.

## 5) Sync & Validation Commands

```bash
make design-sync FIGMA_BOARD=https://www.figma.com/design/gRtWgiHmLTrIZGvkhF2aUC/Untitled?node-id=0-1
make design-validate PLAYBOOK=dashboard-layout
```text
## 6) Decisions Log

- 2025-10-30: Keep dashboard under `<Home />` until dedicated route lands to avoid breaking deep links.
- 2025-10-30: Use shared `ChatModal` for support CTA to reuse accessibility affordances.

## 7) Links

- Dashboard shell (temporary): `client/src/pages/Home.tsx`
- Chat surfaces: `client/src/components/chat/`
- Developer tooling: `client/src/features/dev/`
- Marketplace API: `backend/src/modules/marketplace/`
- Flows telemetry: `backend/src/modules/flows/`
