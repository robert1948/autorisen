import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';

// Minimal test component to isolate the issue
function MinimalApp() {
  return (
    <div className="p-4">
      <h1>Minimal Test - No Context</h1>
      <p>If this loads without error, the issue is with our contexts.</p>
    </div>
  );
}

const rootElement = document.getElementById('root');

if (rootElement) {
  createRoot(rootElement).render(
    <React.StrictMode>
      <BrowserRouter>
        <MinimalApp />
      </BrowserRouter>
    </React.StrictMode>
  );
}
