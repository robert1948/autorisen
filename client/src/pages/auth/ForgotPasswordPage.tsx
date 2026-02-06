import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";

import Logo from "../../components/Logo";
import "../../components/Auth/auth.css";
import { requestPasswordReset } from "../../lib/authApi";

const ForgotPassword = () => {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "success">("idle");
  const [message, setMessage] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setStatus("loading");
    setMessage(null);

    const neutralMessage = "If the email exists, we’ve sent a reset link.";
    try {
      await requestPasswordReset(email.trim());
    } catch (err) {
      console.warn("Password reset request failed", err);
    } finally {
      setStatus("success");
      setMessage(neutralMessage);
    }
  };

  return (
    <div className="cc-auth-wrapper">
      <main className="cc-card" aria-live="polite">
        <div className="cc-logo-container">
          <Logo size="default" />
        </div>
        <h1 className="cc-h1">Forgot your password?</h1>
        <p className="cc-lead">
          Enter the email associated with your CapeControl account and we&apos;ll send you a reset
          link.
        </p>

        <form onSubmit={handleSubmit} aria-label="Forgot password form">
          <div className="cc-form-group">
            <label className="cc-label" htmlFor="forgot-email">
              Email
            </label>
            <input
              id="forgot-email"
              className="cc-input"
              required
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@example.com"
              autoComplete="email"
            />
          </div>

          {message && <div className="cc-success" role="status">{message}</div>}

          <div style={{ marginTop: 12 }}>
            <button
              className={`cc-primary-btn ${status === "loading" ? "loading" : ""}`}
              type="submit"
              disabled={status === "loading"}
              aria-disabled={status === "loading"}
            >
              {status === "loading" ? (
                <>
                  <span className="spinner" aria-hidden>
                    ⏳
                  </span>
                  Sending...
                </>
              ) : (
                "Send reset link"
              )}
            </button>
          </div>
        </form>

        <div className="cc-links" style={{ marginTop: 16 }}>
          <Link to="/auth/login">Return to login</Link>
          <a href="mailto:support@capecontrol.ai">Need help? Contact support</a>
        </div>
      </main>
    </div>
  );
};

export default ForgotPassword;
