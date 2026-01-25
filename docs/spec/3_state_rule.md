# 3-State Rule (Canonical)

## Purpose

Provide a single, enforceable rule for how every user-facing navigation item must behave so users can trust what will happen when they click.

## The Rule

Every navigation item (link, button, menu item, footer link, CTA) must resolve to exactly **one** of these three states:

1. **Works**
   - The user can click and reach a real page/route.
   - If auth is required, the user is guided through the correct auth path.

2. **Explains**
   - The user can click and is shown a clear, non-deceptive explanation of why the destination is not available.
   - The explanation must include the next best action (e.g., "Log in" / "Create free account") without forcing execution.

3. **Hidden**
   - The navigation item is not shown at all when it cannot be used or cannot be truthfully explained.

## Prohibitions

- No dead links.
- No silent failures.
- No ambiguous destinations.
- No links that "look available" but lead to an error state without explanation.

## Evidence / Verification

- Verify each nav item against these three states in staging (autorisen) during UX verification.
- Any violations must be registered as planned Work Orders in `docs/project-plan.csv` (no fixes during MVP freeze).
