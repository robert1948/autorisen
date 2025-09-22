// client/src/api/auth-logout.js - Enhanced logout methods

const DEFAULT_LOCAL_API = 'http://localhost:8000/api';
const env = import.meta && import.meta.env ? import.meta.env : {};
let API_BASE;
if (env.PROD) {
  API_BASE = 'https://www.cape-control.com/api';
} else if (env.VITE_API_BASE) {
  const provided = env.VITE_API_BASE;
  if (provided.includes('localhost') || provided.includes('127.0.0.1')) {
    API_BASE = `${provided.replace(/\/$/, '')}/api`;
  } else {
    API_BASE = '/api';
  }
} else {
  API_BASE = DEFAULT_LOCAL_API;
}

// Token management utility functions
function getToken() {
  return localStorage.getItem('token');
}

function clearToken() {
  localStorage.removeItem('token');
}

/**
 * Logout user - revoke token on server and clear local storage
 */
export async function logoutUser() {
  try {
    const token = getToken();
    if (token) {
      // Call server-side logout endpoint
      const response = await fetch(`${API_BASE}/auth/v2/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      // Even if server call fails, we still clear local storage
      if (!response.ok) {
        console.warn('⚠️ Server logout failed, but continuing with local cleanup');
      }
    }
  } catch (error) {
    console.warn('⚠️ Logout request failed:', error.message);
    // Continue with local cleanup even if server fails
  } finally {
    // Always clear local storage regardless of server response
    clearToken();
    localStorage.removeItem('user_data');
    localStorage.removeItem('refresh_token');
  }
}

/**
 * Logout from all devices - revoke all user tokens
 */
export async function logoutAllDevices() {
  try {
    const token = getToken();
    if (token) {
      const response = await fetch(`${API_BASE}/auth/v2/logout-all`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to logout from all devices');
      }
    }
  } finally {
    // Clear local storage
    clearToken();
    localStorage.removeItem('user_data');
    localStorage.removeItem('refresh_token');
  }
}

/**
 * Emergency logout - force clear all local data
 */
export function emergencyLogout() {
  localStorage.clear(); // Clear all localStorage
  sessionStorage.clear(); // Clear all sessionStorage
  
  // Clear any cookies if used
  document.cookie.split(";").forEach(cookie => {
    const eqPos = cookie.indexOf("=");
    const name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie;
    document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/`;
  });
}
