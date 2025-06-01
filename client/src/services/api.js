import axios from 'axios';

const api = axios.create({
  baseURL: '/', // assuming FastAPI and frontend are served from the same host
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default api;
