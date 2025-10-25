# 🛠️ Operations & Maintenance Playbook

**Purpose**  
Keep environments healthy (dev/staging/prod) with clear SLOs, rotation, and incident play.

---

## 1) Scope
- Monitoring, alerts, backups, rotations, incident response

## 2) Roles & Agents
| Role | Agent | Responsibilities |
|------|-------|------------------|
| Lead Strategist | AutoDeployer | Runbooks & rotations |
| QA/Validation | TestGuardian | Health checks & probes |
| Governance | ShieldAgent | Access & audit reviews |

## 3) Workflow
### Phase A — Baseline
1. Define SLOs/SLIs, dashboards, alerts.
2. Backup & restore drills.
### Phase B — Operate
1. Weekly rotation; patch windows.
2. Smoke tests on deploy.
### Phase C — Incident
1. Triage → comms → mitigation.
2. Post-mortem within 48h.

## 4) Validation Gates
| Gate | Criteria | Owner |
|------|----------|-------|
| SLO Gate | Error budget respected | AutoDeployer |
| Backup Gate | Quarterly restore proof | TestGuardian |

## 5) Metrics & KPIs
- Uptime
- MTTR / MTTA
- Backup success rate

## 6) Artifacts
- Runbooks in `/docs/runbooks/*`
- Pager/alert config links

## 7) Review & Improvement
- Monthly reliability review; action items tracked

## 8) Revision History
| Version | Date | Summary | Author |
|--------:|------|---------|--------|
| v1.0 | 2025-10-25 | Initial skeleton | Codex / GPT-5 |
