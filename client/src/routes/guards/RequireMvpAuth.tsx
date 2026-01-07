import React from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../../features/auth/AuthContext";

/**
 * MVP route guard stub.
 * TODO: align final behavior with SYSTEM_SPEC auth/onboarding details once spec is completed.
 */
export default function RequireMvpAuth() {
  const { state, loading } = useAuth();
  const location = useLocation();

  if (loading) return null;

  const authed = Boolean(state.accessToken);
  if (!authed) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  return <Outlet />;
}
