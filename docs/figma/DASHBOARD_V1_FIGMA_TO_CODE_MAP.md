# Dashboard v1 — Figma to Code File Map (LOCKED)

**Status:** Locked scaffold map (freeze-safe; no route wiring)  
**Locked by commit:** 738827688a2c707b8e868e9ca6971ee5a50618c1  
**Branch:** chore/dashboard-v1-scaffold  
**Commit message:** chore(dashboard): scaffold DashboardPage v1 file map (no route wiring)

## Canonical Sync Strings (exact text)
- Route: /dashboard
- API: GET /api/dashboard/summary
- DTO: DashboardSummaryDTO
- DB: audit_log
- PageComponent: DashboardPage

## Figma Page/Component Names
- Figma Page: Dashboard v1
- Frame: Route — /dashboard
- Component (Page): DashboardPage
- Components:
  - DashboardPage/PageHeader
  - DashboardPage/KpiCard
  - DashboardPage/Panel
  - DashboardPage/ActivityItem
  - DashboardPage/StatusPill
  - DashboardPage/TrendChart
  - DashboardPage/EmptyState
  - DashboardPage/ErrorState
  - DashboardPage/SkeletonBlock

## VS Code File Map (TypeScript)
### Page
- client/src/pages/DashboardPage.tsx — exports `DashboardPage`

### Feature: dashboard
#### Components
- client/src/features/dashboard/components/PageHeader.tsx — exports `PageHeader` (Figma: DashboardPage/PageHeader)
- client/src/features/dashboard/components/KpiCard.tsx — exports `KpiCard` (Figma: DashboardPage/KpiCard)
- client/src/features/dashboard/components/Panel.tsx — exports `Panel` (Figma: DashboardPage/Panel)
- client/src/features/dashboard/components/ActivityItem.tsx — exports `ActivityItem` (Figma: DashboardPage/ActivityItem)
- client/src/features/dashboard/components/StatusPill.tsx — exports `StatusPill` (Figma: DashboardPage/StatusPill)
- client/src/features/dashboard/components/TrendChart.tsx — exports `TrendChart` (Figma: DashboardPage/TrendChart)
- client/src/features/dashboard/components/EmptyState.tsx — exports `EmptyState` (Figma: DashboardPage/EmptyState)
- client/src/features/dashboard/components/ErrorState.tsx — exports `ErrorState` (Figma: DashboardPage/ErrorState)
- client/src/features/dashboard/components/SkeletonBlock.tsx — exports `SkeletonBlock` (Figma: DashboardPage/SkeletonBlock)

#### Types / API / Mapping
- client/src/features/dashboard/types.ts — includes `DashboardSummaryDTO`
- client/src/features/dashboard/api.ts — GET `/api/dashboard/summary`
- client/src/features/dashboard/mappers.ts — API → `DashboardSummaryDTO` mapping
- client/src/features/dashboard/fixtures.ts — optional local fixtures (for UI-only rendering)

## Route Wiring Note (do not implement during freeze)
Register the route path `/dashboard` to render `DashboardPage` in the client router (common locations): App.tsx or client/src/routes/AppRoutes.tsx (if present). If routing is centralized elsewhere, use the equivalent router definition file and add a `/dashboard` entry pointing to `DashboardPage`.

## Import Pattern Example
```ts
import { DashboardPage } from "./pages/DashboardPage";
import { getDashboardSummary } from "./features/dashboard/api";
```

## Freeze Guardrails

* No routing edits were made in the lock-in commit.
* No deploy actions are permitted under this document.
* Any changes to names/paths must update both Figma and this doc in the same PR/commit.
