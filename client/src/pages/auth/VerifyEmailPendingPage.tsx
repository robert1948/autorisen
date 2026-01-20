import React, { FormEvent, useState } from "react";
import { Link } from "react-router-dom";

import { resendVerification } from "../../lib/authApi";
import { useAuth } from "../../features/auth/AuthContext";

type Status = "idle" | "loading" | "success" | "error";

const VerifyEmailPendingPage: React.FC = () => {
  const { state } = useAuth();
  const [email, setEmail] = useState<string>(state.userEmail ?? "");
  const [status, setStatus] = useState<Status>("idle");
  const [message, setMessage] = useState<string | null>(null);
  const [cooldownUntil, setCooldownUntil] = useState<number | null>(null);

  const cooldownActive =
    typeof cooldownUntil === "number" && Date.now() < cooldownUntil;

  const onResend = async (event: FormEvent) => {
    event.preventDefault();
    if (!email.trim()) {
      setStatus("error");
      setMessage("Enter the email you used to register.");
      return;
    }

    setStatus("loading");
    setMessage(null);
    try {
      await resendVerification(email.trim());
      setStatus("success");
      setMessage("Verification email sent. Check your inbox.");
      setCooldownUntil(Date.now() + 10_000);
    } catch (err) {
      const text = err instanceof Error ? err.message : "Unable to resend verification email.";
      setStatus("error");
      setMessage(text);
    }
  };

  return (
    <main className="verify-email-page">
      <section className="verify-email-card">
        <h1>Verify your email</h1>
        <p className="verify-email-card__message verify-email-card__message--error">
          Check your inbox to verify your email address.
        </p>

        <form className="verify-email-card__resend" onSubmit={onResend}>
          <label>
            Email address
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
            />
          </label>
          <button type="submit" disabled={status === "loading" || cooldownActive}>
            {status === "loading"
              ? "Resending…"
              : cooldownActive
              ? "Please wait…"
              : "Resend verification email"}
          </button>
          {message && (
            <p
              className={`verify-email-card__status verify-email-card__status--${status}`}
            >
              {message}
            </p>
          )}
        </form>

        <p style={{ marginTop: 12 }}>
          <Link to="/auth/login">Back to login</Link>
        </p>
      </section>
    </main>
  );
};

export default VerifyEmailPendingPage;
