# Task Capsule

## ID

TC-AUTH-004

## Title

Add developer login endpoint using existing JWT system

## Goal

Implement a new `/api/auth/dev/login` endpoint using FastAPI and the existing JWT system so that authenticated developer accounts can log in separately from tenants.

---

## Strict Requirements

- Reuse `Developer` model from `backend/src/models.py`
- Create a Pydantic schema in `backend/src/schemas/developer.py`
- Add a FastAPI route in `backend/src/routes/auth_dev.py`
- Call the existing JWT token generation utilities
- Do NOT modify tenant auth flows or shared login routes
- Minimal diffs only
- No speculative changes
- Update status + notes in `docs/project-plan.csv` for row `AUTH-004`

---

## Acceptance Criteria

- `POST /api/auth/dev/login` returns a valid JWT when credentials are correct
- Invalid login returns `401` using existing error handling
- `make test` passes
- `make lint` passes
- App starts cleanly (`make up` or `make smoke-local`)
- `docs/project-plan.csv` row for `AUTH-004` updated with `status=completed`, `completion_date=<today>`, `notes=developer login route added`, and any relevant artifacts

---

## Source-Of-Truth References

- `docs/DEVELOPMENT_CONTEXT.md` (auth)
- `docs/MVP_SCOPE.md`
- `docs/Checklist_MVP.md`
- `docs/project-plan.csv` (task status registry)
- `tests/test_auth.py`

---

## Affected Areas (Expected)

- `backend/src/routes/auth_dev.py` (new)
- `backend/src/schemas/developer.py`
- `backend/src/models.py` (if needed)
- `docs/project-plan.csv`
- `docs/DEVELOPMENT_CONTEXT.md`

---

## Out Of Scope

- No tenant auth modifications
- No UI changes
- No Makefile changes
- No Docker changes

---

## Implementation Steps (Propose First)

1. Inspect existing auth utilities and JWT helpers
1. Add `DeveloperLoginRequest` schema in `schemas/developer.py`
1. Create `auth_dev.py` with login route
1. Register the route in the main FastAPI app
1. Update `project-plan.csv` row `AUTH-004`
1. Update relevant docs
1. Provide a unified git diff

---

## Output Format

1. Restate your understanding
1. Propose the implementation plan
1. Wait for approval
1. After approval: show the unified diff (including CSV changes)
