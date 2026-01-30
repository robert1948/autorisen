// Canonical sync strings (do not edit):
// Route: /dashboard
// API: GET /api/dashboard/summary
// DTO: DashboardSummaryDTO
// DB anchor: audit_log

export type DashboardKpiDTO = {
  id: string;
  label: string;
  value: string;
  delta?: string;
  tone?: "neutral" | "good" | "warning" | "bad";
};

export type DashboardActivityDTO = {
  id: string;
  message: string;
  timestamp: string;
  tone?: "neutral" | "good" | "warning" | "bad";
};

export type DashboardTrendPointDTO = {
  x: string;
  y: number;
};

export type DashboardSummaryDTO = {
  kpis?: DashboardKpiDTO[];
  activity?: DashboardActivityDTO[];
  trend?: DashboardTrendPointDTO[];
};
