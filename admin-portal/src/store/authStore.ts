import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import Cookies from 'js-cookie';
import { apiClient } from '@/services/apiClient';
import toast from 'react-hot-toast';

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_staff: boolean;
  is_superuser: boolean;
  is_active: boolean;
  date_joined: string;
  last_login: string | null;
  profile_picture?: string;
  role?: string;
  permissions?: string[];
}

export interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface AuthActions {
  login: (credentials: LoginCredentials) => Promise<boolean>;
  logout: () => Promise<void>;
  refreshAccessToken: () => Promise<boolean>;
  updateUser: (userData: Partial<User>) => void;
  clearError: () => void;
  checkAuth: () => Promise<boolean>;
  changePassword: (data: ChangePasswordData) => Promise<boolean>;
}

export interface LoginCredentials {
  username: string;
  password: string;
  remember_me?: boolean;
}

export interface ChangePasswordData {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

type AuthStore = AuthState & AuthActions;

const initialState: AuthState = {
  user: null,
  token: null,
  refreshToken: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
};

export const useAuthStore = create<AuthStore>()(persist(
    (set, get) => ({
      ...initialState,

      login: async (credentials: LoginCredentials) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await apiClient.post('/auth/login/', credentials);
          const { access, refresh, user } = response.data;

          // Store tokens
          const tokenExpiry = credentials.remember_me ? 30 : 1; // 30 days or 1 day
          Cookies.set('access_token', access, { expires: tokenExpiry });
          Cookies.set('refresh_token', refresh, { expires: 30 }); // Refresh token always 30 days

          // Update state
          set({
            user,
            token: access,
            refreshToken: refresh,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });

          // Set default authorization header
          apiClient.defaults.headers.common['Authorization'] = `Bearer ${access}`;

          toast.success(`Welcome back, ${user.first_name || user.username}!`);
          return true;
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || 
                              error.response?.data?.message || 
                              'Login failed. Please check your credentials.';
          
          set({ 
            isLoading: false, 
            error: errorMessage,
            isAuthenticated: false,
            user: null,
            token: null,
            refreshToken: null,
          });
          
          toast.error(errorMessage);
          return false;
        }
      },

      logout: async () => {
        set({ isLoading: true });
        
        try {
          const { refreshToken } = get();
          
          // Call logout endpoint if refresh token exists
          if (refreshToken) {
            await apiClient.post('/auth/logout/', {
              refresh: refreshToken
            });
          }
        } catch (error) {
          // Ignore logout errors, still proceed with local logout
          console.warn('Logout API call failed:', error);
        } finally {
          // Clear tokens and state
          Cookies.remove('access_token');
          Cookies.remove('refresh_token');
          delete apiClient.defaults.headers.common['Authorization'];
          
          set({
            ...initialState,
            isLoading: false,
          });
          
          toast.success('Logged out successfully');
        }
      },

      refreshAccessToken: async () => {
        const { refreshToken } = get();
        
        if (!refreshToken) {
          return false;
        }

        try {
          const response = await apiClient.post('/auth/token/refresh/', {
            refresh: refreshToken
          });
          
          const { access } = response.data;
          
          // Update token
          Cookies.set('access_token', access, { expires: 1 });
          apiClient.defaults.headers.common['Authorization'] = `Bearer ${access}`;
          
          set({ token: access });
          
          return true;
        } catch (error) {
          // Refresh failed, logout user
          get().logout();
          return false;
        }
      },

      updateUser: (userData: Partial<User>) => {
        const { user } = get();
        if (user) {
          set({ user: { ...user, ...userData } });
        }
      },

      clearError: () => {
        set({ error: null });
      },

      checkAuth: async () => {
        const token = Cookies.get('access_token');
        const refreshToken = Cookies.get('refresh_token');
        
        if (!token && !refreshToken) {
          return false;
        }

        if (token) {
          // Set authorization header
          apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          
          try {
            // Verify token by fetching user profile
            const response = await apiClient.get('/auth/user/');
            
            set({
              user: response.data,
              token,
              refreshToken,
              isAuthenticated: true,
            });
            
            return true;
          } catch (error) {
            // Token might be expired, try refresh
            if (refreshToken) {
              return await get().refreshAccessToken();
            }
          }
        } else if (refreshToken) {
          // No access token but have refresh token
          return await get().refreshAccessToken();
        }
        
        return false;
      },

      changePassword: async (data: ChangePasswordData) => {
        set({ isLoading: true, error: null });
        
        try {
          await apiClient.post('/auth/change-password/', data);
          
          set({ isLoading: false });
          toast.success('Password changed successfully');
          return true;
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || 
                              error.response?.data?.message || 
                              'Failed to change password';
          
          set({ isLoading: false, error: errorMessage });
          toast.error(errorMessage);
          return false;
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// Setup axios interceptor for automatic token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const authStore = useAuthStore.getState();
      const success = await authStore.refreshAccessToken();
      
      if (success) {
        // Retry the original request with new token
        const newToken = useAuthStore.getState().token;
        originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
        return apiClient(originalRequest);
      } else {
        // Refresh failed, redirect to login
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// Initialize auth on app start
if (typeof window !== 'undefined') {
  useAuthStore.getState().checkAuth();
}