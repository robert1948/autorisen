import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import { AuthProvider } from './context/AuthContext';
import CapeAIProvider from './context/CapeAIContextSafe';
import ContextErrorBoundary from './components/ContextErrorBoundary';
import './styles.css';

// Enhanced global error handler for React errors
window.addEventListener('error', (event) => {
  console.error('Global error caught:', event.error);
  
  if (event.error?.message?.includes('Minified React error')) {
    console.warn('React minified error detected - checking for context issues');
    event.preventDefault();
    
    // Try to recover by reloading the page
    setTimeout(() => {
      if (window.confirm('Application error detected. Reload the page?')) {
        window.location.reload();
      }
    }, 1000);
  }
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
  event.preventDefault();
});

// Root component with enhanced error boundaries
function SafeApp() {
  return (
    <ContextErrorBoundary>
      <AuthProvider>
        <CapeAIProvider>
          <BrowserRouter>
            <ContextErrorBoundary>
              <App />
            </ContextErrorBoundary>
          </BrowserRouter>
        </CapeAIProvider>
      </AuthProvider>
    </ContextErrorBoundary>
  );
}

// Initialize with error handling
const rootElement = document.getElementById('root');

if (!rootElement) {
  console.error('Root element not found');
} else {
  try {
    const root = ReactDOM.createRoot(rootElement);
    root.render(<SafeApp />);
  } catch (error) {
    console.error('Failed to initialize React app:', error);
    
    // Fallback rendering
    rootElement.innerHTML = `
      <div style="padding: 20px; text-align: center; font-family: system-ui;">
        <h1>Application Error</h1>
        <p>The application failed to start. Please refresh the page.</p>
        <button onclick="window.location.reload()" style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">
          Reload Page
        </button>
      </div>
    `;
  }
}
