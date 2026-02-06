import React from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useMe } from "../../hooks/useMe";

export default function RequireOnboardingAuth() {
  const location = useLocation();
  const { loading, status, error } = useMe();

  if (loading) {
    return <div className="app-loading">Loading session…</div>;
  }

  if (status === 401 || status === 403) {
    const next = encodeURIComponent(`${location.pathname}${location.search}`);
    return <Navigate to={`/auth/login?next=${next}`} replace />;
  }

  if (error) {
    return <div className="app-loading">Unable to verify session.</div>;
  }

  return <Outlet />;
}
