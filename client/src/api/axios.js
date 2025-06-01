import axios from 'axios';

const instance = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000, // optional: 10 seconds timeout
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true // allows sending cookies if needed
});

// Optional: Add interceptors for request/response (like logging, error handling)
instance.interceptors.request.use(
  (config) => {
    // You can add auth tokens here if needed
    // config.headers.Authorization = `Bearer ${yourAuthToken}`;
    return config;
  },
  (error) => Promise.reject(error)
);

instance.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle global error messages
    console.error('API error:', error);
    return Promise.reject(error);
  }
);

export default instance;
