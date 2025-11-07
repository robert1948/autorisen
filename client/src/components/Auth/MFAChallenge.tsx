import React, { useEffect, useRef, useState } from 'react';
import './auth.css';
import Logo from '../Logo';

const i18n = {
  'mfa.title': 'Multi-factor authentication',
  'mfa.instruction': 'Enter the 6-digit code sent to your device',
  'mfa.resend': 'Resend SMS',
  'mfa.trouble': 'Trouble with MFA?',
  'mfa.submit': 'Verify',
  'mfa.bypass': 'Bypass MFA (dev only)'
};

type Props = {
  onSuccess: () => void;
  onCancel?: () => void;
};

const simulateVerifyMfa = (code: string): Promise<{ok:boolean,message?:string}> => {
  return new Promise((resolve) => {
    setTimeout(()=>{
      if (code === '123456') resolve({ok:true});
      else resolve({ok:false,message:'Invalid code'});
    },700);
  });
};

const MFAChallenge: React.FC<Props> = ({onSuccess, onCancel}) => {
  const [code, setCode] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [secondsLeft, setSecondsLeft] = useState(120);
  const [resendCooldown, setResendCooldown] = useState(0);
  const [attempts, setAttempts] = useState(0);
  const [lockedUntil, setLockedUntil] = useState<number | null>(null);
  const timerRef = useRef<number | null>(null);

  useEffect(()=>{
    if (lockedUntil) return;
    timerRef.current = window.setInterval(()=>{
      setSecondsLeft(s => Math.max(0,s-1));
      setResendCooldown(s => Math.max(0,s-1));
    },1000);
    return ()=>{ if (timerRef.current) clearInterval(timerRef.current); };
  },[lockedUntil]);

  useEffect(()=>{
    if (secondsLeft === 0) {
      setError('Code expired, request a new code');
    }
  },[secondsLeft]);

  useEffect(()=>{
    if (lockedUntil && Date.now() >= lockedUntil) {
      setLockedUntil(null);
      setAttempts(0);
      setSecondsLeft(120);
      setError(null);
    }
  },[lockedUntil]);

  const onSubmit = async (e?:React.FormEvent) => {
    e?.preventDefault();
    setError(null);
    if (lockedUntil) {
      setError('Account locked. Try later.');
      return;
    }
    if (!/^\d{6}$/.test(code)) {
      setError('Enter a 6-digit code');
      return;
    }
    setLoading(true);
    try{
      const res = await simulateVerifyMfa(code);
      if (res.ok) {
        onSuccess();
      } else {
        setAttempts(a => a+1);
        setError(res.message || 'Verification failed');
        if (attempts+1 >= 3) {
          // lockout 5 minutes
          setLockedUntil(Date.now() + 5*60*1000);
          setError('Too many attempts. Account locked for 5 minutes.');
        }
      }
    }catch(err){
      setError('Network error');
    }finally{
      setLoading(false);
    }
  };

  const resend = () => {
    if (resendCooldown > 0) return;
    setResendCooldown(30);
    setSecondsLeft(120);
    setError(null);
    // simulate sending SMS
    setTimeout(()=>alert('Simulated: SMS resent'),400);
  };

  const devBypass = () => {
    if (import.meta.env.DEV) {
      alert('Development MFA bypass, marking as verified');
      onSuccess();
    }
  };

  return (
    <div className="cc-auth-wrapper">
      <div className="cc-card" role="dialog" aria-labelledby="mfa-title">
        <div className="cc-logo-container">
          <Logo size="default" />
        </div>
        <h2 id="mfa-title" className="cc-h1">{i18n['mfa.title']}</h2>
        <p className="cc-lead">{i18n['mfa.instruction']}</p>

        <form onSubmit={onSubmit} aria-describedby="mfa-desc">
          <div className="cc-form-group" id="mfa-desc">
            <label className="cc-label" htmlFor="mfa-code">6-digit code</label>
            <input id="mfa-code" className="cc-input" type="text" inputMode="numeric" autoComplete="one-time-code" value={code} onChange={(e)=>setCode(e.target.value.replace(/[^0-9]/g,''))} maxLength={6} pattern="\\d{6}" aria-required />
          </div>

          <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',gap:12}}>
            <div className="cc-small">Expires in: <span aria-live="polite">{secondsLeft}s</span></div>
            <div>
              <button type="button" className="cc-links" onClick={(e)=>{e.preventDefault(); resend();}} disabled={resendCooldown>0} aria-disabled={resendCooldown>0}>{resendCooldown>0 ? `Resend (${resendCooldown}s)` : i18n['mfa.resend']}</button>
            </div>
          </div>

          {error && <div className="cc-error" role="alert" style={{marginTop:10}}>{error}</div>}

          <div style={{marginTop:12}}>
            <button className={`cc-primary-btn ${loading ? 'loading' : ''}`} type="submit" disabled={loading} aria-disabled={loading}>{i18n['mfa.submit']}</button>
          </div>
        </form>

        <div style={{display:'flex',justifyContent:'space-between',marginTop:12,alignItems:'center'}}>
          <a href="#" onClick={(e)=>{e.preventDefault(); onCancel && onCancel();}} className="cc-small">Back</a>
          <a href="#" onClick={(e)=>{e.preventDefault(); alert('Open help: ' + i18n['mfa.trouble']);}} className="cc-small">{i18n['mfa.trouble']}</a>
        </div>

        {import.meta.env.DEV && (
          <div style={{marginTop:12}}>
            <button className="cc-social-btn" onClick={devBypass}>{i18n['mfa.bypass']}</button>
          </div>
        )}
      </div>
    </div>
  );
};

export default MFAChallenge;
