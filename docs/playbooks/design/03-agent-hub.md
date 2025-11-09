# Design Playbook 03 — Agent Hub

**Owner:** Robert (Product Design)
**Figma Link:** [Agent Hub](https://www.figma.com/design/gRtWgiHmLTrIZGvkhF2aUC/Untitled?node-id=0-1&p=f&t=fqyTV6VUfkaTGa5a-0)
**Status:** 🔄 Migrating to new board
**Purpose:** Bridge the Agent Hub frames (registry + marketplace) with the current developer portal and ensure publishing flows stay aligned.

---

## 1) Flow Overview

- Authenticated developer opens the Agent Hub section inside the dashboard.
- Registry panel lists private agents with create/edit/publish affordances.
- Marketplace feed previews published agents with quick links to detail drawers.
- Support surface enables escalation into ChatKit for troubleshooting.

## 2) Component Map

| Figma Component | React Component | File Path | Status |
|---|---|---|---|
| Agent List & CRUD | `<AgentRegistryPanel />` | `client/src/features/dev/AgentRegistryPanel.tsx` | 🟡 Align spacing & buttons |
| Manifest Editor Drawer | `<AgentManifestEditor />` | `client/src/features/dev/AgentManifestEditor.tsx` | ⚪ Wire visual spec |
| Publish CTA | `<AgentRegistryPanel />` (publish button) | `client/src/features/dev/AgentRegistryPanel.tsx` | 🟡 Needs tooltip styling |
| Marketplace Preview Rail | `<MarketplaceShowcase />` | `client/src/features/marketplace/MarketplaceShowcase.tsx` | ⚪ Add card gradient treatment |
| Support Entry Point | `<ChatModal />` (developer placement) | `client/src/components/chat/ChatModal.tsx` | ⚪ Pending copy update |

## 3) Routes & API Endpoints

- FE route anchors: `/` → `#developers`, `#experiences` (AuthGate required).
- API dependencies: `GET /api/agents`, `POST /api/agents`, `POST /api/agents/{agent_id}/versions`, `POST /api/agents/{agent_id}/versions/{version_id}/publish`, `GET /api/marketplace/agents`.
- Supporting libs: `client/src/lib/api.ts` for registry mutations and marketplace reads.

## 4) Acceptance Criteria

- [ ] Registry list density matches Figma (single-line rows, 16px vertical rhythm).
- [ ] Manifest editor modal width and typography match the spec at 1280px and 1440px breakpoints.
- [ ] Publishing flow confirms state change with the designed success toast.
- [ ] Marketplace section gracefully degrades when zero published agents exist.

## 5) Sync & Validation Commands

```bash
make design-sync FIGMA_BOARD=https://www.figma.com/design/gRtWgiHmLTrIZGvkhF2aUC/Untitled?node-id=0-1
make design-validate PLAYBOOK=agent-hub
```text
## 6) Decisions Log

- 2025-10-30: Keep agent create/edit in a single panel to minimize focus management churn.
- 2025-10-30: Reuse marketplace showcase cards for the hub until dedicated grid ships.

## 7) Links

- Developer portal components: `client/src/features/dev/`
- Marketplace showcase: `client/src/features/marketplace/`
- Agents API: `backend/src/modules/agents/`
- Marketplace API: `backend/src/modules/marketplace/`
