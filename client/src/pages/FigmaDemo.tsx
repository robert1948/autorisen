import React from 'react';
import Frame1 from '../components/generated/Frame1';

const FigmaDemo = () => {
  return (
    <div style={{ padding: '20px', backgroundColor: '#f5f5f5', minHeight: '100vh' }}>
      <h1>🎨 Figma Frame 1 - Generated Component</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <h2>Default Component</h2>
        <Frame1 />
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h2>With Custom Text</h2>
        <Frame1 userNameText="Robert Kleyn" />
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h2>With Additional Content</h2>
        <Frame1 userNameText="John Doe">
          <p style={{ marginTop: '10px', fontSize: '14px', color: '#666' }}>
            Additional content can be added here
          </p>
        </Frame1>
      </div>

      <div style={{ marginTop: '40px', padding: '20px', backgroundColor: 'white', borderRadius: '8px' }}>
        <h3>📋 Component Details</h3>
        <ul>
          <li><strong>Source:</strong> Figma Frame 1 (node 2:9)</li>
          <li><strong>Dimensions:</strong> 269 × 484 pixels</li>
          <li><strong>Elements:</strong> 1 text element (user.name)</li>
          <li><strong>Generated Props:</strong> userNameText</li>
          <li><strong>Design System:</strong> CapeWire Design System</li>
        </ul>
      </div>
    </div>
  );
};

export default FigmaDemo;