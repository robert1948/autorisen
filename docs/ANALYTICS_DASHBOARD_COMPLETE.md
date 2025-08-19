# Analytics Dashboard – Complete Spec (MVP)
## Goals
- Observe API health, usage, and auth success/fail patterns.
- Provide at-a-glance KPIs: requests/min, error rate, p95 latency, active users.

## Sections
1. **KPI Row**: Requests/min, Error %, p95 latency, Active users (24h)
2. **Charts**:
   - Time series: requests/min; error rate
   - Bar: top endpoints by volume
   - Pie: status code distribution
3. **Tables**:
   - Recent errors with trace IDs
   - Top IPs / user agents
4. **Filters**: timeframe, environment

## Data Sources
- `ai_performance_service`, access logs, error tracker.
