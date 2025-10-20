import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";

import Recaptcha from "../../components/Recaptcha";
import { useAuth } from "./AuthContext";

const AuthForms = () => {
  const { state, loginUser, logout, loading, error } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [recaptchaToken, setRecaptchaToken] = useState<string | null>(null);
  const [recaptchaError, setRecaptchaError] = useState<string | null>(null);
  const [socialError, setSocialError] = useState<string | null>(null);

  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID as string | undefined;
  const linkedinClientId = import.meta.env.VITE_LINKEDIN_CLIENT_ID as string | undefined;

  const handleRecaptcha = (token: string | null) => {
    setRecaptchaToken(token);
    if (!token) {
      setRecaptchaError("Please complete the verification");
    } else {
      setRecaptchaError(null);
    }
  };

  const startOAuth = (provider: "google" | "linkedin") => {
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
    const random = window.crypto?.randomUUID?.() ?? Math.random().toString(36).slice(2);
    const stateToken = `${provider}:${random}`;
    sessionStorage.setItem(`oauth:state:${provider}`, stateToken);
    const redirectUri = `${window.location.origin}/auth/callback`;
    const params = new URLSearchParams({
      client_id: clientId,
      redirect_uri: redirectUri,
      response_type: "code",
      scope: "openid email profile",
      state: stateToken,
    });
    if (provider === "google") {
      params.set("access_type", "offline");
      params.set("prompt", "select_account");
      window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?${params.toString()}`;
    } else {
      params.set("prompt", "consent");
      window.location.href = `https://www.linkedin.com/oauth/v2/authorization?${params.toString()}`;
    }
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

  if (state.accessToken) {
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
              onClick={() => startOAuth("google")}
              disabled={loading || !googleClientId}
            >
              Continue with Google
            </button>
            <button
              type="button"
              className="auth-social__button auth-social__button--linkedin"
              onClick={() => startOAuth("linkedin")}
              disabled={loading || !linkedinClientId}
            >
              Continue with LinkedIn
            </button>
          </div>
        </div>
      </form>
      <footer className="auth-footer">
        <Link className="auth-footer__link" to="/forgot-password">
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
