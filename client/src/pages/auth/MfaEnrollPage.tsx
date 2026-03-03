import React, { useState } from 'react';
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

type SetupResponse = { secret: string; otpauth_uri: string; qr_svg: string };
type VerifyResponse = { verified: boolean; message: string };

const MFAEnroll: React.FC = () => {
  const [qrSvg, setQrSvg] = useState<string | null>(null);
  const [secret, setSecret] = useState<string | null>(null);
  const [code, setCode] = useState('');
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const startSetup = async () => {
    setError(null);
    setMessage(null);
    setLoading(true);
    try {
      const res = await authedPost<SetupResponse>('/auth/mfa/setup');
      setQrSvg(res.qr_svg);
      setSecret(res.secret);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Setup failed');
    } finally {
      setLoading(false);
    }
  };

  const verify = async () => {
    if (!/^\d{6}$/.test(code)) {
      setError('Enter a 6-digit code');
      return;
    }
    setError(null);
    setMessage(null);
    setLoading(true);
    try {
      const res = await authedPost<VerifyResponse>('/auth/mfa/verify', { code });
      if (res.verified) {
        setMessage(res.message);
      } else {
        setError(res.message);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Verification failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="cc-auth-wrapper">
      <div className="cc-card" role="region" aria-labelledby="enroll-title">
        <div className="cc-logo-container">
          <Logo size="default" />
        </div>
        <h2 id="enroll-title" className="cc-h1">Enable MFA (Authenticator App)</h2>
        <p className="cc-lead">Scan the QR code with an authenticator app (Google Authenticator, Authy, etc.) or copy the secret key</p>

        {!qrSvg && (
          <div>
            <button className="cc-primary-btn" onClick={startSetup} disabled={loading}>
              {loading ? 'Setting up…' : 'Start setup'}
            </button>
          </div>
        )}

        {qrSvg && (
          <div style={{ display: 'grid', gap: 12 }}>
            <img
              src={qrSvg}
              alt="QR code — scan with authenticator app"
              style={{ width: 200, height: 200, borderRadius: 8, background: '#fff' }}
            />
            <div className="cc-form-group">
              <label className="cc-label">Secret key</label>
              <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                <code style={{ padding: 10, background: 'rgba(255,255,255,0.03)', borderRadius: 8, letterSpacing: 2 }}>
                  {secret}
                </code>
                <button
                  className="cc-social-btn"
                  onClick={() => {
                    navigator.clipboard?.writeText(secret || '');
                    setMessage('Copied to clipboard');
                    setTimeout(() => setMessage(null), 2000);
                  }}
                >
                  Copy
                </button>
              </div>
            </div>

            <div className="cc-form-group">
              <label className="cc-label">Enter 6-digit code from app</label>
              <input
                className="cc-input"
                value={code}
                onChange={(e) => setCode(e.target.value.replace(/[^0-9]/g, ''))}
                maxLength={6}
                inputMode="numeric"
                autoComplete="one-time-code"
                placeholder="000000"
              />
            </div>

            {message && (
              <div className="cc-small" role="status" style={{ color: '#4ade80' }}>
                {message}
              </div>
            )}
            {error && (
              <div className="cc-error" role="alert">
                {error}
              </div>
            )}

            <div>
              <button className="cc-primary-btn" onClick={verify} disabled={loading}>
                {loading ? 'Verifying…' : 'Verify & enable MFA'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MFAEnroll;
