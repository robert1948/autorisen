import React, { useEffect } from "react";
import { Link } from "react-router-dom";

import "../../components/Auth/auth.css";

type Props = {
  fromPath: string;
  allowContinue?: boolean;
  continueTo?: string;
};

export default function SoftGateInterstitial({
  fromPath,
  allowContinue = false,
  continueTo = "/",
}: Props) {
  useEffect(() => {
    try {
      const perRouteKey = `softGateShown:${fromPath}`;
      if (!window.sessionStorage.getItem(perRouteKey)) {
        window.sessionStorage.setItem(perRouteKey, "true");
      }
      if (!window.sessionStorage.getItem("softGateShown")) {
        window.sessionStorage.setItem("softGateShown", "true");
      }
    } catch {
      // ignore
    }
  }, [fromPath]);

  return (
    <div className="cc-auth-wrapper">
      <main className="cc-card" aria-live="polite">
        <h1 className="cc-h1">You need an account to access this feature.</h1>
        <p className="cc-lead">
          Log in to continue, or create a free account in under a minute.
        </p>

        <div style={{ display: "grid", gap: 10, marginTop: 16 }}>
          <Link
            to="/auth/login"
            state={{ from: fromPath }}
            className="cc-primary-btn"
            role="button"
            aria-label="Log in"
            style={{ display: "block", textAlign: "center" }}
          >
            Log in
          </Link>

          <Link
            to="/auth/register"
            state={{ from: fromPath }}
            className="cc-primary-btn"
            role="button"
            aria-label="Create free account"
            style={{ display: "block", textAlign: "center" }}
          >
            Create free account
          </Link>

          {allowContinue && (
            <Link
              to={continueTo}
              className="cc-muted-link"
              aria-label="Continue browsing"
              style={{ textAlign: "center" }}
            >
              Continue browsing
            </Link>
          )}
        </div>
      </main>
    </div>
  );
}
