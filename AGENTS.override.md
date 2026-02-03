# CapeControl — AGENTS.override (Temporary Guardrails)

This override applies higher-priority safety constraints when present.

## Mode
- Plan-first is mandatory.
- Prefer docs-only work unless Robert explicitly approves code changes.

## Strict Safety Gate
- autorisen-only (staging/sandbox)
- NO capecraft production deploy/release unless Robert explicitly instructs it.

## Must Ask Before Any Action Involving
- Deploy/release, pipelines, infra
- DB migrations/schema
- Auth/CSRF/security policy
- Payments (PayFast/Stripe)
