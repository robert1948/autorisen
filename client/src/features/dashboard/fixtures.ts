import type { DashboardSummaryDTO } from "./types";

export const dashboardSummaryFixture: DashboardSummaryDTO = {
  kpis: [
    {
      id: "kpi-ops",
      label: "Ops Health",
      value: "Good",
      delta: "+2%",
      tone: "good",
    },
    {
      id: "kpi-alerts",
      label: "Open Alerts",
      value: "3",
      delta: "-1",
      tone: "warning",
    },
    {
      id: "kpi-sla",
      label: "SLA",
      value: "99.9%",
      delta: "+0.1%",
      tone: "good",
    },
  ],
  trend: [
    { x: "Mon", y: 12 },
    { x: "Tue", y: 18 },
    { x: "Wed", y: 9 },
    { x: "Thu", y: 15 },
    { x: "Fri", y: 22 },
  ],
  activity: [
    {
      id: "act-1",
      message: "CapeAI summarized last 24h operational changes.",
      timestamp: "2026-01-30T10:05:00Z",
      tone: "neutral",
    },
    {
      id: "act-2",
      message: "Audit event recorded: user signed in.",
      timestamp: "2026-01-30T09:42:00Z",
      tone: "good",
    },
    {
      id: "act-3",
      message: "Warning: 1 workflow needs review.",
      timestamp: "2026-01-30T08:15:00Z",
      tone: "warning",
    },
  ],
};
