import React from 'react';
import Frame1 from '../components/generated/Frame1';

const Demo1Demo = () => {
  return (
    <div style={{ padding: '20px', backgroundColor: '#f5f5f5', minHeight: '100vh' }}>
      <h1>🎨 Frame1 Demo - Generated from Figma</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <h2>Default Component</h2>
        <Frame1 />
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h2>With Custom Props</h2>
        <Frame1 
          userNameText="custom.user"
          className="custom-styling"
        />
      </div>

      <div style={{ marginTop: '40px', padding: '20px', backgroundColor: 'white', borderRadius: '8px' }}>
        <h3>📋 Component Details</h3>
        <ul>
          <li><strong>Component:</strong> Frame1</li>
          <li><strong>Generated:</strong> {new Date().toLocaleString()}</li>
          <li><strong>Source:</strong> CapeWire Design System (Figma)</li>
          <li><strong>Framework:</strong> React + TypeScript</li>
        </ul>
      </div>
    </div>
  );
};

export default Demo1Demo;
