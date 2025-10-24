import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../features/auth/AuthContext";

const SOCIAL_PROVIDERS = ["google", "linkedin"] as const;
type SocialProvider = (typeof SOCIAL_PROVIDERS)[number];
const isSocialProvider = (value: string): value is SocialProvider =>
  SOCIAL_PROVIDERS.includes(value as SocialProvider);

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
    const nextParam = params.get("next");
    const targetPath =
      nextParam && nextParam.startsWith("/") ? nextParam : "/dashboard";

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
    if (!isSocialProvider(provider)) {
      setStatus("error");
      setMessage("Invalid OAuth state value.");
      return;
    }

    const stateKey = `oauth:state:${provider}`;
    const recaptchaKey = `oauth:recaptcha:${provider}`;
    const storedState = sessionStorage.getItem(stateKey);
    if (storedState && storedState !== stateParam) {
      sessionStorage.removeItem(stateKey);
      sessionStorage.removeItem(recaptchaKey);
      setStatus("error");
      setMessage("OAuth state verification failed. Please try again.");
      return;
    }

    const recaptchaToken = sessionStorage.getItem(recaptchaKey);
    if (!recaptchaToken) {
      sessionStorage.removeItem(stateKey);
      sessionStorage.removeItem(recaptchaKey);
      setStatus("error");
      setMessage("Verification expired. Please retry the sign-in.");
      return;
    }

    const redirectUri = `${window.location.origin}/auth/callback`;

    const handler =
      provider === "google"
        ? loginWithGoogle({ code, redirect_uri: redirectUri, recaptcha_token: recaptchaToken })
        : provider === "linkedin"
        ? loginWithLinkedIn({ code, redirect_uri: redirectUri, recaptcha_token: recaptchaToken })
        : Promise.reject(new Error("Unsupported identity provider."));

    handler
      .then(() => {
        sessionStorage.removeItem(stateKey);
        sessionStorage.removeItem(recaptchaKey);
        setMessage("Sign-in successful. Redirecting…");
        setTimeout(() => navigate(targetPath, { replace: true }), 500);
      })
      .catch((err: unknown) => {
        sessionStorage.removeItem(stateKey);
        sessionStorage.removeItem(recaptchaKey);
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
