# AI Provider Compliance & Data-Handling Policy

> **Last updated:** 2025-07-03 — CapeControl v0.2.5+

## 1. Providers in Use

| Provider   | Models Used                                                  | Endpoint                      |
| ---------- | ------------------------------------------------------------ | ----------------------------- |
| Anthropic  | claude-3-5-haiku-20241022 (primary), claude-sonnet-4-20250514, claude-3-opus-20240229 | `api.anthropic.com/v1/messages` |
| OpenAI     | gpt-4o-mini (fallback), gpt-4o, gpt-4-turbo, gpt-3.5-turbo | `api.openai.com/v1/chat/completions` |

## 2. Data-Handling Guarantees

### 2.1 Anthropic

- **Training opt-out:** API inputs/outputs are **not** used to train models. Anthropic's [Commercial Terms](https://www.anthropic.com/policies/commercial-terms) guarantee this for API customers.
- **Data retention:** Anthropic may retain API inputs for up to 30 days for trust & safety monitoring, after which they are deleted. Customers can request zero-retention via a Data Processing Addendum (DPA).
- **DPA available:** Yes — contact Anthropic sales or execute via their self-serve portal.
- **SOC 2 Type II:** Completed.
- **Sub-processors:** Listed at <https://www.anthropic.com/policies/subprocessors>.

### 2.2 OpenAI

- **Training opt-out:** API data is **not** used for training by default (since March 2023). Confirmed in [OpenAI API Data Usage Policy](https://openai.com/enterprise-privacy).
- **Data retention:** API inputs may be retained for up to 30 days for abuse monitoring. Zero-retention available for eligible customers.
- **DPA available:** Yes — available via OpenAI's trust portal at <https://trust.openai.com>.
- **SOC 2 Type II:** Completed.
- **Sub-processors:** Listed at <https://openai.com/policies/subprocessors>.

## 3. POPIA / GDPR Compliance

CapeControl operates under South African POPIA regulations. Our provider usage is compliant because:

| Requirement                          | How We Comply                                                                 |
| ------------------------------------ | ----------------------------------------------------------------------------- |
| Lawful processing purpose            | AI assistance explicitly consented to during onboarding                        |
| Data minimisation                    | Input guard caps user prompts at 8 000 characters; sliding window limits context to ~6 000 tokens |
| Cross-border transfer safeguards     | Both providers maintain DPAs with Standard Contractual Clauses (SCCs)         |
| No model training on user data       | Both providers guarantee API data is excluded from training                    |
| Right to erasure                     | Platform deletes threads/messages via user action; provider 30-day auto-purge  |
| Security measures                    | TLS 1.2+ in transit; providers hold SOC 2 Type II certifications              |

## 4. CapeControl Platform Safeguards

| Safeguard                    | Implementation                                              |
| ---------------------------- | ----------------------------------------------------------- |
| Input length guard           | `validate_llm_input()` — 8 000 char max, truncation mode   |
| Token budget (chat)          | Sliding window: 6 000 tokens max context per request        |
| Response caching             | In-memory LLM cache (TTL 300 s, max 512 entries)           |
| Cost tracking                | Every LLM call logged to `usage_log` with model, tokens, cost |
| Per-agent cost visibility    | Admin endpoint `/api/usage/admin/costs` includes `by_agent` breakdown |
| Rate limiting                | Redis-backed per-user rate limits                           |
| Spending circuit breaker     | Platform-wide monthly budget cap via `check_platform_budget()` |
| Temperature governance       | Fixed temperatures per agent (0.2–0.7) to control output variance |
| Model tiering                | Haiku ($0.25/$1.25) for routine tasks; Sonnet/Opus only on explicit upgrade |

## 5. Audit Trail

All LLM interactions are recorded in the `usage_log` table with:

- `user_id` — who made the request
- `event_type` — which agent/service (`chat`, `agent:rag`, `capsule`, `agent:finance`, etc.)
- `model` — exact model ID used
- `tokens_in` / `tokens_out` — token counts
- `cost_usd` — computed cost
- `created_at` — timestamp

Admin cost reports are accessible at `/api/usage/admin/costs` and include both per-user and per-agent breakdowns.

## 6. Review Schedule

This document must be reviewed:

- **Quarterly** — or whenever a new AI provider/model is added
- **Immediately** — if provider terms of service change
- **On audit request** — by any CapeControl board member or compliance officer

---

*Maintained by the CapeControl engineering team.*
