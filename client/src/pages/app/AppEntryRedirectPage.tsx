import { Navigate } from "react-router-dom";
import { features } from "../../config/features";

function isOnboardingComplete(): boolean {
  return localStorage.getItem("onboarding_complete") === "true";
}

export default function AppEntryRedirect() {
  // Enforce onboarding gate (if enabled)
  if (features.onboarding && !isOnboardingComplete()) {
    return <Navigate to="/app/onboarding" replace />;
  }

  // Prefer Sunbird-Pilot when enabled
  if (features.sunbirdPilot) {
    return <Navigate to="/app/sunbird-pilot" replace />;
  }

  // Fallback
  return <Navigate to="/app/dashboard" replace />;
}
