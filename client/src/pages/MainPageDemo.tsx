import React, { useState } from 'react';
import Mainpage from '../components/generated/Mainpage';

const MainPageDemo = () => {
  const [userName, setUserName] = useState('user.name');
  const [customStyle, setCustomStyle] = useState('');

  return (
    <div style={{ padding: '20px', backgroundColor: '#f8f9fa', minHeight: '100vh' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <header style={{ marginBottom: '30px', textAlign: 'center' }}>
          <h1 style={{ color: '#2c3e50', marginBottom: '10px' }}>
            🎨 MainPage Component - Generated from Figma
          </h1>
          <p style={{ color: '#7f8c8d', fontSize: '16px' }}>
            This component was automatically generated from your Figma design (node-id=0-1)
          </p>
        </header>

        {/* Interactive Controls */}
        <div style={{ 
          backgroundColor: 'white', 
          padding: '20px', 
          borderRadius: '12px', 
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          marginBottom: '30px' 
        }}>
          <h2 style={{ marginBottom: '20px', color: '#34495e' }}>🎮 Interactive Controls</h2>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
                👤 User Name Text:
              </label>
              <input
                type="text"
                value={userName}
                onChange={(e) => setUserName(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '2px solid #e9ecef',
                  borderRadius: '6px',
                  fontSize: '14px'
                }}
                placeholder="Enter user name..."
              />
            </div>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
                🎨 Custom CSS Class:
              </label>
              <input
                type="text"
                value={customStyle}
                onChange={(e) => setCustomStyle(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '2px solid #e9ecef',
                  borderRadius: '6px',
                  fontSize: '14px'
                }}
                placeholder="custom-class-name"
              />
            </div>
          </div>
        </div>

        {/* Component Showcase */}
        <div style={{ 
          backgroundColor: 'white', 
          padding: '20px', 
          borderRadius: '12px', 
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          marginBottom: '30px' 
        }}>
          <h2 style={{ marginBottom: '20px', color: '#34495e' }}>🖼️ Component Preview</h2>
          
          <div style={{ 
            border: '2px dashed #dee2e6', 
            padding: '30px', 
            borderRadius: '8px',
            backgroundColor: '#fafafa',
            textAlign: 'center'
          }}>
            <Mainpage 
              userNameText={userName}
              className={customStyle}
            />
          </div>
        </div>

        {/* Variations */}
        <div style={{ 
          backgroundColor: 'white', 
          padding: '20px', 
          borderRadius: '12px', 
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          marginBottom: '30px' 
        }}>
          <h2 style={{ marginBottom: '20px', color: '#34495e' }}>🔄 Component Variations</h2>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
            <div style={{ padding: '15px', border: '1px solid #dee2e6', borderRadius: '8px' }}>
              <h3 style={{ marginBottom: '10px', fontSize: '14px', color: '#6c757d' }}>Default</h3>
              <Mainpage />
            </div>
            
            <div style={{ padding: '15px', border: '1px solid #dee2e6', borderRadius: '8px' }}>
              <h3 style={{ marginBottom: '10px', fontSize: '14px', color: '#6c757d' }}>With Custom Text</h3>
              <Mainpage userNameText="john.doe" />
            </div>
            
            <div style={{ padding: '15px', border: '1px solid #dee2e6', borderRadius: '8px' }}>
              <h3 style={{ marginBottom: '10px', fontSize: '14px', color: '#6c757d' }}>With Children</h3>
              <Mainpage userNameText="admin">
                <div style={{ marginTop: '10px', padding: '8px', backgroundColor: '#e3f2fd', borderRadius: '4px' }}>
                  Additional content can go here
                </div>
              </Mainpage>
            </div>
          </div>
        </div>

        {/* Technical Details */}
        <div style={{ 
          backgroundColor: 'white', 
          padding: '20px', 
          borderRadius: '12px', 
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <h2 style={{ marginBottom: '20px', color: '#34495e' }}>📋 Technical Details</h2>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div>
              <h3 style={{ marginBottom: '10px', color: '#495057' }}>Component Info</h3>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                <li style={{ padding: '4px 0', borderBottom: '1px solid #f1f3f4' }}>
                  <strong>Name:</strong> Mainpage
                </li>
                <li style={{ padding: '4px 0', borderBottom: '1px solid #f1f3f4' }}>
                  <strong>Source:</strong> Figma node-id=0-1
                </li>
                <li style={{ padding: '4px 0', borderBottom: '1px solid #f1f3f4' }}>
                  <strong>Generated:</strong> {new Date().toLocaleString()}
                </li>
                <li style={{ padding: '4px 0', borderBottom: '1px solid #f1f3f4' }}>
                  <strong>Framework:</strong> React + TypeScript
                </li>
              </ul>
            </div>
            
            <div>
              <h3 style={{ marginBottom: '10px', color: '#495057' }}>Available Props</h3>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                <li style={{ padding: '4px 0', borderBottom: '1px solid #f1f3f4' }}>
                  <strong>userNameText:</strong> string (optional)
                </li>
                <li style={{ padding: '4px 0', borderBottom: '1px solid #f1f3f4' }}>
                  <strong>className:</strong> string (optional)
                </li>
                <li style={{ padding: '4px 0', borderBottom: '1px solid #f1f3f4' }}>
                  <strong>children:</strong> React.ReactNode (optional)
                </li>
              </ul>
            </div>
          </div>
          
          <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
            <h4 style={{ marginBottom: '10px' }}>🚀 Usage Example</h4>
            <pre style={{ 
              backgroundColor: '#2d3748', 
              color: '#e2e8f0', 
              padding: '15px', 
              borderRadius: '6px',
              fontSize: '13px',
              overflow: 'auto'
            }}>
{`import Mainpage from './components/generated/Mainpage';

function App() {
  return (
    <Mainpage 
      userNameText="custom.user"
      className="my-custom-style"
    >
      <p>Additional content</p>
    </Mainpage>
  );
}`}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MainPageDemo;