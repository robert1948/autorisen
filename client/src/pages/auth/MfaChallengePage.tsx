import React, { useEffect, useRef, useState } from 'react';
import '../../components/Auth/auth.css';
import Logo from '../../components/Logo';
import { getCsrfToken } from '../../lib/authApi';

const API_BASE =
  ((import.meta as unknown as { env?: Record<string, string | undefined> }).env?.VITE_API_BASE as
    | string
    | undefined) ?? '/api';

const AUTH_STORAGE_KEY = 'autorisen-auth';

function getAccessToken(): string | null {
  try {
    const raw = window.localStorage.getItem(AUTH_STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as { accessToken?: string | null };
    return parsed.accessToken ?? null;
  } catch {
    return null;
  }
}

async function authedPost<T>(endpoint: string, body?: unknown): Promise<T> {
  const token = getAccessToken();
  const csrfToken = await getCsrfToken();
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  if (csrfToken) headers['X-CSRF-Token'] = csrfToken;

  const res = await fetch(`${API_BASE}${endpoint}`, {
    method: 'POST',
    headers,
    credentials: 'include',
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error((data as { detail?: string }).detail || `Request failed (${res.status})`);
  }
  return res.json() as Promise<T>;
}

type VerifyResponse = { verified: boolean; message: string };

type Props = {
  onSuccess: () => void;
  onCancel?: () => void;
};

const MFAChallenge: React.FC<Props> = ({ onSuccess, onCancel }) => {
  const [code, setCode] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [attempts, setAttempts] = useState(0);
  const [lockedUntil, setLockedUntil] = useState<number | null>(null);
  const lockTimerRef = useRef<number | null>(null);

  // Unlock when lockout expires
  useEffect(() => {
    if (!lockedUntil) return;
    const remaining = lockedUntil - Date.now();
    if (remaining <= 0) {
      setLockedUntil(null);
      setAttempts(0);
      setError(null);
      return;
    }
    lockTimerRef.current = window.setTimeout(() => {
      setLockedUntil(null);
      setAttempts(0);
      setError(null);
    }, remaining);
    return () => {
      if (lockTimerRef.current) clearTimeout(lockTimerRef.current);
    };
  }, [lockedUntil]);

  const onSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    setError(null);
    if (lockedUntil) {
      setError('Account locked. Try again later.');
      return;
    }
    if (!/^\d{6}$/.test(code)) {
      setError('Enter a 6-digit code');
      return;
    }
    setLoading(true);
    try {
      const res = await authedPost<VerifyResponse>('/auth/mfa/verify', { code });
      if (res.verified) {
        onSuccess();
      } else {
        const newAttempts = attempts + 1;
        setAttempts(newAttempts);
        setError(res.message || 'Verification failed');
        if (newAttempts >= 5) {
          setLockedUntil(Date.now() + 5 * 60 * 1000);
          setError('Too many attempts. Account locked for 5 minutes.');
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Verification failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="cc-auth-wrapper">
      <div className="cc-card" role="dialog" aria-labelledby="mfa-title">
        <div className="cc-logo-container">
          <Logo size="default" />
        </div>
        <h2 id="mfa-title" className="cc-h1">Multi-factor authentication</h2>
        <p className="cc-lead">Enter the 6-digit code from your authenticator app</p>

        <form onSubmit={onSubmit} aria-describedby="mfa-desc">
          <div className="cc-form-group" id="mfa-desc">
            <label className="cc-label" htmlFor="mfa-code">6-digit code</label>
            <input
              id="mfa-code"
              className="cc-input"
              type="text"
              inputMode="numeric"
              autoComplete="one-time-code"
              value={code}
              onChange={(e) => setCode(e.target.value.replace(/[^0-9]/g, ''))}
              maxLength={6}
              placeholder="000000"
              aria-required
            />
          </div>

          {error && (
            <div className="cc-error" role="alert" style={{ marginTop: 10 }}>
              {error}
            </div>
          )}

          <div style={{ marginTop: 12 }}>
            <button
              className={`cc-primary-btn ${loading ? 'loading' : ''}`}
              type="submit"
              disabled={loading || !!lockedUntil}
            >
              {loading ? 'Verifying…' : 'Verify'}
            </button>
          </div>
        </form>

        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 12, alignItems: 'center' }}>
          {onCancel && (
            <a href="#" onClick={(e) => { e.preventDefault(); onCancel(); }} className="cc-small">
              Back
            </a>
          )}
          <a
            href="mailto:support@cape-control.com?subject=MFA%20help"
            className="cc-small"
          >
            Trouble with MFA?
          </a>
        </div>
      </div>
    </div>
  );
};

export default MFAChallenge;
