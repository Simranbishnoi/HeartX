// Centralized API configuration for HeartX
// Uses VITE_API_URL in production (e.g. Render / Vercel), falling back to local backend
export const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/+$/, '');
