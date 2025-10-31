# Playbooks Overview

The playbooks catalog captures the cross-functional initiatives that keep Cape Control aligned. Use the snapshots below to understand the current focus and jump into the owning documents.

## Portfolio Snapshot

| Anchor | Focus | Status | Owner File |
| --- | --- | --- | --- |
| P1 | MVP launch deliverables and release readiness | Doing | `docs/playbooks/mvp_launch.md` |
| P2 | Auth reliability and onboarding hardening | Doing | `docs/playbooks/onboarding_playbook.md` |
| P3 | Agent marketplace and orchestration scaffolding | Todo | `docs/playbooks/agents_playbook.md` |

## Detailed Index

| Category | Description | Primary Owners | Path |
| --- | --- | --- | --- |
| UI/UX | Component standards, accessibility, and handoff checklists | Product Design | `docs/playbooks/ui_ux_playbook.md` |
| Onboarding | Invite-to-value flows, auth protections, activation metrics | Growth PM | `docs/playbooks/onboarding_playbook.md` |
| Agents | AI agent lifecycle, evaluation, and guardrails | AI Product Lead | `docs/playbooks/agents_playbook.md` |
| Documentation | Repo docs, diagrams, and release notes processes | Technical Writer | `docs/playbooks/docs_playbook.md` |
| DevOps | CI/CD, infrastructure reviews, and on-call hygiene | DevOps Lead | `docs/playbooks/devops_playbook.md` |
| Design (Figma) | Component-to-code alignment playbooks | Product Design | `docs/playbooks/design/` |

## Design Integration

- Store diagram exports and handoff assets under `docs/figma/`.
- Reference canonical frame links inside each playbook when they are available.
- When exporting updates, commit both the markdown changes and any refreshed assets to keep the design system in sync with engineering.

## Design Integration Layer

| Figma Board | Module | Status | Linked Playbook |
|---|---|---|---|
| [Auth Flow](https://www.figma.com/design/HK7SbPtB0uJxeCUDVcrbzM/CapeWire?node-id=1-56) | Auth & Onboarding | 🟡 In Sync | `docs/playbooks/design/01-auth-flow.md` |
| [Dashboard Layout](https://www.figma.com/design/HK7SbPtB0uJxeCUDVcrbzM/CapeWire?node-id=1-103) | Core Dashboard | 🔵 In Design | `docs/playbooks/design/02-dashboard-layout.md` |
| [Agent Hub](https://www.figma.com/design/HK7SbPtB0uJxeCUDVcrbzM/CapeWire?node-id=1-92) | Agents Marketplace | ⚪ Pending | `docs/playbooks/design/03-agent-hub.md` |
| [Profile & Settings](https://www.figma.com/design/HK7SbPtB0uJxeCUDVcrbzM/CapeWire?node-id=1-74) | Accounts | ⚪ Pending | `docs/playbooks/design/04-profile-settings.md` |
| [Home / Landing](https://www.figma.com/design/HK7SbPtB0uJxeCUDVcrbzM/CapeWire?node-id=1-31) | Marketing Shell | ⚪ Pending | `docs/playbooks/design/05-home-landing.md` |

> Source of truth for the design layer is the CapeWire board above. Each playbook tracks a component map, API touchpoints, acceptance criteria, and sync commands.
