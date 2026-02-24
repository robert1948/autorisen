# Agents & Modules Registry (CapeControl)

> **Last verified:** 2026-02-24
> **Source of truth:** This document reflects the actual codebase structure.

---

## AI Agent Sub-Packages (Active)

All AI agents live under `backend/src/modules/agents/` as sub-packages with
`router.py`, `service.py`, `schemas.py`, and optional `knowledge_base.py` / `prompts.py`.

| Agent | Purpose | Provider | Path |
|---|---|---|---|
| **CapeAI Guide** | In-app assistant for onboarding/help | Claude 3.5 Haiku | `backend/src/modules/agents/cape_ai_guide/` |
| **CapeAI Domain Specialist** | Domain-specific advice (workflows, analytics, security) | Claude 3.5 Haiku | `backend/src/modules/agents/cape_ai_domain_specialist/` |
| **Customer Agent** | Help customers express goals, suggest workflows & plans | Claude 3.5 Haiku | `backend/src/modules/agents/customer_agent/` |
| **Dev Agent** | Assist developers with build/test/publish of agents | Claude 3.5 Haiku | `backend/src/modules/agents/dev_agent/` |
| **Finance Agent** | AI-powered financial analysis, budgeting, compliance | Claude 3.5 Haiku | `backend/src/modules/agents/finance_agent/` |
| **Content Agent** | Multi-channel content generation (blog, social, email) | Claude 3.5 Haiku | `backend/src/modules/agents/content_agent/` |

**Shared infrastructure:**

| File | Purpose |
|---|---|
| `backend/src/modules/agents/router.py` | REST surface for agent CRUD + marketplace + WebSocket |
| `backend/src/modules/agents/executor.py` | Agent dispatch engine (slug-based task execution) |
| `backend/src/modules/agents/schemas.py` | Pydantic models for agent registry |
| `backend/src/modules/agents/tool_use.py` | Tool-use utilities |

---

## Domain Modules (Non-Agent)

Business logic organized as FastAPI modules. Each has a `router.py` imported
by the app factory via `_safe_import()`.

| Module | Purpose | Path |
|---|---|---|
| **Auth** | Registration, login, JWT, OAuth (Google/LinkedIn), CSRF, RBAC | `backend/src/modules/auth/` |
| **Onboarding** | Onboarding checklist & role/profile setup | `backend/src/modules/onboarding/` |
| **ChatKit** | Multi-step chat workflows, tool registry | `backend/src/modules/chatkit/` |
| **RAG** | Controlled document retrieval, evidence trace, query pipeline | `backend/src/modules/rag/` |
| **Capsules** | Template-driven workflow runs (SOP, audit, clause, compliance) | `backend/src/modules/capsules/` |
| **Flows** | Workflow / automation flow definitions | `backend/src/modules/flows/` |
| **Marketplace** | Agent/workflow marketplace listings | `backend/src/modules/marketplace/` |
| **Payments** | PayFast integration, invoices, subscriptions | `backend/src/modules/payments/` |
| **Subscriptions** | Plan management, subscribe/cancel | `backend/src/modules/subscriptions/` |
| **User** | User profile management | `backend/src/modules/user/` |
| **Account** | Account settings, preferences | `backend/src/modules/account/` |
| **Ops** | Operational endpoints | `backend/src/modules/ops/` |
| **Support** | Support ticket management | `backend/src/modules/support/` |
| **Dev Dashboard** | Developer portal (API keys, usage stats) | `backend/src/modules/dev/` |
| **AI Router** | AI provider routing/abstraction | `backend/src/modules/ai_router/` |
| **Health** | Monitoring & health check router | `backend/src/modules/health/` |

---

## Middleware Stack

Middleware follows the pure ASGI pattern (`__init__(app)` + `__call__(scope, receive, send)`).

| Middleware | Purpose | Location |
|---|---|---|
| **CSRFMiddleware** | CSRF token validation on state-changing requests | `backend/src/modules/auth/csrf.py` |
| **CacheHeadersMiddleware** | Cache-Control headers for static assets | `backend/src/middleware/cache_headers.py` |
| **ReadOnlyModeMiddleware** | Block writes when `READ_ONLY_MODE=1` | `backend/src/middleware/read_only.py` |
| **MonitoringMiddleware** | Request metrics (latency, status codes, error rates) | `backend/src/middleware/monitoring.py` |
| **DDoSProtectionMiddleware** | IP-based rate/abuse blocking (optional) | `app/middleware/ddos_protection.py` |
| **InputSanitizationMiddleware** | Request body injection scanning (optional) | `app/utils/input_sanitization.py` |

---

## Build / Utility Scripts

| Tool | Purpose | Path |
|---|---|---|
| **TestGuardian** | `pytest` fixture regeneration | `scripts/regenerate_fixtures.py` |
| **Plan Sync** | Syncs `project-plan.csv` to `Master_ProjectPlan.md` | `scripts/plan_sync.py` |
| **Build Docs Index** | Documentation indexing | `tools/build_docs_index.py` |
| **Sitemap Crawler** | Crawl and validate sitemaps | `tools/crawl_sitemap.py` |
| **Route Lister** | Extract routes from source code | `tools/list_routes_from_source.py` |
| **Dashboard Updater** | Update control dashboard data | `tools/update_dashboard.py` |

---

### Quick Verify

```bash
set -euo pipefail

printf "\n>>> Agent sub-packages...\n"
ls -1d backend/src/modules/agents/*/  2>/dev/null | sort || true

printf "\n>>> Agent shared files...\n"
ls -1 backend/src/modules/agents/*.py 2>/dev/null | sort || true

printf "\n>>> Domain modules...\n"
ls -1d backend/src/modules/*/  2>/dev/null | sort || true

printf "\n>>> Middleware...\n"
ls -1 backend/src/middleware/*.py app/middleware/*.py 2>/dev/null | sort || true

printf "\n>>> Utility scripts...\n"
ls -1 scripts/*.py tools/*.py 2>/dev/null | sort || true
```
