# ChatKit Session Lifecycle — CapeControl × Codex

**Last updated:** 2025-10-19

This note documents the agreed upon ChatKit/Codex session flow that both teams
will implement. It maps directly to the final sitemap
(`docs/sitemap_v2_final.mmd`) and the API surface exposed under
`https://cape-control.com/`.

## 1. Preconditions

| Requirement | Notes |
| --- | --- |
| Verified CapeControl account | `/auth/login` returns `email_verified: true`; unverified users are redirected to `/verify-email/:token`. |
| Authenticated browser session | Frontend stores `access_token` / refresh cookie per existing auth flow. |
| Codex feature guard | `/codex/*` routes are protected by the verified gate described in the sitemap. |

## 2. Endpoint Quick Reference

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/api/codex/sessions` | `POST` | Create a Codex session (agent, placement, metadata). |
| `/api/codex/sessions/:id` | `GET` | Fetch a specific session (for resume/debug). |
| `/api/codex/sessions/current` | `GET` | Retrieve the latest active session for the current user/context. |
| `/api/codex/chatkit/sessions` | `GET` | List ChatKit sessions (mirrors Codex session state for the SDK). |
| `/api/codex/chatkit/token` | `GET` | Mint ChatKit client token scoped to the Codex session. |

> ⚠️ All endpoints inherit the verified-user guard — responses return `403` if
> the email verification step has not been completed.

## 3. Session Flow Overview

### Step 1 — User enters `/codex/chatkit`

Frontend checks `AuthContext.state.isEmailVerified`. If false, show the “Verify
your email” banner. Otherwise continue.

### Step 2 — Create or resolve Codex session

```text
POST /api/codex/sessions
Content-Type: application/json
Authorization: Bearer <access_token>

{
  "placement": "developer-workbench",
  "agent_id": "agent_123",
  "context": { "from": "dashboard" }
}
```text
Response includes the new `session_id`, initial status, and optional metadata.

- If an active session already exists (same placement + agent), backend may
  return `409` with a pointer to `/current`.

### Step 3 — Fetch ChatKit token

```text
GET /api/codex/chatkit/token?session_id=<session_id>
Authorization: Bearer <access_token>
```text
Returns `{ "token": "<chatkit-jwt>", "expires_at": "..." }`. The frontend
hands this token to the ChatKit Web SDK.

### Step 4 — Synchronize sessions

- `GET /api/codex/chatkit/sessions` exposes ChatKit-side session IDs for analytics/audit.
- `GET /api/codex/sessions/:id` or `/current` is used to resume state on refresh.

### Step 5 — ChatKit runtime

The SDK uses the issued token to open the WebSocket and orchestrate messages.
Tool calls and transcripts are still persisted through existing ChatKit
adapters.

### Step 6 — Termination and cleanup (future)

When the user ends a run, the client can call
`POST /api/codex/sessions/:id/close` (todo) or rely on backend TTL.

### Sequence Diagram (conceptual)

```text
User → Frontend SPA → POST /api/codex/sessions → Backend → DB
User → Frontend SPA → GET  /api/codex/chatkit/token → Backend → ChatKit JWT
Frontend → ChatKit SDK (Browser) → connect using token
```text
## 4. Error Handling Guidelines

| Scenario | Expected behaviour |
| --- | --- |
| Session creation returns 403 | Surface “Verify your email” modal (use existing AuthGate component). |
| `/api/codex/chatkit/token` returns 404 | Session expired or missing; call `/api/codex/sessions/current` to recover, otherwise prompt to start a new session. |
| Token expired mid-chat | Catch 401 from ChatKit transport, refresh via `/api/codex/chatkit/token`, and re-connect. |
| Backend rate limits | Respect `Retry-After`; display toast "`Codex is busy, please retry in X seconds`". |

## 5. Frontend Integration Checklist

- [x] Guard `/codex/*` routes using `AuthGate` (already implemented).
- [ ] Add React Query hooks:
  - `useCreateCodexSession` → POST `/api/codex/sessions`
  - `useCurrentCodexSession` → GET `/api/codex/sessions/current`
  - `useChatKitToken` → GET `/api/codex/chatkit/token`
- [ ] Cache `session_id` in component state and refresh the token before expiry.
- [ ] Log lifecycle events to `/api/codex` (if analytics is required).

## 6. Backend TODOs (for completeness)

- Ensure `/api/codex/chatkit/token` validates that the requesting user owns the referenced session.
- Align ChatKit token claims with Codex session metadata (agent, placement, user ID).
- Emit structured logs (`codex.session.created`, `codex.chatkit.token.issued`) for observability.
- Optionally support `DELETE /api/codex/sessions/:id` for manual teardown.

## 7. References

- Final sitemap: `docs/sitemap_v2_final.mmd` (SVG export: `docs/sitemap_v2_final.svg`)
- Auth flow details: see `docs/USAGE_TEMPLATES.md` sections on login and verification.
- Current implementation notes are tracked under tasks `AUTH-060` / `AUTH-061` in `docs/autorisen_project_plan.csv`.

---

_Prepared by the Codex integration team. For questions, reach out on #autorisen-ops or contact the CapeControl project lead._
