# Agents Playbook

- **Goal:** Ship reliable AI agents with clear scopes, guardrails, and monitoring across environments.
- **Scope:** Agent design, prompt templates, evaluation harnesses, rollout strategy, and observability.

## Cadence

- Weekly agent performance review (latency, success rate, escalations).
- Monthly prompt audit for drift and hallucination patterns.
- Quarterly red-team exercises on high-risk agents.

## Checklist

- Document agent purpose, inputs, outputs, and fallback handling.
- Store prompts and tool manifests in version control (`docs/agents.md`).
- Provide sandbox test cases and acceptance criteria before release.
- Enable logging/metrics for success, failure, and human handoff events.
- Coordinate rollout plan with Support and Compliance.

## Tooling

- LLM provider dashboards (OpenAI, Anthropic, etc.).
- Internal evaluation scripts under `tools/`.
- Quick Verify script (docs/agents.md) to detect missing artifacts.
- PagerDuty or equivalent for incident response.

## Owners

- **Primary:** AI Product Lead.
- **Support:** Prompt engineering team, Observability engineer, Compliance partner.
