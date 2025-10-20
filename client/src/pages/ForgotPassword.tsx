import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";

import { requestPasswordReset } from "../lib/authApi";

const ForgotPassword = () => {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [message, setMessage] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setStatus("loading");
    setMessage(null);

    try {
      const response = await requestPasswordReset(email);
      setStatus("success");
      setMessage(response?.message ?? "Check your email for reset instructions.");
    } catch (err) {
      const error = err instanceof Error ? err.message : "Unable to process request.";
      setStatus("error");
      setMessage(error);
    }
  };

  return (
    <main className="auth-page">
      <section className="auth-card" id="forgot-password">
        <header className="auth-card__header">
          <h2>Forgot your password?</h2>
          <p className="auth-card__subtitle">
            Enter the email associated with your CapeControl account and we&apos;ll send you a reset
            link.
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
              autoComplete="email"
            />
          </label>
          {message && (
            <p className={status === "success" ? "auth-success" : "auth-error"}>{message}</p>
          )}
          <button className="auth-submit" type="submit" disabled={status === "loading"}>
            {status === "loading" ? "Sending..." : "Send reset link"}
          </button>
        </form>
        <footer className="auth-footer">
          <Link className="auth-footer__link" to="/">
            Return to login
          </Link>
          <a className="auth-footer__link" href="mailto:support@capecontrol.ai">
            Need help? Contact support
          </a>
        </footer>
      </section>
    </main>
  );
};

export default ForgotPassword;
