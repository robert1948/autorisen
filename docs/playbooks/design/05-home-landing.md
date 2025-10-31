# Design Playbook 05 — Home / Landing

**Owner:** Marketing Design
**Figma Link:** [CapeWire — Home / Landing](https://www.figma.com/design/HK7SbPtB0uJxeCUDVcrbzM/CapeWire?node-id=1-31&mode=design)
**Status:** ⚪ Pending
**Purpose:** Keep the public marketing shell aligned with the CapeWire landing frames while sharing components with the in-app experience.

---

## 1) Flow Overview

- Visitor lands on `/` and sees hero, product highlights, and pricing.
- CTA buttons trigger guided chat or deep-link into registration.
- Scroll progression reveals showcase, pricing tiers, FAQ, and legal copy.
- Authenticated visitors stay on the same page but unlock gated sections via `<AuthGate />`.

## 2) Component Map

| Figma Component | React Component | File Path | Status |
|---|---|---|---|
| Hero Section | `<Home />` hero block | `client/src/pages/Home.tsx` | 🟡 Tighten spacing + typography |
| Top Navigation | `<TopNav />` | `client/src/components/nav/TopNav.tsx` | ✅ Synced |
| Primary CTA Buttons | `<Home />` hero actions | `client/src/pages/Home.tsx` | 🟡 Align copy with Figma |
| Product Highlight Cards | `<Home />` highlights grid | `client/src/pages/Home.tsx` | 🟡 Needs icon parity |
| Chat Launch Modal | `<ChatModal />` | `client/src/components/chat/ChatModal.tsx` | ✅ Synced |
| Onboarding Chat Entry | `<OnboardingChat />` | `client/src/features/chat/OnboardingChat.tsx` | ✅ Synced |
| Pricing Section | `<Home />` pricing tiers | `client/src/pages/Home.tsx` | 🔵 Refresh badges per design |
| FAQ Accordion | `<Home />` FAQ grid | `client/src/pages/Home.tsx` | 🔵 Convert to accordion |
| Footer & Legal Copy | `<Home />` footer | `client/src/pages/Home.tsx` | 🟡 Update copy blocks |

## 3) Routes & API Endpoints

- FE route: `/` with anchor targets (`#home`, `#features`, `#pricing`, `#faq`, `#about`).
- API dependencies: `GET /api/health` for status badge, `GET /api/marketplace/agents` for showcase, `GET /api/flows/onboarding/checklist` (when authenticated).
- Marketing assets stored under `client/src/assets/` and `docs/figma/` (exports).

## 4) Acceptance Criteria

- [ ] Hero typography, button spacing, and badge styles match the Figma frame at 1440px.
- [ ] Pricing cards render exactly as spec’d, including highlighted tier treatment.
- [ ] FAQ converts to accessible accordion behavior while preserving copy.
- [ ] Footer legal copy synced with latest marketing-approved language.

## 5) Sync & Validation Commands

```bash
make design-sync FIGMA_BOARD=https://www.figma.com/design/HK7SbPtB0uJxeCUDVcrbzM/CapeWire?node-id=1-31
make design-validate PLAYBOOK=home-landing
```

## 6) Decisions Log

- 2025-10-30: Reuse in-app components for chat CTAs to avoid diverging behavior.
- 2025-10-30: Keep `/` as single page; marketing vs app state handled inside `<Home />`.

## 7) Links

- Landing page implementation: `client/src/pages/Home.tsx`
- Shared navigation: `client/src/components/nav/TopNav.tsx`
- Chat surfaces: `client/src/components/chat/`
- Marketplace showcase data: `backend/src/modules/marketplace/`
- Marketing assets: `client/src/assets/`, `docs/figma/`
