# Autorisen – Development Log

Chronological record of notable changes, fixes, decisions. Keep entries short and link PRs where possible.

Use the structured template in `docs/UPDATE_ENTRY_TEMPLATE.md` for substantial changes; for tiny ones use the quick inline format.

Format options:

- Quick: `YYYY-MM-DD – [type] short summary (PR #) – impact: api|db|perf|none`
- Full: Fill sections 1–15 in the template and paste a summarized first line here with a link.

## 2025-08-19

- Initialized documentation pack for planning & progress tracking.
- Aligned structure with Localstorm/CapeControl docs for consistency.

## 2025-08-18

- Heroku release v70 (autorisen). Investigated buildpack/runtime parity issues.
- Action item: lock Python runtime and requirements from production.

## Conventions

- Format: `YYYY-MM-DD – short action – link (optional)`
- Tag with **[infra] [api] [ui] [db] [docs]** as needed.

Commit message convention: `<type>: <scope>: <short summary>` (see template file for types).
