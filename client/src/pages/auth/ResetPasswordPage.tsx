import { FormEvent, useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";

import Logo from "../../components/Logo";
import PasswordMeter from "../../components/PasswordMeter";
import "../../components/Auth/auth.css";
import { completePasswordReset } from "../../lib/authApi";

const ResetPassword = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const initialToken = searchParams.get("token") ?? "";
  const [token, setToken] = useState(initialToken);
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [status, setStatus] = useState<"idle" | "loading" | "error">("idle");
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    setToken(initialToken);
  }, [initialToken]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!token) {
      setStatus("error");
      setMessage("A valid reset token is required.");
      return;
    }
    if (password !== confirmPassword) {
      setStatus("error");
      setMessage("Passwords do not match.");
      return;
    }
    setStatus("loading");
    setMessage(null);

    try {
      await completePasswordReset({
        token,
        new_password: password,
      });
      navigate("/auth/login", {
        replace: true,
        state: { notice: "Password reset successful." },
      });
    } catch (err) {
      const error = err instanceof Error ? err.message : "Unable to reset password.";
      setStatus("error");
      setMessage(error);
    }
  };

  const disableInputs = status === "loading";

  return (
    <div className="cc-auth-wrapper">
      <main className="cc-card" aria-live="polite">
        <div className="cc-logo-container">
          <Logo size="default" />
        </div>
        <h1 className="cc-h1">Reset your password</h1>
        <p className="cc-lead">
          Choose a new password for your CapeControl account. Passwords must be at least 12
          characters long.
        </p>

        <form onSubmit={handleSubmit} aria-label="Reset password form">
          <div className="cc-form-group">
            <label className="cc-label" htmlFor="reset-token">
              Reset token
            </label>
            <input
              id="reset-token"
              className="cc-input"
              required
              type="text"
              value={token}
              onChange={(event) => setToken(event.target.value)}
              placeholder="Paste the token from your email"
              autoComplete="one-time-code"
              disabled={disableInputs}
            />
          </div>

          <div className="cc-form-group">
            <label className="cc-label" htmlFor="new-password">
              New password
            </label>
            <div className="cc-pass-wrap">
              <input
                id="new-password"
                className="cc-input"
                type={showPassword ? "text" : "password"}
                required
                minLength={12}
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="Create a strong password"
                autoComplete="new-password"
                disabled={disableInputs}
              />
              <button
                type="button"
                className="cc-pass-toggle"
                onClick={() => setShowPassword((prev) => !prev)}
              >
                {showPassword ? "Hide" : "Show"}
              </button>
            </div>
          </div>

          <PasswordMeter password={password} />

          <div className="cc-form-group">
            <label className="cc-label" htmlFor="confirm-password">
              Confirm new password
            </label>
            <div className="cc-pass-wrap">
              <input
                id="confirm-password"
                className="cc-input"
                type={showConfirmPassword ? "text" : "password"}
                required
                minLength={12}
                value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)}
                placeholder="Re-enter your password"
                autoComplete="new-password"
                disabled={disableInputs}
              />
              <button
                type="button"
                className="cc-pass-toggle"
                onClick={() => setShowConfirmPassword((prev) => !prev)}
              >
                {showConfirmPassword ? "Hide" : "Show"}
              </button>
            </div>
          </div>

          {message && <div className="cc-error" role="alert">{message}</div>}

          <div style={{ marginTop: 12 }}>
            <button
              className={`cc-primary-btn ${status === "loading" ? "loading" : ""}`}
              type="submit"
              disabled={disableInputs}
              aria-disabled={disableInputs}
            >
              {status === "loading" ? (
                <>
                  <span className="spinner" aria-hidden>
                    ⏳
                  </span>
                  Updating...
                </>
              ) : (
                "Update password"
              )}
            </button>
          </div>
        </form>

        <div className="cc-links" style={{ marginTop: 16 }}>
          <Link to="/auth/login">Return to login</Link>
          <Link to="/auth/forgot-password">Didn&apos;t get a token?</Link>
        </div>
      </main>
    </div>
  );
};

export default ResetPassword;
