// client/src/config/features.ts
export const features = {
  onboarding: import.meta.env.VITE_FF_ONBOARDING === "true",
  sunbirdPilot: import.meta.env.VITE_FF_SUNBIRD_PILOT === "true",
  agentsShell: import.meta.env.VITE_FF_AGENTS_SHELL === "true",
  payments: import.meta.env.VITE_FF_PAYMENTS === "true",
} as const;
