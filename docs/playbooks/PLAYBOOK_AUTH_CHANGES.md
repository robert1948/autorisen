# PLAYBOOK — Auth & CSRF Changes (MVP)

## Purpose

Define governance guardrails for any changes to authentication and CSRF behavior.
This playbook exists to keep the session and CSRF model stable for MVP.

**Auth & CSRF are FROZEN** (FREEZE_REVIEW.md, §3). All changes to these
surfaces must follow this playbook without exception.

## Spec References

| Reference | Scope |
|---|---|
| SYSTEM_SPEC §3.1 | Auth flows: login, refresh, logout, me, csrf |
| SYSTEM_SPEC §3.2 | CSRF policy (double-submit pattern) |
| SYSTEM_SPEC §3.3 | Session guarantees and non-guarantees |
| SYSTEM_SPEC §3.4 | Frozen vs flexible areas |
| SYSTEM_SPEC §8 | Change control authority |
| SECURITY_CSRF.md | Canonical CSRF implementation detail |
| FREEZE_REVIEW.md | Management freeze status for §3 |

## Scope — What Counts as an Auth/CSRF Change

This playbook applies to any modification that touches:

1. **Auth endpoints** — `/api/auth/login`, `/api/auth/refresh`, `/api/auth/logout`,
   `/api/auth/me`, `/api/auth/csrf`, or any new `/api/auth/*` route.
2. **CSRF middleware** — Token issuance, validation, cookie/header names, exemption list.
3. **Session/token lifecycle** — JWT signing, access/refresh token TTL, token rotation,
   cookie attributes (`HttpOnly`, `Secure`, `SameSite`, `Path`, `Domain`).
4. **Auth dependencies** — `get_current_user`, role checks, token version checks,
   any function imported from `backend/src/modules/auth/deps.py`.
5. **Security middleware** — Rate limiting on auth routes, lockout logic, DDoS
   protections that gate auth endpoints.

Changes that do **not** trigger this playbook:
- Pure documentation corrections (typos, formatting) with no behavioral claims.
- Test-only changes that do not modify production auth code.
- Frontend auth UI changes that do not alter API contracts or token handling.

## Preconditions (ALL must be true before starting)

- [ ] The proposed change is **required** to satisfy SYSTEM_SPEC scope (not a nice-to-have).
- [ ] SYSTEM_SPEC §3.1 and §3.2 are current and used as the baseline for the change.
- [ ] SECURITY_CSRF.md is current and consistent with §3.2.
- [ ] The change has been assessed for security impact (cookie exposure, token leakage,
      replay attacks, CSRF bypass).
- [ ] Any cookie or header name changes are explicitly documented in the PR description.
- [ ] The change does NOT introduce a new auth flow not already defined in §3.1.

## Allowed Actions

| Action | Constraint |
|---|---|
| Fix a bug in existing auth flow | Must not alter the API contract (request/response shape, status codes) |
| Update SYSTEM_SPEC §3 language | Must reflect actual authoritative behavior, not aspirational |
| Update SECURITY_CSRF.md | Must stay consistent with SYSTEM_SPEC §3.2 |
| Adjust cookie attributes | Must not weaken security posture (e.g., removing `HttpOnly` from refresh cookie) |
| Add/adjust auth tests | Only in a separately approved engineering work order |
| Add a CSRF exemption | Only for server-to-server webhook endpoints; must be documented in §3.2 |

## Explicit Stop Conditions

**Stop immediately and escalate** if any of these are true:

1. The change would **weaken** CSRF or session protections (e.g., removing double-submit
   validation, shortening token TTL without justification, making refresh cookie non-HttpOnly).
2. The change would **introduce a new auth flow** not covered by SYSTEM_SPEC §3.1
   (e.g., API key auth, magic links, SSO federation beyond existing OAuth).
3. The change would **alter the CSRF exemption list** beyond documented webhook endpoints.
4. The change **requires payment execution work** (NEXT-003 remains blocked per §4.4).
5. The change would **modify token signing** (algorithm, key material) without a dedicated
   security review work order.
6. **Change control requirements** (SYSTEM_SPEC §8) are not met.

## Procedure

### Step 1 — Classify the change

Determine whether the change is:
- **Behavioral** (modifies auth/CSRF runtime behavior) → full playbook applies.
- **Documentation-only** (updates spec language to match existing behavior) → skip to Step 4.

### Step 2 — Security impact checklist

Before writing code, answer each question in the PR description:

- [ ] Does this change alter any cookie attributes? If yes, list old → new values.
- [ ] Does this change add, remove, or rename any auth endpoint? If yes, document the contract.
- [ ] Does this change modify token TTL, rotation, or signing? If yes, justify.
- [ ] Does this change add or remove a CSRF exemption? If yes, justify the server-to-server case.
- [ ] Could this change enable token replay, session fixation, or CSRF bypass? Explain.
- [ ] Does the change affect CORS headers related to auth? If yes, list changes.

If any answer raises concern → **STOP** and create a dedicated security review work order.

### Step 3 — Implementation constraints

- Branch from `main` using Work Order naming (`wo/<id>`).
- Auth code changes and test changes MUST be in **separate commits**.
- Run the existing auth test suite and confirm green before pushing:
  ```bash
  ./.venv/bin/python -m pytest tests/test_auth.py tests/test_auth_canonical.py -q
  ```
- Verify CSRF flow manually or via curl:
  ```bash
  # 1. Fetch CSRF token
  csrf=$(curl -s -c cookies.txt http://localhost:8000/api/auth/csrf \
    | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])')
  # 2. Attempt a protected endpoint
  curl -s -b cookies.txt -H "X-CSRF-Token: $csrf" \
    -X POST http://localhost:8000/api/auth/logout
  ```

### Step 4 — Documentation update

- Update SYSTEM_SPEC §3.1/§3.2 if behavior changed.
- Update SECURITY_CSRF.md if CSRF mechanism changed.
- Ensure PR description references this playbook and the originating work order.

### Step 5 — Review and merge

- PR requires review before merge.
- Reviewer must confirm:
  - [ ] Security impact checklist is complete (Step 2).
  - [ ] No stop conditions are triggered.
  - [ ] Auth tests pass.
  - [ ] Spec documents are consistent with the change.
- After merge, verify on staging:
  ```bash
  curl -s https://dev.cape-control.com/api/auth/csrf | python3 -c \
    'import json,sys; d=json.load(sys.stdin); assert "token" in d; print("CSRF OK")'
  ```

## Rollback

If a merged auth change causes issues on staging:

1. Revert the merge commit on `main`.
2. Push and redeploy (`make deploy-heroku`).
3. Verify auth flows are restored via health check and manual CSRF test.
4. Open a post-mortem work order referencing the reverted PR.

## Audit Trail

Every auth/CSRF change must produce:
- A PR with the security impact checklist filled out.
- Evidence of passing auth tests (CI or local log).
- Updated spec documents if behavior changed.
- Entry in `docs/project-plan.csv` linking to the work order and artifacts.
