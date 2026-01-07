import React from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../../features/auth/AuthContext";

/**
 * MVP route guard (AuthContext-backed).
 * Enforces the SYSTEM_SPEC §2.5.7 linear flow using a minimal localStorage stub for onboarding completion.
 * TODO: replace onboarding completion stub with authoritative onboarding state when available.
 */
export default function RequireMvpAuth() {
  const { state, loading } = useAuth();
  const location = useLocation();

  if (loading) return null;

  const authed = Boolean(state.accessToken);
  if (!authed) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  const path = location.pathname;
  const isOnboardingRoute = path.startsWith("/onboarding/");

  const onboardingComplete = localStorage.getItem("onboarding_complete") === "true";
  if (!onboardingComplete && !isOnboardingRoute) {
    return <Navigate to="/onboarding/welcome" replace state={{ from: path }} />;
  }

  return <Outlet />;
}
