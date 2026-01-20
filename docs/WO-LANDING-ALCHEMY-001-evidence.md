# WO-LANDING-ALCHEMY-001 — Curiosity Cascade Landing Evidence

This page is a lightweight checklist for verifying the Curiosity Cascade implementation on the root landing page (`/`).

## Where to Verify

- Route: `/`
- Component: `client/src/pages/Landing.tsx`

## Failure Modes Guardrail (must be **absent**)

Confirm **none** of the following appear on the landing page:

- Full feature lists
- Dashboard screenshots
- “Everything we do” explanations
- Forced signup before relevance
- Urgency CTAs (e.g., “Act now”, “Don’t miss out”)

## Curiosity Cascade Stages (must be **present**)

### Stage 1 — Curiosity Trigger (Pattern Disruption)
- [ ] Opens with intrigue/questions, not explanations
- [ ] No technical language / no feature list
- [ ] User can feel interest without details

### Stage 2 — Interaction (Micro-Rewards)
- [ ] Click/hover micro-interactions reveal small clarity
- [ ] Rewards are insights, not full answers

### Stage 3 — Breadcrumb Trail (Progressive Disclosure)
- [ ] Breadcrumb nav exists and feels optional
- [ ] Each reveal suggests the next question
- [ ] No “dump” of information

### Stage 4 — Meaningful Reveal (Identity Framing)
- [ ] “This is for people who…” framing exists
- [ ] User can recognize themselves

### Stage 5 — Invitation (Permission-Based Commitment)
- [ ] CTAs feel safe/optional
- [ ] Exploration path exists without account creation

## Screenshot Capture (Before/After)

### Local sandbox (recommended)
1. In one terminal:
   - `cd client && npm run dev`
2. Open the app in your browser (usually `http://localhost:5173/`).
3. Take screenshots:
   - **Before**: capture the existing landing page prior to changes (if available in git history)
   - **After**: capture the updated Curiosity Cascade landing page

### Git-based “before” option
If you need a reproducible “before” screenshot:

1. Checkout previous commit (or stash current changes).
2. Run `npm run dev`.
3. Screenshot `/`.
4. Return to current branch state.
5. Screenshot `/` again.

## Notes

Intent map present: `docs/capcontrol-curiosity-cascade.mm`.

Cross-check the landing copy + breadcrumb labels against that map, while still enforcing the WO non-negotiables (no feature dump, no forced signup, no urgency CTAs).
