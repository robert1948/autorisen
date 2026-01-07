import React from "react";
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../../features/auth/AuthContext";

/**
 * MVP guest-only guard (AuthContext-backed).
 * If a user is already authenticated, redirect to /dashboard.
 */
export default function RequireMvpGuest() {
  const { state, loading } = useAuth();

  if (loading) return null;

  const authed = Boolean(state.accessToken);
  if (authed) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}
