import axios from 'axios';

const api = axios.create({ baseURL: '/api/', withCredentials: true, headers: { 'Content-Type': 'application/json' } });
api.interceptors.request.use((config) => {
  const csrf = document.cookie.split('; ').find((part) => part.startsWith('csrftoken='))?.split('=').slice(1).join('=');
  if (csrf) config.headers['X-CSRFToken'] = decodeURIComponent(csrf);
  return config;
});
api.interceptors.response.use((response) => response, (error) => {
  const message = error.response?.data?.error || error.response?.data?.detail || error.message || 'Request failed';
  return Promise.reject(new Error(typeof message === 'string' ? message : JSON.stringify(message)));
});
export default api;
