import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { AuthProvider } from './context/AuthContext';

// ✅ Import Bootstrap CSS first
import 'bootstrap/dist/css/bootstrap.min.css';

// ✅ Import Bootstrap's JS bundle for navbar toggling
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

// ✅ Global CSS (existing)
import './index.css';

// ✅ SCSS entry point
import './styles/app.scss';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </React.StrictMode>
);
