// client/src/utils/api-interceptors.js
/**
 * API Interceptors for CapeControl
 * ===============================
 * 
 * Handles automatic logout on token expiration and other auth failures.
 */

import { getToken, clearToken } from './token';
import { emergencyLogout } from '../api/auth-logout';

// Create axios instance with interceptors
export function setupApiInterceptors(axios, navigate) {
  // Request interceptor - add auth token
  axios.interceptors.request.use(
    (config) => {
      const token = getToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Response interceptor - handle auth failures
  axios.interceptors.response.use(
    (response) => {
      return response;
    },
    (error) => {
      const { response } = error;
      
      if (response?.status === 401) {
        // Check if logout is required
        const logoutRequired = response.headers['x-logout-required'] === 'true' ||
                              response.data?.logout_required === true;
        
        if (logoutRequired) {
          console.warn('🚪 Token expired or invalid - forcing logout');
          
          // Perform emergency logout (don't wait for server)
          emergencyLogout();
          
          // Redirect to login
          if (navigate) {
            navigate('/login', { 
              state: { 
                message: 'Your session has expired. Please log in again.',
                type: 'warning' 
              } 
            });
          } else {
            // Fallback if navigate not available
            window.location.href = '/login?expired=true';
          }
        }
      }
      
      return Promise.reject(error);
    }
  );
}

// Manual check for token expiration
export function checkTokenExpiration() {
  const token = getToken();
  if (!token) return false;

  try {
    const [, payloadBase64] = token.split('.');
    const payload = JSON.parse(atob(payloadBase64));
    const now = Math.floor(Date.now() / 1000);
    
    if (payload.exp < now) {
      console.warn('🚪 Token expired - forcing logout');
      emergencyLogout();
      return true; // Token is expired
    }
    
    return false; // Token is valid
  } catch (error) {
    console.error('Token validation error:', error);
    emergencyLogout();
    return true; // Treat invalid token as expired
  }
}

// Periodic token validation (optional)
export function startTokenValidation(intervalMs = 60000) {
  const interval = setInterval(() => {
    if (checkTokenExpiration()) {
      clearInterval(interval);
    }
  }, intervalMs);
  
  return interval;
}
