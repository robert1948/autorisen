# Agents Overview (CapeControl / AutoLocal / Autorisen)

Concise snapshot of agents in the codebase. Paths reflect the current structure.
If a filename differs in your repo, adjust the **Path** column (see the Quick Verify block).

---

## Core System Agents (Active)

| Category | Agent | Purpose | Status | Path |
|---|---|---|---|---|
| Core | **AuthAgent** | Registration, login, refresh, `/me`, role-based JWT | ✅ Active | `backend/src/modules/agents/auth_agent.py` |
| Core | **OnboardAgent** | Onboarding checklist + role/profile setup | ✅ Active | `backend/src/modules/agents/onboard_agent.py` |
| Core | **AuditAgent** | Request/audit event capture; cooperates with middleware | ✅ Active | `backend/src/modules/agents/audit_agent.py` |
| Core | **MonitoringAgent** | Health/metrics (`/api/health`, `/api/metrics`) | ✅ Active | `backend/src/modules/agents/monitoring_agent.py` |
| Core | **SecurityAgent** | Rate limiting, input checks, abuse controls | ✅ Active | `backend/src/modules/agents/security_agent.py` |
| Core | **Agents Router** | REST surface for agents | ✅ Active | `backend/src/modules/agents/router.py` |

---

## AI-Assisted Agents (MVP / In Progress)

| Category | Agent | Purpose | Status | Path |
|---|---|---|---|---|
| AI | **CapeAI Guide Agent** | Persistent in-app guide for onboarding/help (Claude 3.5 Haiku) | ✅ Active | `backend/src/modules/agents/cape_ai_guide/` |
| AI | **CapeAI Domain Specialist** | Domain-specific advice (workflows, analytics, security) | ✅ Active | `backend/src/modules/agents/cape_ai_domain_specialist/` |
| AI | **DevAgent** | Assists developers with build/test/publish of agents | 🔜 Planned (Phase 2) | `backend/src/modules/agents/dev_agent.py` |
| AI | **CustomerAgent** | Helps customers express goals → suggests workflows | 🧪 Stub | `backend/src/modules/agents/customer_agent.py` |
| AI | **ChatAgentKit Runtime** | Multi-step chat workflows (ChatKit/Codex layer) | 🔄 In progress | `backend/src/modules/agents/chatkit_runtime.py` |
| AI | **FinanceAgent** | Connects to Money schema & finance APIs | 📝 Concept | `backend/src/modules/agents/finance_agent.py` |
| AI | **EnergyAgent** | Tuya smart-meter → usage dashboard | 🧪 Prototype | `backend/src/modules/agents/energy_agent.py` |

**AI Provider:** Anthropic Claude 3.5 Haiku (claude-3-5-haiku-20241022)  
**Capabilities:** Basic completions, system prompts, temperature/token control  
**Available but not implemented:** Streaming, tool use, vision, conversation history  
**Test:** `python3 scripts/test_anthropic_api.py` (5/5 tests passing)

---

## Middleware-Bound (Support Agents)

| Category | Middleware / Delegate | Purpose | Status | Path |
|---|---|---|---|---|
| Support | **AuditLoggingMiddleware** → AuditAgent | Request/actor logging | ✅ Active | `backend/src/middleware/audit_logging.py` |
| Support | **MonitoringMiddleware** → MonitoringAgent | Uptime/metrics | ✅ Active | `backend/src/middleware/monitoring.py` |
| Support | **DDoSProtectionMiddleware** | Basic DDoS/rate protections | ✅ Active | `backend/src/middleware/ddos_protection.py` |
| Support | **InputSanitizationMiddleware** | Input cleansing/validation | ✅ Active | `backend/src/middleware/input_sanitization.py` |
| Support | **ContentModerationMiddleware** | Blocks disallowed content | ✅ Active | `backend/src/middleware/content_moderation.py` |

---

## Build/Docs Utility “Agents” (Repo Automation)

These aren’t FastAPI agents, but they automate quality gates and docs.

| Category | Agent/Tool | Purpose | Status | Path |
|---|---|---|---|---|
| Utility | **TestGuardianAgent** | Runs pytest and deterministically “heals” fixtures | ✅ Active (local/CI) | `scripts/regenerate_fixtures.py`, `pytest.ini` |
| Utility | **DocWeaver** | Keeps docs/playbooks/sitemaps tidy (format/check) | 🧪 Prototype | `tools/docweaver.py` *(or your chosen path)* |

> If your DocWeaver script lives elsewhere, update the path above.

---

### Quick Verify — copy/paste

Use these from the repo root to sanity-check files and surface any gaps.

```bash
set -euo pipefail

printf "\n▶ Listing agent files...\n"
ls -1 backend/src/modules/agents | sort || true

printf "\n▶ Flagging missing expected agent files...\n"
## Update this list if you rename files
EXPECT=(
  auth_agent.py onboard_agent.py audit_agent.py monitoring_agent.py security_agent.py router.py
  capeai_guide.py dev_agent.py customer_agent.py chatkit_runtime.py finance_agent.py energy_agent.py
  task_chain_agent.py billing_agent.py marketplace_agent.py auto_deploy_agent.py
)
for name in "${EXPECT[@]}"; do
  [[ -f "backend/src/modules/agents/$name" ]] || echo "⚠️ Missing: backend/src/modules/agents/$name"
done

printf "\n▶ Grepping for FastAPI routers and route decorators...\n"
rg -n "APIRouter|@router\(|@app\.get\(|@app\.post\(" backend/src/modules/agents || true

printf "\n▶ Listing middlewares...\n"
ls -1 backend/src/middleware | sort || true

printf "\n▶ Checking utility agents...\n"
[[ -f "scripts/regenerate_fixtures.py" ]] || echo "⚠️ Missing: scripts/regenerate_fixtures.py (TestGuardianAgent)"
[[ -f "tools/docweaver.py" ]] || echo "ℹ️ DocWeaver path differs — update docs/agents.md Path column"

printf "\n▶ (Optional) Dumping registered /api/agents routes if the app factory is importable...\n"
python3 - <<'PY'
try:
    from backend.src.app import create_app  # adjust if your factory has a different name
    app = create_app()
    for r in app.router.routes:
        path = getattr(r, 'path', '')
        methods = sorted(getattr(r, 'methods', []) or [])
        if path.startswith('/api/agents'):
            print(f"{path}  {methods}")
except Exception as e:
    print(f"(skip) Could not import app to introspect routes: {e}")
PY
