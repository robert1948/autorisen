import React from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../../features/auth/AuthContext";
import { useOnboardingStatus } from "../../hooks/useOnboardingStatus";

/**
 * MVP route guard (AuthContext-backed).
 * Enforces the SYSTEM_SPEC §2.5.7 linear flow using the real onboarding status API.
 */
export default function RequireMvpAuth() {
  const { state, loading: authLoading } = useAuth();
  const { data: onboardingData, loading: onboardingLoading } = useOnboardingStatus();
  const location = useLocation();

  if (authLoading || onboardingLoading) return null;

  const authed = Boolean(state.accessToken);
  if (!authed) {
    const next = encodeURIComponent(`${location.pathname}${location.search}`);
    return <Navigate to={`/auth/login?next=${next}`} replace />;
  }

  const path = location.pathname;
  const isOnboardingRoute = path.startsWith("/onboarding/");

  const onboardingComplete = onboardingData?.session?.onboarding_completed ?? false;
  if (!onboardingComplete && !isOnboardingRoute) {
    return <Navigate to="/onboarding/welcome" replace state={{ from: path }} />;
  }

  return <Outlet />;
}
