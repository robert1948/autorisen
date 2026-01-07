import { FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { resendVerification, verifyEmail } from "../../lib/authApi";
import { useAuth } from "../../features/auth/AuthContext";

type Status = "loading" | "success" | "error" | "idle";

const VerifyEmail = () => {
  const { token } = useParams<{ token: string }>();
  const navigate = useNavigate();
  const { state, markEmailVerified } = useAuth();

  const [status, setStatus] = useState<Status>("loading");
  const [message, setMessage] = useState<string>("Verifying your email…");
  const [emailInput, setEmailInput] = useState<string>(state.userEmail ?? "");
  const [resendStatus, setResendStatus] = useState<Status>("idle");
  const [resendMessage, setResendMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("Verification token missing.");
      return;
    }
    let timeoutId: number | undefined;
    verifyEmail(token)
      .then(() => {
        markEmailVerified();
        setStatus("success");
        setMessage("Email verified! Redirecting…");
        timeoutId = window.setTimeout(
          () => navigate("/welcome?email_verified=1", { replace: true }),
          800,
        );
      })
      .catch((err) => {
        const text =
          err instanceof Error ? err.message : "We were unable to verify your email.";
        setStatus("error");
        setMessage(text);
      });
    return () => {
      if (timeoutId) {
        window.clearTimeout(timeoutId);
      }
    };
  }, [token, markEmailVerified, navigate]);

  const handleResend = async (event: FormEvent) => {
    event.preventDefault();
    if (!emailInput) {
      setResendStatus("error");
      setResendMessage("Enter the email you used to register.");
      return;
    }
    setResendStatus("loading");
    setResendMessage(null);
    try {
      await resendVerification(emailInput);
      setResendStatus("success");
      setResendMessage(`Verification email sent to ${emailInput}. Check your inbox.`);
    } catch (err) {
      const text =
        err instanceof Error ? err.message : "Unable to resend the verification email.";
      setResendStatus("error");
      setResendMessage(text);
    }
  };

  return (
    <main className="verify-email-page">
      <section className="verify-email-card">
        <h1>Email Verification</h1>
        <p className={`verify-email-card__message verify-email-card__message--${status}`}>
          {message}
        </p>
        {status === "error" && (
          <form className="verify-email-card__resend" onSubmit={handleResend}>
            <label>
              Email address
              <input
                type="email"
                value={emailInput}
                onChange={(event) => setEmailInput(event.target.value)}
                placeholder="you@example.com"
                required
              />
            </label>
            <button type="submit" disabled={resendStatus === "loading"}>
              {resendStatus === "loading" ? "Resending…" : "Resend verification email"}
            </button>
            {resendMessage && (
              <p className={`verify-email-card__status verify-email-card__status--${resendStatus}`}>
                {resendMessage}
              </p>
            )}
          </form>
        )}
      </section>
    </main>
  );
};

export default VerifyEmail;
