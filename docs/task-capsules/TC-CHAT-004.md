# Task Capsule

## ID

TC-CHAT-004

## Title

ChatKit frontend components (launcher, modal, telemetry, token refresh)

## Goal

Implement the ChatKit frontend components for CapeControl so that users can open a Chat launcher, interact through a modal chat UI, see connection / telemetry state, and benefit from automatic token refresh. This should integrate cleanly with the existing ChatKit backend endpoints delivered in `CHAT-001`.

---

## Strict Requirements

- Implement a Chat launcher entry point in `client/src/components/chat/`.
- Implement a modal or panel-based chat UI in `client/src/components/chat/`.
- Show connection / telemetry state (e.g. connecting, connected, error) using WebSocket status.
- Integrate with existing ChatKit token endpoints, including auto-refresh logic.
- Apply styling updates only where needed in `client/src/index.css`.
- Preserve existing routes and layouts; do not break current pages.
- Maintain TypeScript correctness across all updated files.
- Produce minimal diffs and avoid speculative refactors.
- Update status and metadata for `CHAT-004` in `docs/project-plan.csv` after completion.

---

## Acceptance Criteria

- A visible Chat launcher is available from the main UI (exact placement can be refined later but must be reachable).
- Clicking the launcher opens a chat modal or panel with:
  - message history display,
  - input area,
  - send action.
- WebSocket / ChatKit integration:
  - Successfully sends messages to the existing ChatKit backend,
  - Receives and renders responses.
- Token handling:
  - Uses existing token endpoints,
  - Automatically refreshes tokens before expiry without forcing a full page reload.
- Telemetry / status:
  - Some visible indicator of connection state (e.g. dot / label) is present in the launcher or header of the modal.
- `npm run type-check` passes.
- `npm run build` succeeds.
- `make lint` (or the equivalent frontend lint command) passes.
- `docs/project-plan.csv` row for `CHAT-004` updated to reflect the new status, completion date, and notes.

---

## Source-of-Truth References

- `docs/DEVELOPMENT_CONTEXT.md` (ChatKit / frontend sections).
- `docs/MVP_SCOPE.md`.
- `docs/Checklist_MVP.md`.
- `docs/project-plan.csv` row `CHAT-004`.
- Existing ChatKit backend modules and API contracts.
- Existing React layout and routing in `client/src/`.

---

## Affected Areas (Expected)

- `client/src/components/chat/*` (new or updated components).
- `client/src/index.css` (styling updates).
- `client/src/lib/` or similar utility directories (token or API helpers, if needed).
- `docs/project-plan.csv` (update `CHAT-004` row).
- Potentially `client/src/pages/*` or layout shell for launcher placement.

---

## Out of Scope

- No changes to backend ChatKit endpoints (those were delivered in `CHAT-001` and related tasks).
- No changes to payments, onboarding, or unrelated pages.
- No changes to Docker, Makefile, or deployment configuration.
- No major layout redesign outside what is necessary to host the Chat launcher and modal.
- No introduction of new frontend dependencies without explicit approval.

---

## Implementation Steps (Propose First)

1. Review existing ChatKit backend endpoints and any existing frontend scaffolding in `client/src/components/chat/`.
1. Design the component structure for:
   - Chat launcher,
   - Chat modal or panel,
   - Telemetry / status indicator,
   - Token / API interaction helpers.
1. Implement or update components under `client/src/components/chat/` and wire them into the existing layout.
1. Add or update token handling and WebSocket / HTTP integration, including automatic token refresh, using existing utilities where possible.
1. Apply minimal styling changes in `client/src/index.css` to support the launcher and modal.
1. Run `npm run type-check`, `npm run build`, and the relevant lint command, and fix any issues.
1. Update `docs/project-plan.csv` row `CHAT-004` with new `status`, `completion_date`, `notes`, and any relevant artifacts or verification commands.
1. Provide a unified git diff for review.

---

## Output Format

1. Restate your understanding of this Task Capsule.
1. Propose a concrete implementation plan referencing the affected files.
1. Wait for approval.
1. After approval, apply the changes and provide the unified diff, including the `docs/project-plan.csv` update.
