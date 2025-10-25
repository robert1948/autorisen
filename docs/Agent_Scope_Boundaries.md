# Agent Scope Boundaries

These areas **require human ownership**. Agents may assist with suggestions, but must not make direct changes without explicit approval and scope labels.

## Strategic Product Decisions

- Feature selection, scope trims, roadmap trade-offs
- User research synthesis and prioritization

## Infrastructure & Security

- Architecture changes, network boundaries, data retention policies
- Mail/SMTP, ReCAPTCHA, OAuth/OIDC, secrets management
- Any IAM/permissions changes

## Production Data & User Experience

- Any action that could affect live tenants/customers
- Migration strategies and rollback plans

## Agent PR Requirements

- Explicit labels for sensitive scopes:
  - `codex:infra` (infra/security)
  - `codex:backend` / `codex:frontend`
- Link to this document in the PR body
- Clear rollback instructions if applicable
