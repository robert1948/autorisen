import React from 'react';
import Frame1 from '../components/generated/Frame1';

const TestPage = () => {
  return (
    <div style={{ padding: '20px' }}>
      <h1>Test Frame1 Component</h1>
      <Frame1 userNameText="Hello World!" />
    </div>
  );
};

export default TestPage;