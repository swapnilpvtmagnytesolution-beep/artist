import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import Cookies from 'js-cookie';
import toast from 'react-hot-toast';

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
const API_TIMEOUT = 30000; // 30 seconds

// Create axios instance
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = Cookies.get('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Add CSRF token for non-GET requests
    if (config.method !== 'get') {
      const csrfToken = Cookies.get('csrftoken');
      if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken;
      }
    }

    // Log request in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`🚀 ${config.method?.toUpperCase()} ${config.url}`, {
        data: config.data,
        params: config.params,
      });
    }

    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // Log response in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`✅ ${response.config.method?.toUpperCase()} ${response.config.url}`, {
        status: response.status,
        data: response.data,
      });
    }

    return response;
  },
  (error) => {
    // Log error in development
    if (process.env.NODE_ENV === 'development') {
      console.error(`❌ ${error.config?.method?.toUpperCase()} ${error.config?.url}`, {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message,
      });
    }

    // Handle different error types
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      
      switch (status) {
        case 400:
          // Bad Request - show validation errors
          if (data.detail) {
            toast.error(data.detail);
          } else if (data.message) {
            toast.error(data.message);
          }
          break;
          
        case 401:
          // Unauthorized - handled by auth interceptor
          break;
          
        case 403:
          // Forbidden
          toast.error('You do not have permission to perform this action');
          break;
          
        case 404:
          // Not Found
          toast.error('The requested resource was not found');
          break;
          
        case 429:
          // Too Many Requests
          toast.error('Too many requests. Please try again later.');
          break;
          
        case 500:
          // Internal Server Error
          toast.error('Internal server error. Please try again later.');
          break;
          
        case 502:
        case 503:
        case 504:
          // Server unavailable
          toast.error('Server is temporarily unavailable. Please try again later.');
          break;
          
        default:
          toast.error(`Request failed with status ${status}`);
      }
    } else if (error.request) {
      // Network error
      toast.error('Network error. Please check your connection.');
    } else {
      // Other error
      toast.error('An unexpected error occurred.');
    }

    return Promise.reject(error);
  }
);

// API Service Classes
export class AuthAPI {
  static async login(credentials: { username: string; password: string; remember_me?: boolean }) {
    const response = await apiClient.post('/auth/login/', credentials);
    return response.data;
  }

  static async logout(refreshToken: string) {
    const response = await apiClient.post('/auth/logout/', { refresh: refreshToken });
    return response.data;
  }

  static async refreshToken(refreshToken: string) {
    const response = await apiClient.post('/auth/token/refresh/', { refresh: refreshToken });
    return response.data;
  }

  static async getUser() {
    const response = await apiClient.get('/auth/user/');
    return response.data;
  }

  static async changePassword(data: {
    current_password: string;
    new_password: string;
    confirm_password: string;
  }) {
    const response = await apiClient.post('/auth/change-password/', data);
    return response.data;
  }

  static async resetPassword(email: string) {
    const response = await apiClient.post('/auth/password-reset/', { email });
    return response.data;
  }
}

export class EventsAPI {
  static async getEvents(params?: {
    page?: number;
    page_size?: number;
    search?: string;
    status?: string;
    date_from?: string;
    date_to?: string;
  }) {
    const response = await apiClient.get('/events/', { params });
    return response.data;
  }

  static async getEvent(id: string) {
    const response = await apiClient.get(`/events/${id}/`);
    return response.data;
  }

  static async createEvent(data: any) {
    const response = await apiClient.post('/events/', data);
    return response.data;
  }

  static async updateEvent(id: string, data: any) {
    const response = await apiClient.patch(`/events/${id}/`, data);
    return response.data;
  }

  static async deleteEvent(id: string) {
    const response = await apiClient.delete(`/events/${id}/`);
    return response.data;
  }

  static async getEventMedia(id: string, params?: {
    page?: number;
    page_size?: number;
    media_type?: string;
  }) {
    const response = await apiClient.get(`/events/${id}/media/`, { params });
    return response.data;
  }

  static async uploadMedia(eventId: string, files: FormData) {
    const response = await apiClient.post(`/events/${eventId}/upload/`, files, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }
}

export class UsersAPI {
  static async getUsers(params?: {
    page?: number;
    page_size?: number;
    search?: string;
    is_active?: boolean;
    is_staff?: boolean;
  }) {
    const response = await apiClient.get('/users/', { params });
    return response.data;
  }

  static async getUser(id: string) {
    const response = await apiClient.get(`/users/${id}/`);
    return response.data;
  }

  static async createUser(data: any) {
    const response = await apiClient.post('/users/', data);
    return response.data;
  }

  static async updateUser(id: string, data: any) {
    const response = await apiClient.patch(`/users/${id}/`, data);
    return response.data;
  }

  static async deleteUser(id: string) {
    const response = await apiClient.delete(`/users/${id}/`);
    return response.data;
  }
}

export class DashboardAPI {
  static async getStats() {
    const response = await apiClient.get('/dashboard/stats/');
    return response.data;
  }

  static async getEventAnalytics(eventId?: string) {
    const url = eventId ? `/dashboard/events/${eventId}/analytics/` : '/dashboard/events/analytics/';
    const response = await apiClient.get(url);
    return response.data;
  }

  static async getMediaAnalytics() {
    const response = await apiClient.get('/dashboard/media/analytics/');
    return response.data;
  }

  static async getUserAnalytics() {
    const response = await apiClient.get('/dashboard/users/analytics/');
    return response.data;
  }
}

export class SecurityAPI {
  static async getSecurityEvents(params?: {
    page?: number;
    page_size?: number;
    event_type?: string;
    severity?: string;
    resolved?: boolean;
  }) {
    const response = await apiClient.get('/security/events/', { params });
    return response.data;
  }

  static async getAuditLogs(params?: {
    page?: number;
    page_size?: number;
    action?: string;
    user?: string;
    resource_type?: string;
  }) {
    const response = await apiClient.get('/security/audit-logs/', { params });
    return response.data;
  }

  static async getIPWhitelist() {
    const response = await apiClient.get('/security/ip-whitelist/');
    return response.data;
  }

  static async addIPToWhitelist(data: {
    ip_address: string;
    description?: string;
    expires_at?: string;
  }) {
    const response = await apiClient.post('/security/ip-whitelist/', data);
    return response.data;
  }

  static async getIPBlacklist() {
    const response = await apiClient.get('/security/ip-blacklist/');
    return response.data;
  }

  static async addIPToBlacklist(data: {
    ip_address: string;
    reason: string;
    expires_at?: string;
  }) {
    const response = await apiClient.post('/security/ip-blacklist/', data);
    return response.data;
  }
}

// File upload helper
export const uploadFile = async (
  url: string,
  file: File,
  onProgress?: (progress: number) => void
) => {
  const formData = new FormData();
  formData.append('file', file);

  const config: AxiosRequestConfig = {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  };

  if (onProgress) {
    config.onUploadProgress = (progressEvent) => {
      const progress = progressEvent.total
        ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
        : 0;
      onProgress(progress);
    };
  }

  const response = await apiClient.post(url, formData, config);
  return response.data;
};

// Download file helper
export const downloadFile = async (url: string, filename?: string) => {
  const response = await apiClient.get(url, {
    responseType: 'blob',
  });

  // Create download link
  const blob = new Blob([response.data]);
  const downloadUrl = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = downloadUrl;
  link.download = filename || 'download';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(downloadUrl);
};

export default apiClient;