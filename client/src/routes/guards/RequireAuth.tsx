import React, { useEffect, useState } from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../../features/auth/AuthContext";

export default function RequireAuth() {
  const { state, loading } = useAuth();
  const location = useLocation();
  const [verificationChecked, setVerificationChecked] = useState(false);

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

  // If we don't yet know the email verification state (or it's false), validate once
  // before mounting protected app pages (prevents dashboard API calls on stale sessions).
  useEffect(() => {
    let cancelled = false;

    const check = async () => {
      if (!state.accessToken) {
        if (!cancelled) setVerificationChecked(true);
        return;
      }

      // Fast-path: already verified in state.
      if (state.isEmailVerified) {
        if (!cancelled) setVerificationChecked(true);
        return;
      }

      try {
        const resp = await fetch("/api/auth/me", {
          method: "GET",
          credentials: "include",
          headers: {
            Authorization: `Bearer ${state.accessToken}`,
          },
        });

        if (resp.ok) {
          const data = (await resp.json()) as { email_verified?: boolean };
          if (data?.email_verified === true) {
            try {
              const raw = window.localStorage.getItem("autorisen-auth");
              const parsed = raw ? (JSON.parse(raw) as any) : {};
              const next = { ...parsed, isEmailVerified: true };
              window.localStorage.setItem("autorisen-auth", JSON.stringify(next));
            } catch {
              // ignore
            }
          }

          if (!cancelled) setVerificationChecked(true);
          return;
        }

        const text = await resp.text();
        const lower = (text || "").toLowerCase();
        if (resp.status === 403 && lower.includes("email not verified")) {
          try {
            window.localStorage.removeItem("autorisen-auth");
            window.localStorage.removeItem("autorisen-refresh-token");
          } catch {
            // ignore
          }
          if (!cancelled) {
            window.location.assign("/auth/verify-email");
          }
          return;
        }

        if (resp.status === 401) {
          try {
            window.localStorage.removeItem("autorisen-auth");
            window.localStorage.removeItem("autorisen-refresh-token");
          } catch {
            // ignore
          }
          if (!cancelled) {
            window.location.assign("/auth/login");
          }
          return;
        }

        if (!cancelled) setVerificationChecked(true);
      } catch {
        if (!cancelled) setVerificationChecked(true);
      }
    };

    check();

    return () => {
      cancelled = true;
    };
  }, [state.accessToken, state.isEmailVerified]);

  if (!verificationChecked) return null;

  return <Outlet />;
}
