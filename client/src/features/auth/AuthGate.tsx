import { ReactNode, useState } from "react";

import { useAuth } from "./AuthContext";
import { resendVerification } from "../../lib/authApi";

const PendingVerificationNotice = ({ email }: { email: string | null }) => {
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [message, setMessage] = useState<string | null>(null);

  const handleResend = async () => {
    if (!email) {
      setStatus("error");
      setMessage("Sign in again to resend the verification email.");
      return;
    }
    setStatus("loading");
    setMessage(null);
    try {
      await resendVerification(email);
      setStatus("success");
      setMessage(`Verification email sent to ${email}.`);
    } catch (err) {
      const text = err instanceof Error ? err.message : "Unable to resend verification email.";
      setStatus("error");
      setMessage(text);
    }
  };

  return (
    <section className="auth-pending">
      <h3>Verify your email to continue</h3>
      <p>
        We sent a verification link to <strong>{email ?? "your email address"}</strong>. Click the link in
        that message to finish activating your account.
      </p>
      <button type="button" className="auth-pending__button" onClick={handleResend} disabled={status === "loading"}>
        {status === "loading" ? "Resending…" : "Resend verification email"}
      </button>
      {message && <p className={`auth-pending__status auth-pending__status--${status}`}>{message}</p>}
    </section>
  );
};

const AuthGate = ({ children, fallback }: { children: ReactNode; fallback?: ReactNode }) => {
  const { state } = useAuth();
  if (!state.accessToken) {
    return fallback ?? <p className="auth-gate-message">Please log in to access this section.</p>;
  }
  if (!state.isEmailVerified) {
    return <PendingVerificationNotice email={state.userEmail} />;
  }
  return <>{children}</>;
};

export default AuthGate;
