# Documentation Playbook

- **Goal:** Keep internal and external documentation accurate, discoverable, and actionable for every release.
- **Scope:** Product docs, API references, runbooks, playbooks, and diagrams.

## Cadence

- Weekly doc stand-up to triage requests and stale content.
- Release-day checklist to update change logs and customer notes.
- Quarterly information architecture review of the `/docs` tree.

## Checklist

- Align doc updates with engineering tickets before they merge.
- Reference canonical diagrams (Figma or draw.io) and store exports in `docs/figma/`.
- Run `npm run lint:markdown` (planned) before committing large doc batches.
- Verify links, code snippets, and commands against the current branch.
- Submit playbook updates via PR with reviewer from owning team.

## Tooling

- Markdown stored in repo with Prettier formatting.
- draw.io / Figma for diagrams, exported to svg/png when possible.
- Vale or markdownlint (planned) for consistency checks.
- GitHub issues to track doc debt.

## Owners

- **Primary:** Technical Writer.
- **Support:** Engineering managers, Product Marketing, Support lead.
