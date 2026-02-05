# Diagrams
This folder uses a source/export convention.

## Structure
- `docs/diagrams/src/` — editable sources (e.g., MindMup `.mup`)
- `docs/diagrams/export/` — exported artifacts for viewing/review (e.g., `.pdf`)

## Naming rule
Exported files MUST share the same base name as their source.
Example:
- `src/auth-workflow.mup`
- `export/auth-workflow.pdf`

## Update rule
When a `.mup` changes, re-export the `.pdf` and commit both in the same PR/commit.
