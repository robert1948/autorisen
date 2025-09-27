# Master Project Plan (generated snapshot) — autorisen

Snapshot: 2025-09-27

- Total tasks: 74
- Status counts: todo: 64, busy: 7, done: 3

## Top priority (P1) tasks — quick view

| Task ID | Title | Owner | Estimate | Depends On |
|---|---|---:|---:|---:|
| AUTH-001 | Design auth data model | backend | 6 |  |
| AUTH-002 | Implement /auth/register + hashing | backend | 8 | AUTH-001 |
| AUTH-003 | Implement /auth/login + JWT | backend | 8 | AUTH-002 |
| AUTH-004 | /auth/me and refresh flow | backend | 6 | AUTH-003 |
| AUTH-005 | Security hardening & tests | backend | 6 | AUTH-003 |
| ORG-006 | Org model + memberships | backend | 8 | AUTH-001 |
| ORG-007 | /orgs CRUD + /orgs/{id}/members | backend | 8 | ORG-006,AUTH-004 |
| AIGW-009 | Provider adapter interface | backend | 6 |  |
| AIGW-010 | OpenAI adapter + quotas | backend | 10 | AIGW-009,AUTH-003 |
| AIGW-011 | /ai/complete|/ai/chat routes | backend | 8 | AIGW-010 |
| ORCH-012 | Run model + state machine | backend | 10 | AIGW-011 |
| ORCH-013 | POST /flows/{name}/run | backend | 8 | ORCH-012 |
