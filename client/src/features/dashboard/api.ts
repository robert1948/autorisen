import { dashboardSummaryFixture } from "./fixtures";
import type { DashboardSummaryDTO } from "./types";

// Canonical sync strings (do not edit):
// Route: /dashboard
// API: GET /api/dashboard/summary

export async function getDashboardSummary(): Promise<DashboardSummaryDTO> {
  // Freeze-safe scaffold: return fixture data for UI-only rendering.
  // TODO(freeze-lift): Replace with real fetch to GET /api/dashboard/summary.
  return dashboardSummaryFixture;
}
