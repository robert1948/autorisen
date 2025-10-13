import { FormEvent, useState } from "react";

import { useAuth } from "./AuthContext";

const AuthForms = () => {
  const { state, loginUser, logout, loading, error } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    await loginUser(email, password);
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
        <div className="auth-captcha">
          <div className="auth-captcha__status">
            <span className="auth-captcha__spinner" aria-hidden="true" />
            <span>Verifying…</span>
          </div>
          <div className="auth-captcha__brand">
            <span>CapeControl</span>
            <a href="#privacy">Privacy</a>
            <span>•</span>
            <a href="#terms">Terms</a>
          </div>
        </div>
        <p className="auth-terms">
          By clicking Log in, you agree to CapeControl&apos;s <a href="#terms">terms</a>,
          <a href="#privacy"> privacy policy</a>, and <a href="#privacy">cookie policy</a>.
        </p>
        {error && <p className="auth-error">{error}</p>}
        <button className="auth-submit" type="submit" disabled={loading}>
          {loading ? "Submitting…" : "Log in"}
        </button>
      </form>
      <footer className="auth-footer">
        <a className="auth-footer__link" href="#support">
          Forgot your password?
        </a>
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
