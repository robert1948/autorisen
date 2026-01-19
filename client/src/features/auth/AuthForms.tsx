import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";

import Recaptcha from "../../components/Recaptcha";
import { useAuth } from "./AuthContext";
import { resendVerification } from "../../lib/authApi";

const SOCIAL_PROVIDERS = ["google", "linkedin"] as const;
type SocialProvider = (typeof SOCIAL_PROVIDERS)[number];

const AuthForms = () => {
  const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? "/api";

  const { state, loginUser, logout, loading, error } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [recaptchaToken, setRecaptchaToken] = useState<string | null>(null);
  const [recaptchaError, setRecaptchaError] = useState<string | null>(null);
  const [socialError, setSocialError] = useState<string | null>(null);
  const [resendStatus, setResendStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [resendMessage, setResendMessage] = useState<string | null>(null);

  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID as string | undefined;
  const linkedinClientId = import.meta.env.VITE_LINKEDIN_CLIENT_ID as string | undefined;

  const oauthRecaptchaKey = (provider: SocialProvider) => `oauth:recaptcha:${provider}`;
  const oauthStateKey = (provider: SocialProvider) => `oauth:state:${provider}`;

  const handleRecaptcha = (token: string | null) => {
    setRecaptchaToken(token);
    if (!token) {
      setRecaptchaError("Please complete the verification");
      SOCIAL_PROVIDERS.forEach((provider) => sessionStorage.removeItem(oauthRecaptchaKey(provider)));
    } else {
      setRecaptchaError(null);
    }
  };

  const startOAuth = async (provider: SocialProvider) => {
    if (!recaptchaToken) {
      setRecaptchaError("Please complete the verification");
      return;
    }
    const clientId = provider === "google" ? googleClientId : linkedinClientId;
    if (!clientId) {
      setSocialError(
        provider === "google"
          ? "Google login is not configured. Set VITE_GOOGLE_CLIENT_ID."
          : "LinkedIn login is not configured. Set VITE_LINKEDIN_CLIENT_ID.",
      );
      return;
    }
    setSocialError(null);
    sessionStorage.setItem(oauthRecaptchaKey(provider), recaptchaToken);
    const oauthBase = `${API_BASE}/api/auth/oauth/${provider}/start`;
    const params = new URLSearchParams({
      next: "/dashboard",
      format: "json",
    });
    const stateKey = oauthStateKey(provider);

    try {
      const response = await fetch(`${oauthBase}?${params.toString()}`, {
        method: "GET",
        credentials: "include",
        headers: {
          Accept: "application/json",
        },
      });
      const contentType = response.headers.get("content-type") ?? "";
      if (response.ok && contentType.includes("application/json")) {
        const data = (await response.json()) as {
          authorization_url?: string;
          state?: string;
        };
        if (data.state) {
          sessionStorage.setItem(stateKey, data.state);
        }
        if (data.authorization_url) {
          window.location.href = data.authorization_url;
          return;
        }
      }
      if (!response.ok) {
        throw new Error(`Unexpected response (${response.status})`);
      }
    } catch (err) {
      console.error(`Failed to start ${provider} OAuth flow`, err);
      setSocialError(
        provider === "google"
          ? "Unable to connect to Google. Please try again."
          : "Unable to connect to LinkedIn. Please try again.",
      );
      sessionStorage.removeItem(stateKey);
      return;
    }

    // Fallback to legacy redirect if JSON negotiation failed.
    sessionStorage.removeItem(stateKey);
    const fallbackParams = new URLSearchParams({ next: "/dashboard" });
    window.location.href = `${oauthBase}?${fallbackParams.toString()}`;
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setSocialError(null);
    if (!recaptchaToken) {
      setRecaptchaError("Please complete the verification");
      return;
    }
    await loginUser(email, password, recaptchaToken);
  };

  const handleResend = async () => {
    if (!state.userEmail) {
      setResendStatus("error");
      setResendMessage("Sign in again to resend the verification email.");
      return;
    }
    setResendStatus("loading");
    setResendMessage(null);
    try {
      await resendVerification(state.userEmail);
      setResendStatus("success");
      setResendMessage(`Verification email sent to ${state.userEmail}.`);
    } catch (err) {
      const text = err instanceof Error ? err.message : "Unable to resend the verification email.";
      setResendStatus("error");
      setResendMessage(text);
    }
  };

  if (state.accessToken) {
    if (!state.isEmailVerified) {
      return (
        <section className="auth-card" id="auth">
          <header className="auth-card__header">
            <h2>Check your inbox</h2>
            <p className="auth-card__subtitle">
              We emailed a verification link to {state.userEmail ?? "your address"}. You need to
              verify before accessing your account.
            </p>
          </header>
          <button
            type="button"
            className="auth-submit"
            onClick={handleResend}
            disabled={resendStatus === "loading"}
          >
            {resendStatus === "loading" ? "Resending…" : "Resend verification email"}
          </button>
          {resendMessage && (
            <p
              className={`auth-status ${
                resendStatus === "error"
                  ? "auth-status--error"
                  : resendStatus === "success"
                  ? "auth-status--success"
                  : ""
              }`}
            >
              {resendMessage}
            </p>
          )}
          <button type="button" className="btn btn--ghost" onClick={logout}>
            Logout
          </button>
        </section>
      );
    }
    return (
      <section className="auth-card" id="auth">
        <header>
          <span className="badge">Access</span>
          <h3>Signed in</h3>
        </header>
        <p>You are logged in as {state.userEmail ?? "current user"}.</p>
        <button type="button" className="btn btn--ghost" onClick={logout}>
          Logout
        </button>
      </section>
    );
  }

  return (
    <section className="auth-card" id="auth">
      <header className="auth-card__header">
        <h2>Log in to CapeControl</h2>
        <p className="auth-card__subtitle">
          Welcome back! Enter your credentials to access the control center.
        </p>
      </header>
      <form className="auth-form" onSubmit={handleSubmit}>
        <label>
          Email
          <input
            required
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="you@example.com"
            autoComplete="username"
          />
        </label>
        <label className="auth-password-label">
          Password
          <div className="auth-password-field">
            <input
              type={showPassword ? "text" : "password"}
              required
              minLength={12}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Enter your password"
              autoComplete="current-password"
            />
            <button
              type="button"
              className="auth-password-toggle"
              onClick={() => setShowPassword((prev) => !prev)}
            >
              {showPassword ? "Hide" : "Show"}
            </button>
          </div>
        </label>
        <Recaptcha onVerify={handleRecaptcha} error={recaptchaError ?? undefined} />
        <p className="auth-terms">
          By clicking Log in, you agree to CapeControl&apos;s <a href="#terms">terms</a>,
          <a href="#privacy"> privacy policy</a>, and <a href="#privacy">cookie policy</a>.
        </p>
        {error && <p className="auth-error">{error}</p>}
        {socialError && <p className="auth-error">{socialError}</p>}
        <button className="auth-submit" type="submit" disabled={loading}>
          {loading ? "Submitting…" : "Log in"}
        </button>
        <div className="auth-social">
          <p className="auth-social__label">Or continue with</p>
          <div className="auth-social__buttons">
            <button
              type="button"
              className="auth-social__button auth-social__button--google"
              onClick={() => void startOAuth("google")}
              disabled={loading || !googleClientId}
            >
              Continue with Google
            </button>
            <button
              type="button"
              className="auth-social__button auth-social__button--linkedin"
              onClick={() => void startOAuth("linkedin")}
              disabled={loading || !linkedinClientId}
            >
              Continue with LinkedIn
            </button>
          </div>
        </div>
      </form>
      <footer className="auth-footer">
        <Link className="auth-footer__link" to="/auth/forgot-password">
          Forgot your password?
        </Link>
        <a className="auth-footer__link" href="mailto:support@capecontrol.ai">
          Forgot your email?
        </a>
        <a className="auth-footer__link" href="/register">
          Need an account? Start the signup flow
        </a>
      </footer>
    </section>
  );
};

export default AuthForms;
