import React from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../../features/auth/AuthContext";

export default function RequireAuth() {
  const { state, loading } = useAuth();
  const location = useLocation();

  // While AuthProvider is loading (login in progress etc.)
  if (loading) return null; // or a spinner component

  const authed = Boolean(state.accessToken);

  if (!authed) {
    return (
      <Navigate
        to="/auth/login"
        replace
        state={{ from: location.pathname }}
      />
    );
  }

  return <Outlet />;
}
