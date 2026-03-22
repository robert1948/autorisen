# OpenClaw Pilot Baseline Task Checklist

- Pilot ID: OPCLAW-PILOT-001
- Baseline window: 2026-03-22 to 2026-03-26
- Owner: Product Lead (TBD)
- Last updated: 2026-03-22

## Completion Rules

- Capture each task end-to-end using the current non-agent workflow.
- Record start/end timestamps and outcome.
- Record number of handoffs and tools touched.
- Mark data sensitivity level and whether escalation was required.
- Minimum sample size: 40 tasks per use case.

## Use Case A Baseline: Support inbox triage and drafting

| Task ID | Task description | Sample target | Owner | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| A-01 | Classify inbound request type | 10 | Support Lead (TBD) | Not Started |  |
| A-02 | Draft first response for review | 10 | Support Lead (TBD) | Not Started |  |
| A-03 | Retrieve related context from internal docs | 10 | Ops Lead (TBD) | Not Started |  |
| A-04 | Escalate ambiguous/high-risk requests | 10 | Security Observer (TBD) | Not Started |  |

## Use Case B Baseline: Project status brief generation

| Task ID | Task description | Sample target | Owner | Status | Notes |
| --- | --- | --- | --- | --- | --- |
| B-01 | Gather latest project updates from source docs | 10 | PM Lead (TBD) | Not Started |  |
| B-02 | Draft project status summary for leadership | 10 | PM Lead (TBD) | Not Started |  |
| B-03 | Validate summary against source evidence | 10 | Compliance Lead (TBD) | Not Started |  |
| B-04 | Publish final brief and track corrections | 10 | Ops Lead (TBD) | Not Started |  |

## Baseline Data Capture Fields

| Field | Required | Description |
| --- | --- | --- |
| task_id | Yes | Unique ID (A-01, B-02, etc.) |
| user_id | Yes | Pilot user performing task |
| started_at | Yes | UTC timestamp |
| ended_at | Yes | UTC timestamp |
| duration_minutes | Yes | Derived from start/end |
| outcome | Yes | success, failure, escalated |
| handoffs_count | Yes | Number of human handoffs |
| tools_touched | Yes | Comma-separated apps/tools |
| data_class | Yes | non-sensitive, sanitized |
| notes | No | Optional context |

## Sign-Off

- Product: <approve/reject> <date>
- Engineering: <approve/reject> <date>
- Security: <approve/reject> <date>
- Operations: <approve/reject> <date>
