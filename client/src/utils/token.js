// Get token from localStorage
export function getToken() {
  return localStorage.getItem('token');
}

// Save token to localStorage
export function setToken(token) {
  localStorage.setItem('token', token);
}

// Remove token from localStorage
export function clearToken() {
  localStorage.removeItem('token');
}

// Check if token is expired (or malformed)
export function isTokenExpired(token) {
  if (!token) return true;

  try {
    const [, payloadBase64] = token.split('.');
    const payload = JSON.parse(atob(payloadBase64));
    const now = Math.floor(Date.now() / 1000); // seconds since epoch
    return payload.exp < now;
  } catch (err) {
    console.warn('Invalid token format:', err);
    return true; // Treat malformed token as expired
  }
}
