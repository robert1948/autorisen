import React from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { features } from "../../config/features";
import { useOnboardingStatus } from "../../hooks/useOnboardingStatus";

const allowlistPrefixes = ["/onboarding", "/app/onboarding", "/app/account"];

function hasExploreQuietly(): boolean {
  return localStorage.getItem("onboarding_explore_quietly") === "true";
}

export default function RequireOnboarding() {
  const location = useLocation();
  const { loading, error, status, data } = useOnboardingStatus();

  if (!features.onboarding) return <Outlet />;

  if (loading) {
    return <div className="app-loading">Loading onboarding…</div>;
  }

  if (status === 401 || status === 403) {
    const next = encodeURIComponent(`${location.pathname}${location.search}`);
    return <Navigate to={`/auth/login?next=${next}`} replace />;
  }

  if (error) {
    return <div className="app-loading">Unable to verify onboarding.</div>;
  }

  if (hasExploreQuietly()) return <Outlet />;

  const path = location.pathname;
  const allowlisted = allowlistPrefixes.some((p) => path.startsWith(p));
  const completed = Boolean(data?.session?.onboarding_completed);

  if (!completed && !allowlisted) {
    const next = encodeURIComponent(`${location.pathname}${location.search}`);
    return <Navigate to={`/onboarding/welcome?next=${next}`} replace />;
  }

  return <Outlet />;
}
