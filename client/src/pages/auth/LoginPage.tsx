import React, { useState, useCallback } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import '../../components/Auth/auth.css';
import Logo from '../../components/Logo';
import Recaptcha from '../../components/Recaptcha';
import { useAuth } from '../../features/auth/AuthContext';

const API_BASE = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? '';

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
  const location = useLocation();
  const navigate = useNavigate();
  const { loginUser, loading: authLoading, error: authError } = useAuth();
  const notice = (location.state as { notice?: string } | null)?.notice;
  const searchParams = new URLSearchParams(location.search);
  const nextParam = searchParams.get('next');
  const stateRedirect = (location.state as { from?: string } | null)?.from;
  const safeNext = nextParam && nextParam.startsWith('/') ? nextParam : null;
  const redirectTo = safeNext ?? stateRedirect ?? '/dashboard';
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<{ email?:string, password?:string }>({});
  const [recaptchaToken, setRecaptchaToken] = useState<string | null>(null);
  const [socialError, setSocialError] = useState<string | null>(null);

  const startOAuth = useCallback(async (provider: 'google' | 'linkedin') => {
    if (!recaptchaToken) {
      setSocialError('Please complete the verification first.');
      return;
    }
    setSocialError(null);
    // Store recaptcha token for the callback page
    sessionStorage.setItem(`oauth:recaptcha:${provider}`, recaptchaToken);
    const oauthBase = `${API_BASE}/api/auth/oauth/${provider}/start`;
    const params = new URLSearchParams({ next: redirectTo, format: 'json' });
    try {
      const response = await fetch(`${oauthBase}?${params.toString()}`, {
        method: 'GET',
        credentials: 'include',
        headers: { Accept: 'application/json' },
      });
      const contentType = response.headers.get('content-type') ?? '';
      if (response.ok && contentType.includes('application/json')) {
        const data = await response.json() as { authorization_url?: string; state?: string };
        if (data.state) sessionStorage.setItem(`oauth:state:${provider}`, data.state);
        if (data.authorization_url) { window.location.href = data.authorization_url; return; }
      }
      if (!response.ok) throw new Error(`Unexpected response (${response.status})`);
      setSocialError(`Could not start ${provider} sign-in. Please try again.`);
    } catch (err) {
      console.error(`Failed to start ${provider} OAuth flow`, err);
      setSocialError(`Unable to connect to ${provider}. Please try again.`);
    }
  }, [recaptchaToken, redirectTo]);

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
    if (!validate()) return;
    setLoading(true);
    try {
      await loginUser(email.trim(), password, recaptchaToken);
      navigate(redirectTo, { replace: true });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Network error';
      setError(message);
    } finally {
      setLoading(false);
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
        {notice && <div className="cc-success" role="status">{notice}</div>}

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

          <Recaptcha onVerify={setRecaptchaToken} />

          {(error || authError) && (
            <div className="cc-error" role="alert">{error || authError}</div>
          )}

          <div style={{marginTop:12}}>
            <button
              className={`cc-primary-btn ${loading || authLoading ? 'loading' : ''}`}
              type="submit"
              disabled={loading || authLoading}
              aria-disabled={loading || authLoading}
            >
              {loading || authLoading ? (
                <>
                  <span className="spinner" aria-hidden>⏳</span> {i18n['login.button']}
                </>
              ) : (
                i18n['login.button']
              )}
            </button>
          </div>
        </form>

        <div className="cc-divider">{i18n['login.or']}</div>

        {socialError && <div className="cc-error" role="alert" style={{marginBottom:10}}>{socialError}</div>}

        <div style={{display:'grid',gap:10}}>
          <button className="cc-social-btn" onClick={() => void startOAuth('google')} aria-label="Continue with Google">
            <span className="cc-social-icon" aria-hidden><svg width="18" height="18" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M43.6 24.5c0-1.6-.1-3.1-.4-4.5H24v8.5h11c-.5 2.5-1.9 4.6-4 6v5h6.5c3.8-3.5 6.1-8.7 6.1-15z" fill="#4285F4"/><path d="M24 44c5.4 0 9.9-1.8 13.2-4.9l-6.5-5c-1.8 1.2-4 1.9-6.7 1.9-5.2 0-9.6-3.5-11.1-8.2H6.3v5.2C9.5 39.6 16.2 44 24 44z" fill="#34A853"/><path d="M12.9 27.8c-.4-1.2-.6-2.5-.6-3.8s.2-2.6.6-3.8v-5.2H6.3C4.8 18 4 21 4 24s.8 6 2.3 9l6.6-5.2z" fill="#FBBC05"/><path d="M24 11c2.9 0 5.5 1 7.6 3l5.7-5.7C33.9 5.1 29.4 3 24 3 16.2 3 9.5 7.4 6.3 15l6.6 5.2C14.4 15.5 18.8 11 24 11z" fill="#EA4335"/></svg></span>
            Continue with Google
          </button>
          <button className="cc-social-btn" onClick={() => void startOAuth('linkedin')} aria-label="Continue with LinkedIn">
            <span className="cc-social-icon" aria-hidden><svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M20.5 2h-17A1.5 1.5 0 002 3.5v17A1.5 1.5 0 003.5 22h17a1.5 1.5 0 001.5-1.5v-17A1.5 1.5 0 0020.5 2zM8 19H5v-9h3zM6.5 8.25A1.75 1.75 0 118.3 6.5a1.78 1.78 0 01-1.8 1.75zM19 19h-3v-4.74c0-1.42-.6-1.93-1.38-1.93A1.74 1.74 0 0013 14.19V19h-3v-9h2.9v1.3a3.11 3.11 0 012.7-1.4c1.55 0 3.36.86 3.36 3.66z" fill="#0A66C2"/></svg></span>
            Continue with LinkedIn
          </button>
        </div>

        <div className="cc-links" style={{marginTop:14}}>
          <Link to="/auth/forgot-password">{i18n['login.forgot']}</Link>
          <a href="#" onClick={(e)=>{e.preventDefault(); alert('Forgot email flow placeholder')}}>{i18n['login.forgotEmail']}</a>
        </div>

        <p className="cc-agree" style={{marginTop:16}}>
          By clicking Log in, you agree to CapeControl's <a href="/terms" target="_blank" rel="noopener noreferrer">terms</a>, <a href="/privacy" target="_blank" rel="noopener noreferrer">privacy policy</a>, and <a href="/cookies" target="_blank" rel="noopener noreferrer">cookie policy</a>.
        </p>

        <div style={{textAlign:'center',marginTop:12}}>
          <a href="#" onClick={(e)=>{e.preventDefault(); alert('Start signup flow')}}>{i18n['login.signup']}</a>
        </div>
      </main>
    </div>
  );
};

export default LoginPage;
