import React from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { features } from "../../config/features";
import { useOnboardingStatus } from "../../hooks/useOnboardingStatus";

const allowlistPrefixes = ["/onboarding", "/app/onboarding", "/app/account"];

/* v0.2.5-4: bypass onboarding for users with no session or 100% progress */

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

  // Consider onboarding done if:
  // 1. session.onboarding_completed flag is true, OR
  // 2. progress is 100% (all steps done but /complete wasn't called), OR
  // 3. no session exists (user predates onboarding feature)
  const sessionComplete = Boolean(data?.session?.onboarding_completed);
  const allStepsDone = (data?.progress ?? 0) >= 100;
  const noSession = !data?.session;
  const completed = sessionComplete || allStepsDone || noSession;

  if (!completed && !allowlisted) {
    const next = encodeURIComponent(`${location.pathname}${location.search}`);
    return <Navigate to={`/onboarding/welcome?next=${next}`} replace />;
  }

  return <Outlet />;
}
