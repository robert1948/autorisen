# Landing Messaging Change Log (2026-03-17)

## Purpose
This document records the homepage and public-page copy updates that reposition CapeControl from generic workflow AI language to a governed, trust-first agentic platform narrative.

## Strategic Shift
- From: workflow automation + broad AI value language
- To: governed agentic operations for compliance-heavy, trust-sensitive teams

Core framing now emphasized across public pages:
- Agents that act
- Evidence you can verify
- Control where it matters
- Approved-source retrieval
- Human-in-control checkpoints
- Escalation and accountability

## Files Updated
- `client/src/pages/Home.tsx`
- `client/src/components/HomePage.tsx`
- `client/src/components/Footer.tsx`
- `client/src/pages/public/WelcomePage.tsx`
- `client/src/pages/public/AboutPage.tsx`
- `client/src/pages/public/SubscribePage.tsx`
- `client/src/pages/public/DeveloperInfoPage.tsx`
- `client/src/pages/public/CustomerInfoPage.tsx`

## Section-Level Mapping

### 1) Hero (live and legacy landing)
- Old: "Reframe Your AI Journey... Effortless Magic"
- New: "Governed AI Agents for High-Trust Business Operations"

- Old CTA set: dashboard/support-oriented language
- New CTA set:
  - Primary: `See How It Works`
  - Secondary: `Start Guided Onboarding`

### 2) Value/Positioning section
- Old: alchemy/magic framing
- New: trust-by-design framing with explicit governance language

### 3) Agentic capability section
- Old feature headings included emotional framing (for example: "Tame AI Anxiety")
- New standardized headings:
  - `Agents That Act`
  - `Evidence You Can Verify`
  - `Control Where It Matters`

### 4) Core business function section
- Old: reverse-benchmark and novelty framing
- New: operational framing tied to real business execution
  - Operations Support
  - Compliance Workflows
  - Reporting and Documentation

### 5) Trust/governance section
- Old: exploration/magic metaphors
- New: explicit trust controls, source boundaries, approvals, and reviewability

### 6) Secondary CTA and final CTA
- Old: brand-magic / discovery-chat style messaging
- New: governance and accountability messaging, aligned with trust-sensitive buyers

## Public Route Consistency Pass

### `WelcomePage`
- Replaced "Go to Dashboard" with `See How It Works`
- Normalized onboarding CTA label to `Start Guided Onboarding`
- Tightened intro copy to emphasize controlled onboarding

### `AboutPage`
- Rewrote high-level narrative to trust-first agentic positioning
- Updated feature cards to governance/evidence/accountability language
- Updated CTA pair to:
  - `See How It Works`
  - `Start Guided Onboarding`

### `SubscribePage`
- Free-tier CTA text updated from `Get Started Free` to `Start Guided Onboarding`

### `DeveloperInfoPage` and `CustomerInfoPage`
- Updated top framing copy for message parity
- Preserved legal and contractual content
- Normalized customer registration CTA URL to canonical route: `/auth/register`

## Footer Alignment
- Shared footer description updated to governed-agentic positioning with approved-source and human-checkpoint language.

## Validation
- Frontend build command run after each pass:
  - `npm run build` (from `client/`)
- Result: successful build after all changes
- Existing non-blocking warning unchanged:
  - `ChatKitProvider.tsx` is both dynamically and statically imported

## Notes for Marketing/Product
- This is a messaging-layer change only; no product behavior was modified.
- Legal terms pages were not rewritten; only non-binding intro framing was adjusted where applicable.
- Recommended next step: A/B test hero + CTA pair on `/` with existing analytics hooks.
