import React, { useState } from 'react';
import '../../components/Auth/auth.css';
import Logo from '../../components/Logo';

const i18n = {
  'enroll.title': 'Enable MFA (Authenticator App)',
  'enroll.instruction': 'Scan the QR code with an authenticator app or copy the secret key',
  'enroll.verify': 'Verify setup',
  'enroll.copy': 'Copy'
};

const simulateEnrollApi = (): Promise<{qrDataUrl:string, secret:string}> => {
  return new Promise((resolve)=>{
    setTimeout(()=>{
      // simple placeholder QR url: a data URL with SVG
      const secret = 'ABCD-EFGH-1234';
      const svg = `<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><rect width='100%' height='100%' fill='#0b1220'/><text x='50%' y='50%' fill='#ffffff' font-size='12' text-anchor='middle' dominant-baseline='middle'>QR</text></svg>`;
      const qrDataUrl = 'data:image/svg+xml;utf8,' + encodeURIComponent(svg);
      resolve({qrDataUrl, secret});
    },500);
  });
};

const MFAEnroll: React.FC = () => {
  const [qr, setQr] = useState<string | null>(null);
  const [secret, setSecret] = useState<string | null>(null);
  const [code, setCode] = useState('');
  const [message, setMessage] = useState<string | null>(null);

  const start = async () => {
    const res = await simulateEnrollApi();
    setQr(res.qrDataUrl);
    setSecret(res.secret);
  };

  const verify = () => {
    if (!/^[0-9]{6}$/.test(code)) { setMessage('Enter a 6-digit code'); return; }
    // simulate verification
    setTimeout(()=>{
      if (code === '123456') setMessage('MFA enabled (simulated)');
      else setMessage('Invalid code');
    },600);
  };

  return (
    <div className="cc-auth-wrapper">
      <div className="cc-card" role="region" aria-labelledby="enroll-title">
        <div className="cc-logo-container">
          <Logo size="default" />
        </div>
        <h2 id="enroll-title" className="cc-h1">{i18n['enroll.title']}</h2>
        <p className="cc-lead">{i18n['enroll.instruction']}</p>

        {!qr && (
          <div>
            <button className="cc-primary-btn" onClick={start}>{i18n['enroll.verify']}</button>
          </div>
        )}

        {qr && (
          <div style={{display:'grid',gap:12}}>
            <img src={qr} alt="QR code to scan" style={{width:160,height:160,borderRadius:8,background:'#fff'}} />
            <div className="cc-form-group">
              <label className="cc-label">Secret key</label>
              <div style={{display:'flex',gap:8}}>
                <code style={{padding:10,background:'rgba(255,255,255,0.03)',borderRadius:8}}>{secret}</code>
                <button className="cc-social-btn" onClick={()=>{navigator.clipboard?.writeText(secret||''); alert('Copied');}}>{i18n['enroll.copy']}</button>
              </div>
            </div>

            <div className="cc-form-group">
              <label className="cc-label">Enter code from app</label>
              <input className="cc-input" value={code} onChange={e=>setCode(e.target.value.replace(/[^0-9]/g,''))} maxLength={6} />
            </div>

            {message && <div className="cc-small" role="status">{message}</div>}

            <div>
              <button className="cc-primary-btn" onClick={verify}>{i18n['enroll.verify']}</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MFAEnroll;
