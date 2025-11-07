import React from 'react';
import Logo from '../components/Logo';
import '../components/Auth/auth.css';

const LogoTestPage: React.FC = () => {
  return (
    <div style={{ padding: '40px', backgroundColor: '#0f1720', color: 'white', minHeight: '100vh' }}>
      <h1 style={{ textAlign: 'center', marginBottom: '40px' }}>CapeControl Logo Test Page</h1>
      
      <div style={{ display: 'grid', gap: '40px', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))' }}>
        
        <div style={{ textAlign: 'center', padding: '20px', backgroundColor: '#0b1220', borderRadius: '12px' }}>
          <h3>Small Logo (64x64)</h3>
          <Logo size="small" />
          <p style={{ marginTop: '10px', fontSize: '14px' }}>Perfect for navigation bars</p>
        </div>

        <div style={{ textAlign: 'center', padding: '20px', backgroundColor: '#0b1220', borderRadius: '12px' }}>
          <h3>Medium Logo (128x128)</h3>
          <Logo size="medium" />
          <p style={{ marginTop: '10px', fontSize: '14px' }}>Great for card headers</p>
        </div>

        <div style={{ textAlign: 'center', padding: '20px', backgroundColor: '#0b1220', borderRadius: '12px' }}>
          <h3>Large Logo (256x256)</h3>
          <Logo size="large" />
          <p style={{ marginTop: '10px', fontSize: '14px' }}>Hero sections and splash</p>
        </div>

        <div style={{ textAlign: 'center', padding: '20px', backgroundColor: '#0b1220', borderRadius: '12px' }}>
          <h3>Default Logo (1024x1024)</h3>
          <Logo size="default" />
          <p style={{ marginTop: '10px', fontSize: '14px' }}>Maximum quality</p>
        </div>
      </div>

      <div style={{ marginTop: '60px' }}>
        <h2>Available Assets:</h2>
        <div style={{ display: 'grid', gap: '10px', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', marginTop: '20px' }}>
          <div style={{ padding: '15px', backgroundColor: '#0b1220', borderRadius: '8px' }}>
            <h4>Favicon Files</h4>
            <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '14px' }}>
              <li>favicon.ico (multi-size)</li>
              <li>favicon-16x16.png</li>
              <li>favicon-32x32.png</li>
              <li>favicon-48x48.png</li>
            </ul>
          </div>
          
          <div style={{ padding: '15px', backgroundColor: '#0b1220', borderRadius: '8px' }}>
            <h4>Mobile Icons</h4>
            <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '14px' }}>
              <li>apple-touch-icon.png (180x180)</li>
              <li>android-chrome-192x192.png</li>
              <li>android-chrome-512x512.png</li>
            </ul>
          </div>
          
          <div style={{ padding: '15px', backgroundColor: '#0b1220', borderRadius: '8px' }}>
            <h4>UI Variants</h4>
            <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '14px' }}>
              <li>logo-64x64.png</li>
              <li>logo-128x128.png</li>
              <li>logo-256x256.png</li>
              <li>logo-512x512.png</li>
            </ul>
          </div>
        </div>
      </div>

      <div style={{ marginTop: '40px', textAlign: 'center' }}>
        <h3>Navigation Links</h3>
        <div style={{ display: 'flex', gap: '20px', justifyContent: 'center', flexWrap: 'wrap' }}>
          <a href="/auth/login" style={{ color: '#007BFF', textDecoration: 'none', padding: '8px 16px', border: '1px solid #007BFF', borderRadius: '6px' }}>Login Page</a>
          <a href="/auth/mfa" style={{ color: '#007BFF', textDecoration: 'none', padding: '8px 16px', border: '1px solid #007BFF', borderRadius: '6px' }}>MFA Challenge</a>
          <a href="/account/mfa-enroll" style={{ color: '#007BFF', textDecoration: 'none', padding: '8px 16px', border: '1px solid #007BFF', borderRadius: '6px' }}>MFA Enroll</a>
        </div>
      </div>
    </div>
  );
};

export default LogoTestPage;