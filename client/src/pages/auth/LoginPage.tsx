import React, { useState } from 'react';
import { Link, useNavigate } from "react-router-dom";
import '../../components/Auth/auth.css';
import Logo from '../../components/Logo';

import { useAuth } from "../../features/auth/AuthContext";
import { resendVerification } from "../../lib/authApi";

const i18n = {
  'login.title': 'Log in to CapeControl',
  'login.lead': 'Welcome back! Enter your credentials to access the control center.',
  'login.button': 'Log in',
  'login.or': 'OR CONTINUE WITH',
  'login.forgot': 'Forgot your password?',
  'login.forgotEmail': 'Forgot your email?',
  'login.signup': 'Need an account? Start the signup flow',
  'mfa.bypass_note': 'reCAPTCHA is not configured. Set VITE_RECAPTCHA_SITE_KEY when you are ready to enforce verification. A temporary bypass token has been supplied for local testing.'
};

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { loginUser } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<{ email?:string, password?:string }>({});
  const [errorCode, setErrorCode] = useState<"EMAIL_NOT_VERIFIED" | null>(null);
  const [emailForResend, setEmailForResend] = useState<string | null>(null);
  const [resendStatus, setResendStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [resendMessage, setResendMessage] = useState<string | null>(null);

  const validate = () => {
    const errs: { email?:string, password?:string } = {};
    if (!email) errs.email = 'Email is required';
    else if (!/^\S+@\S+\.\S+$/.test(email)) errs.email = 'Enter a valid email';
    if (!password) errs.password = 'Password is required';
    setValidationErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const onSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    setError(null);
    setErrorCode(null);
    setEmailForResend(null);
    setResendStatus("idle");
    setResendMessage(null);
    if (!validate()) return;
    setLoading(true);
    try {
      await loginUser(email.trim(), password, null);
      navigate("/app", { replace: true });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Invalid credentials";
      const normalizedMessage = message.toLowerCase();
      if (normalizedMessage.includes("not verified")) {
        setErrorCode("EMAIL_NOT_VERIFIED");
        setEmailForResend(email.trim());
        setError("Email not verified. Check your inbox or resend.");
      } else {
        setError(message);
      }
    } finally {
      setLoading(false);
    }
  };

  const onResendVerification = async () => {
    if (!emailForResend) return;
    setResendStatus("loading");
    setResendMessage(null);
    try {
      await resendVerification(emailForResend);
      setResendStatus("success");
      setResendMessage("Verification email sent");
    } catch (_err) {
      setResendStatus("error");
      setResendMessage("Could not resend, try again");
    }
  };

  return (
    <div className="cc-auth-wrapper">
      <main className="cc-card" aria-live="polite">
        <div className="cc-logo-container">
          <Logo size="default" />
        </div>
        <h1 className="cc-h1">{i18n['login.title']}</h1>
        <p className="cc-lead">{i18n['login.lead']}</p>

        <form onSubmit={onSubmit} aria-label="Login form">
          <div className="cc-form-group">
            <label className="cc-label" htmlFor="email">Email</label>
            <input id="email" className={`cc-input ${validationErrors.email ? 'error' : ''}`} type="email" value={email} onChange={e => setEmail(e.target.value)} aria-invalid={!!validationErrors.email} aria-describedby={validationErrors.email? 'email-error' : undefined} />
            {validationErrors.email && <div id="email-error" className="cc-error">{validationErrors.email}</div>}
          </div>

          <div className="cc-form-group">
            <label className="cc-label" htmlFor="password">Password</label>
            <div className="cc-pass-wrap">
              <input id="password" className={`cc-input ${validationErrors.password ? 'error' : ''}`} type={showPassword ? 'text' : 'password'} value={password} onChange={e => setPassword(e.target.value)} aria-invalid={!!validationErrors.password} aria-describedby={validationErrors.password? 'pass-error' : undefined} />
              <button type="button" className="cc-pass-toggle" aria-pressed={showPassword} onClick={() => setShowPassword(s => !s)}>{showPassword ? 'Hide' : 'Show'}</button>
            </div>
            {validationErrors.password && <div id="pass-error" className="cc-error">{validationErrors.password}</div>}
          </div>

          {import.meta.env.DEV && (
            <div className="cc-recaptcha-note" role="note">{i18n['mfa.bypass_note']}</div>
          )}

          {error && <div className="cc-error" role="alert">{error}</div>}
          {errorCode === "EMAIL_NOT_VERIFIED" && (
            <div style={{ marginTop: 10 }}>
              <button
                type="button"
                className={`cc-primary-btn ${resendStatus === "loading" ? "loading" : ""}`}
                onClick={onResendVerification}
                disabled={resendStatus === "loading"}
                aria-disabled={resendStatus === "loading"}
              >
                {resendStatus === "loading" ? "Sending..." : "Resend verification email"}
              </button>
              {resendMessage && (
                <div
                  className={resendStatus === "success" ? "auth-status auth-status--success" : "auth-status auth-status--error"}
                  style={{ marginTop: 8 }}
                >
                  {resendMessage}
                </div>
              )}
            </div>
          )}

          <div style={{marginTop:12}}>
            <button className={`cc-primary-btn ${loading ? 'loading' : ''}`} type="submit" disabled={loading} aria-disabled={loading}>
              {loading ? (<><span className="spinner" aria-hidden>⏳</span> {i18n['login.button']}</>) : i18n['login.button']}
            </button>
          </div>

          <div style={{ marginTop: 10 }}>
            <Link
              to="/auth/register"
              className="cc-primary-btn"
              role="button"
              aria-label="Create free account"
              style={{ display: 'block', textAlign: 'center' }}
            >
              Create free account
            </Link>
          </div>

          <div className="cc-register-microcopy" style={{ marginTop: 10, textAlign: 'center' }}>
            <span>New here? </span>
            <Link className="cc-muted-link" to="/auth/register">Create an account when you’re ready.</Link>
          </div>
        </form>

        <div className="cc-divider">{i18n['login.or']}</div>

        <div style={{display:'grid',gap:10}}>
          <button className="cc-social-btn" onClick={() => alert('Start OAuth flow: /auth/google')} aria-label="Continue with Google">
            <span className="cc-social-icon" aria-hidden><svg width="18" height="18" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg"><rect width="48" height="48" rx="8" fill="#fff"/></svg></span>
            Continue with Google
          </button>
          <button className="cc-social-btn" onClick={() => alert('Start OAuth flow: /auth/linkedin')} aria-label="Continue with LinkedIn">
            <span className="cc-social-icon" aria-hidden><svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><rect width="24" height="24" rx="4" fill="#fff"/></svg></span>
            Continue with LinkedIn
          </button>
        </div>

        <div className="cc-links" style={{marginTop:14}}>
          <Link to="/auth/forgot-password">{i18n['login.forgot']}</Link>
          <a href="mailto:support@capecontrol.ai">{i18n['login.forgotEmail']}</a>
        </div>

        <p className="cc-agree" style={{marginTop:16}}>
          By clicking Log in, you agree to CapeControl's <a href="/terms" target="_blank" rel="noopener noreferrer">terms</a>, <a href="/privacy" target="_blank" rel="noopener noreferrer">privacy policy</a>, and <a href="/cookies" target="_blank" rel="noopener noreferrer">cookie policy</a>.
        </p>

      </main>
    </div>
  );
};

export default LoginPage;
