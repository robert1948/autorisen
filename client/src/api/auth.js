// client/src/api/auth.js

const DEFAULT_LOCAL_API = 'http://localhost:8000/api';
// Resolve API base safely for dev vs production:
// - In production, point at the public API URL
// - In development, prefer relative '/api' so Vite proxy handles requests (avoids embedding container hostnames)
// - If VITE_API_BASE explicitly points at localhost (e.g., when running client locally), use that absolute host URL
const env = import.meta && import.meta.env ? import.meta.env : {};
let API_BASE;
if (env.PROD) {
  API_BASE = 'https://www.cape-control.com/api';
} else if (env.VITE_API_BASE) {
  const provided = env.VITE_API_BASE;
  if (provided.includes('localhost') || provided.includes('127.0.0.1')) {
    API_BASE = `${provided.replace(/\/$/, '')}/api`;
  } else {
    // use relative path so the dev server proxy can route to the container-internal backend
    API_BASE = '/api';
  }
} else {
  API_BASE = DEFAULT_LOCAL_API;
}

export async function loginUser(email, password) {
  const response = await fetch(`${API_BASE}/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      username: email,
      password: password
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Login failed');
  }

  return await response.json(); // { access_token, token_type }
}

// V2 Registration API Methods

/**
 * Validate email availability for registration
 */
export async function validateEmail(email) {
  try {
    const response = await fetch(`${API_BASE}/auth/v2/validate-email?email=${encodeURIComponent(email)}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    });

    // Check if response is JSON
    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      throw new Error('Server returned non-JSON response');
    }

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || error.message || 'Email validation failed');
    }

    return await response.json(); // { available: bool, reason?: string, message: string }
  } catch (error) {
    console.error('Email validation error:', error);
    return { 
      available: null, 
      reason: 'validation_error',
      message: 'Unable to validate email. Please try again.'
    };
  }
}

/**
 * Validate password strength
 */
export async function validatePassword(password) {
  try {
    const response = await fetch(`${API_BASE}/auth/v2/validate-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password })
    });

    // Check if response is JSON
    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      throw new Error('Server returned non-JSON response');
    }

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || error.message || 'Password validation failed');
    }

    return await response.json(); // { valid: bool, score: int, requirements: object }
  } catch (error) {
    console.error('Password validation error:', error);
    return {
      valid: false,
      score: 0,
      requirements: {
        minLength: false,
        hasUpper: false,
        hasLower: false,
        hasNumber: false,
        hasSpecial: false
      }
    };
  }
}

/**
 * Register new user with V2 enhanced validation
 */
export async function registerUserV2(userData) {
  try {
    // Map frontend data to backend schema
    const backendData = {
      email: userData.email,
      password: userData.password,
      full_name: `${userData.firstName || ''} ${userData.lastName || ''}`.trim(),
      user_role: userData.role === 'customer' ? 'client' : userData.role, // Map 'customer' to 'client'
      company_name: userData.company || null,
      industry: userData.industry || null,
      project_budget: userData.project_budget || null,
      skills: userData.skills || null,
      portfolio: userData.portfolio || null,
      github: userData.github || null,
      tos_accepted: true // Always true since user completed the form
    };

    console.log('🔄 Mapping frontend data to backend:', { 
      frontend: userData, 
      backend: backendData 
    });

    const response = await fetch(`${API_BASE}/auth/v2/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(backendData)
    });

    // Check if response is JSON
    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      console.error('Non-JSON response received:', await response.text());
      throw new Error('Server error: Invalid response format');
    }

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || data.message || 'Registration failed');
    }

    return data; // { id, email, access_token?, ... }
  } catch (error) {
    console.error('Registration error:', error);
    throw error;
  }
}

/**
 * Enhanced login with better error handling and retry logic
 */
export async function loginUserV2(email, password, retryCount = 0) {
  const MAX_RETRIES = 2;
  const TIMEOUT_MS = 25000; // 25 second timeout (less than Heroku's 30s)
  
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_MS);
    
    const response = await fetch(`${API_BASE}/auth/v2/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    // Check if response is JSON before parsing
    const contentType = response.headers.get('content-type');
    
    if (!response.ok) {
      if (response.status === 503 && retryCount < MAX_RETRIES) {
        // Retry on 503 errors with exponential backoff
        const delayMs = Math.pow(2, retryCount) * 1000; // 1s, 2s, 4s...
        console.log(`Retrying login after ${delayMs}ms (attempt ${retryCount + 1})`);
        await new Promise(resolve => setTimeout(resolve, delayMs));
        return loginUserV2(email, password, retryCount + 1);
      }
      
      if (response.status === 503) {
        throw new Error('Service temporarily unavailable. Please try again in a moment.');
      }
      
      if (contentType && contentType.includes('application/json')) {
        const error = await response.json();
        throw new Error(error.detail || 'Login failed');
      } else {
        // Server returned HTML error page instead of JSON
        throw new Error(`Server error (${response.status}). Please try again later.`);
      }
    }

    if (!contentType || !contentType.includes('application/json')) {
      throw new Error('Server returned invalid response format');
    }

    return await response.json(); // { access_token, token_type, user: {...} }
  } catch (error) {
    if (error.name === 'AbortError' || error.message.includes('timed out')) {
      if (retryCount < MAX_RETRIES) {
        console.log(`Login timed out, retrying... (attempt ${retryCount + 1})`);
        const delayMs = 2000; // 2 second delay for timeout retries
        await new Promise(resolve => setTimeout(resolve, delayMs));
        return loginUserV2(email, password, retryCount + 1);
      }
      throw new Error('Login request timed out. Please check your connection and try again.');
    }
    console.error('Login error:', error);
    throw error;
  }
}
