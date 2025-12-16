import React from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { features } from "../../config/features";

const allowlistPrefixes = ["/app/onboarding", "/app/account"];

function isOnboardingComplete(): boolean {
  return localStorage.getItem("onboarding_complete") === "true";
}

export default function RequireOnboarding() {
  const location = useLocation();

  if (!features.onboarding) return <Outlet />;

  const complete = isOnboardingComplete();
  const path = location.pathname;

  const allowlisted = allowlistPrefixes.some((p) => path.startsWith(p));
  if (!complete && !allowlisted) {
    return <Navigate to="/app/onboarding" replace state={{ from: path }} />;
  }

  return <Outlet />;
}
