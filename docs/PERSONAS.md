# Personas — CapeControl

Last updated: 2025-09-22

This document captures the primary user personas for the CapeControl MVP and the top jobs-to-be-done (JTBD) we'll prioritise.

## Personas

### 1) Startup SME

- Typical profile: small team (1-10 people), product or operations lead responsible for customer support and knowledge base.

- Goals:
  - Reduce response time to common customer queries.
  - Automate routine scheduling and follow-ups.
  - Surface insights from support interactions.

- Pain points:
  - Limited engineering bandwidth.
  - Lack of time to craft templated responses.
  - Fragmented tools and manual workflows.

- Top JTBD:
  1. "Help me triage and answer the top 10 customer questions."  
  2. "Schedule follow-ups and reminders automatically based on rules."  
  3. "Provide a short summary of recent customer interactions."

- Acceptance criteria:
  - Able to create a FAQ agent and see improved average response time by X% in trials.  
  - Scheduler can create and trigger reminders from a template.

### 2) Solo Creator / Consultant

- Typical profile: single operator or small freelance consultant using CapeControl to automate admin tasks and generate outputs for clients.

- Goals:
  - Save time on repetitive administrative tasks.
  - Produce higher-quality deliverables faster.
  - Maintain control over outputs and privacy of client data.

- Pain points:
  - No dedicated ops or engineering support.
  - Concerned about cost and complexity.

- Top JTBD:
  1. "Auto-generate a client deliverable (e.g., brief, FAQ) from a prompt and template."  
  2. "Set up lightweight scheduling for client meetings and reminders."  
  3. "Quickly get suggested templates for common tasks."

- Acceptance criteria:
  - A template run produces a deliverable with > 80% user-rated usefulness in trials.  
  - Templates can be instantiated and edited in <10 minutes.

## How to use these personas

- Use persona JTBDs to prioritise feature development and create sample starter prompts in `GET /api/examples`.
- Ensure onboarding flows include persona selection and pre-filled starter tasks.

## Next steps

- Add quantitative measures and sample users for each persona.
- Validate personas with at least 3 external interviews per persona.
