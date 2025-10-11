/**
 * API Client Configuration
 * Centralized axios instance with interceptors for authentication and error handling
 */

import axios from 'axios';

// Ensure the base URL always points to the API v1 prefix.
const rawBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const normalizedBase = rawBase.replace(/\/+$/, ''); // remove trailing slash
const API_BASE_URL = normalizedBase.endsWith('/api/v1') ? normalizedBase : `${normalizedBase}/api/v1`;

// Create axios instance with base configuration
// Log the resolved API base early so devs can confirm which host the frontend will call.
// This helps diagnose localhost vs deployed-backend issues (seen as ERR_BLOCKED_BY_CLIENT or 401s).
console.info('Resolved API_BASE_URL:', API_BASE_URL);
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh and errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Handle 401 Unauthorized errors
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          // Attempt to refresh the token
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token: newRefreshToken } = response.data;
          
          // Update stored tokens
          localStorage.setItem('access_token', access_token);
          if (newRefreshToken) {
            localStorage.setItem('refresh_token', newRefreshToken);
          }

          // Retry the original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return apiClient(originalRequest);
        } catch (refreshError) {
          // Refresh failed: clear tokens but do NOT redirect in prototype mode.
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          return Promise.reject(refreshError);
        }
      } else {
        // No refresh token - in dev mode avoid redirect
        // No refresh token: clear local tokens and continue (do not redirect)
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      }
    }

    // Handle other errors
    if (error.response?.status >= 500) {
      console.error('Server error:', error.response.data);
      // You could show a global error notification here
    }

    return Promise.reject(error);
  }
);

// Utility functions for common HTTP methods
// These helpers unwrap axios' response and return response.data so callers
// receive plain JSON (or blob for downloads) instead of the full AxiosResponse.
const api = {
  // GET request
  get: (url, config = {}) => apiClient.get(url, config).then((res) => res.data),

  // POST request
  post: (url, data = {}, config = {}) => apiClient.post(url, data, config).then((res) => res.data),

  // PUT request
  put: (url, data = {}, config = {}) => apiClient.put(url, data, config).then((res) => res.data),

  // PATCH request
  patch: (url, data = {}, config = {}) => apiClient.patch(url, data, config).then((res) => res.data),

  // DELETE request
  delete: (url, config = {}) => apiClient.delete(url, config).then((res) => res.data),

  // Upload file
  upload: (url, formData, config = {}) => {
    const uploadConfig = {
      ...config,
      headers: {
        ...config.headers,
        'Content-Type': 'multipart/form-data',
      },
    };
    return apiClient.post(url, formData, uploadConfig).then((res) => res.data);
  },

  // Download file
  download: (url, config = {}) => {
    const downloadConfig = {
      ...config,
      responseType: 'blob',
    };
    return apiClient.get(url, downloadConfig).then((res) => res.data);
  },

  // Set auth token manually
  setAuthToken: (token) => {
    if (token) {
      localStorage.setItem('access_token', token);
      apiClient.defaults.headers.common.Authorization = `Bearer ${token}`;
    } else {
      localStorage.removeItem('access_token');
      delete apiClient.defaults.headers.common.Authorization;
    }
  },

  // Clear auth token
  clearAuthToken: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    delete apiClient.defaults.headers.common.Authorization;
  },

  // Get stored tokens
  getTokens: () => ({
    access_token: localStorage.getItem('access_token'),
    refresh_token: localStorage.getItem('refresh_token'),
  }),

  // Check if user is authenticated
  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  },

  // Get base URL
  getBaseURL: () => API_BASE_URL,
};

export default api;
