import axios from "axios";

// Default to a relative base so the app works behind nginx with an /api proxy.
// Set VITE_API_URL at build time (e.g. "https://api.example.com") to override.
const API_BASE = import.meta.env.VITE_API_URL ?? "";

const api = axios.create({
  baseURL: `${API_BASE}/api/v1`,
});

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Redirect to login on 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export default api;
