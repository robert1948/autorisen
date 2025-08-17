import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import { AuthProvider } from './context/AuthContext';
import CapeAIProvider from './context/CapeAIContext';
import './styles.css'; // ✅ Tailwind import

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AuthProvider>
      <CapeAIProvider>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </CapeAIProvider>
    </AuthProvider>
  </React.StrictMode>
);
