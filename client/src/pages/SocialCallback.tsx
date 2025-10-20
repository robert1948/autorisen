import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../features/auth/AuthContext";

const SocialCallback = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { loginWithGoogle, loginWithLinkedIn } = useAuth();
  const [message, setMessage] = useState("Finishing sign-in…");
  const [status, setStatus] = useState<"loading" | "error">("loading");

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const errorParam = params.get("error");
    const errorDescription = params.get("error_description");
    const code = params.get("code");
    const stateParam = params.get("state");

    if (errorParam) {
      setStatus("error");
      setMessage(errorDescription ?? errorParam);
      return;
    }

    if (!code || !stateParam) {
      setStatus("error");
      setMessage("Missing OAuth response parameters.");
      return;
    }

    const [provider] = stateParam.split(":");
    if (!provider) {
      setStatus("error");
      setMessage("Invalid OAuth state value.");
      return;
    }

    const storageKey = `oauth:state:${provider}`;
    const expected = sessionStorage.getItem(storageKey);
    if (expected !== stateParam) {
      setStatus("error");
      setMessage("OAuth state verification failed. Please try again.");
      return;
    }

    const redirectUri = `${window.location.origin}/auth/callback`;

    const handler =
      provider === "google"
        ? loginWithGoogle({ code, redirect_uri: redirectUri })
        : provider === "linkedin"
        ? loginWithLinkedIn({ code, redirect_uri: redirectUri })
        : Promise.reject(new Error("Unsupported identity provider."));

    handler
      .then(() => {
        sessionStorage.removeItem(storageKey);
        setMessage("Sign-in successful. Redirecting…");
        setTimeout(() => navigate("/", { replace: true }), 500);
      })
      .catch((err: unknown) => {
        const msg =
          err instanceof Error ? err.message : "Unable to complete social login. Please try again.";
        setStatus("error");
        setMessage(msg);
      });
  }, [location.search, loginWithGoogle, loginWithLinkedIn, navigate]);

  return (
    <section className="auth-card auth-card--callback">
      <header>
        <span className="badge">OAuth</span>
        <h2>{status === "error" ? "Sign-in failed" : "Signing you in…"}</h2>
      </header>
      <p className={`auth-status ${status === "error" ? "auth-status--error" : ""}`}>{message}</p>
      <button
        type="button"
        className="auth-submit auth-submit--secondary"
        onClick={() => navigate("/", { replace: true })}
      >
        Return to home
      </button>
    </section>
  );
};

export default SocialCallback;
