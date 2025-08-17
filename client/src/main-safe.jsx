import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import { AuthProvider } from './context/AuthContext';
import CapeAIProvider from './context/CapeAIContextSafe';
import ContextErrorBoundary from './components/ContextErrorBoundary';
import './styles.css';

// Safer approach with error boundaries and safer context
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ContextErrorBoundary>
      <AuthProvider>
        <CapeAIProvider>
          <BrowserRouter>
            <App />
          </BrowserRouter>
        </CapeAIProvider>
      </AuthProvider>
    </ContextErrorBoundary>
  </React.StrictMode>
);
