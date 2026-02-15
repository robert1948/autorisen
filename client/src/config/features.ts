// client/src/config/features.ts
export const features = {
  onboarding: import.meta.env.VITE_FF_ONBOARDING === "true",
  sunbirdPilot: import.meta.env.VITE_FF_SUNBIRD_PILOT === "true",
  agentsShell: import.meta.env.VITE_FF_AGENTS_SHELL === "true",
  payments: import.meta.env.VITE_FF_PAYMENTS === "true",
  /** Dashboard v2 — role-aware dynamic dashboard (spec §4.7) */
  dashboardV2: import.meta.env.VITE_FF_DASHBOARD_V2 !== "false", // enabled by default
} as const;
