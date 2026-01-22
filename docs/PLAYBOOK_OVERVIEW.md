# PLAYBOOKS_OVERVIEW.md

## Single Point of Truth (SPoT)

- project-plan.csv is the sole Single Point of Truth for scope, work existence, status, sequencing, gates, authority, and deployment eligibility
- All other artifacts are derived from or constrained by the plan
- Other files may be authoritative within their domain but are not sources of truth
- If any artifact conflicts with project-plan.csv, the CSV always prevails
- Autonomous agents may reason freely but may only act within plan boundaries

| Playbook | Owner | Agents | Status | Progress | Last Updated | Key Milestone |
|-----------|--------|---------|----------|------------|----------------|
| MVP Launch | Product Lead | CodexOps, TestGuardianAgent | ✅ Done | 100% | 2025-10-21 | Staging pipeline complete |
| Heroku Deployment | DevOps Lead | ReleaseBot, DocAgent | 🔄 Doing | 80% | 2025-10-25 | Pipeline + Makefile live |
| Testing Suite | QA Lead | TestGuardianAgent | 🧩 Planned | 0% | – | Initial pytest config stable |
| AI Agents Integration | Backend Lead | AgentManager, SandboxAI | 🧠 Planned | 10% | – | Define /agents schema |
| Docs & Playbooks | DocAgent | Codex | ✅ Done | 100% | 2025-10-25 | Linked in Codex sidebar |
