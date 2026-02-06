import React from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../../features/auth/AuthContext";

export default function RequireAuth() {
  const { state } = useAuth();
  const location = useLocation();

  if (state.status === "unknown") {
    return <div className="app-loading">Loading session…</div>;
  }

  if (state.status === "unauthenticated") {
    const next = encodeURIComponent(`${location.pathname}${location.search}`);
    return (
      <Navigate
        to={`/auth/login?next=${next}`}
        replace
        state={{ from: location.pathname }}
      />
    );
  }

  return <Outlet />;
}
