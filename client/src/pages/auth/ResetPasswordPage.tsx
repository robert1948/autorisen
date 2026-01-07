import { FormEvent, useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import PasswordMeter from "../../components/PasswordMeter";
import { completePasswordReset } from "../../lib/authApi";

const ResetPassword = () => {
  const [searchParams] = useSearchParams();
  const initialToken = searchParams.get("token") ?? "";
  const [token, setToken] = useState(initialToken);
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
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
      const response = await completePasswordReset({
        token,
        password,
        confirm_password: confirmPassword,
      });
      setStatus("success");
      setMessage(response?.message ?? "Password updated successfully. You can now log in.");
    } catch (err) {
      const error = err instanceof Error ? err.message : "Unable to reset password.";
      setStatus("error");
      setMessage(error);
    }
  };

  const disableInputs = status === "loading" || status === "success";

  return (
    <main className="auth-page">
      <section className="auth-card" id="reset-password">
        <header className="auth-card__header">
          <h2>Reset your password</h2>
          <p className="auth-card__subtitle">
            Choose a new password for your CapeControl account. Passwords must be at least 12
            characters long.
          </p>
        </header>
        <form className="auth-form" onSubmit={handleSubmit}>
          <label>
            Reset token
            <input
              required
              type="text"
              value={token}
              onChange={(event) => setToken(event.target.value)}
              placeholder="Paste the token from your email"
              autoComplete="one-time-code"
              disabled={disableInputs}
            />
          </label>
          <label className="auth-password-label">
            New password
            <div className="auth-password-field">
              <input
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
                className="auth-password-toggle"
                onClick={() => setShowPassword((prev) => !prev)}
              >
                {showPassword ? "Hide" : "Show"}
              </button>
            </div>
          </label>
          <PasswordMeter password={password} />
          <label className="auth-password-label">
            Confirm new password
            <div className="auth-password-field">
              <input
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
                className="auth-password-toggle"
                onClick={() => setShowConfirmPassword((prev) => !prev)}
              >
                {showConfirmPassword ? "Hide" : "Show"}
              </button>
            </div>
          </label>
          {message && (
            <p className={status === "success" ? "auth-success" : "auth-error"}>{message}</p>
          )}
          <button className="auth-submit" type="submit" disabled={disableInputs}>
            {status === "loading" ? "Updating..." : "Update password"}
          </button>
        </form>
        <footer className="auth-footer">
          <Link className="auth-footer__link" to="/">
            Return to login
          </Link>
          <Link className="auth-footer__link" to="/forgot-password">
            Didn&apos;t get a token?
          </Link>
        </footer>
      </section>
    </main>
  );
};

export default ResetPassword;
