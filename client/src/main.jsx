import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import { AuthProvider } from './context/AuthContext';
import CapeAIProvider from './context/CapeAIContextSafe';
import ContextErrorBoundary from './components/ContextErrorBoundary';
import './styles.css';

// Global error handler for React errors
window.addEventListener('error', (event) => {
  if (event.error?.message?.includes('Minified React error')) {
    console.warn('React error caught:', event.error);
    event.preventDefault();
  }
});

// Safer approach with error boundaries and no StrictMode to avoid double mounting
ReactDOM.createRoot(document.getElementById('root')).render(
  <ContextErrorBoundary>
    <AuthProvider>
      <CapeAIProvider>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </CapeAIProvider>
    </AuthProvider>
  </ContextErrorBoundary>
);
