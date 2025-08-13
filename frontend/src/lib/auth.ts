'use client';

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  date_joined: string;
  is_staff: boolean;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
}

// Get authentication state from localStorage
export const getAuthState = (): AuthState => {
  if (typeof window === 'undefined') {
    return { user: null, token: null, isAuthenticated: false };
  }

  const token = localStorage.getItem('token');
  const userStr = localStorage.getItem('user');
  
  if (token && userStr) {
    try {
      const user = JSON.parse(userStr);
      return { user, token, isAuthenticated: true };
    } catch (error) {
      // Clear invalid data
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
  }
  
  return { user: null, token: null, isAuthenticated: false };
};

// Set authentication state
export const setAuthState = (user: User, token: string): void => {
  localStorage.setItem('token', token);
  localStorage.setItem('user', JSON.stringify(user));
};

// Clear authentication state
export const clearAuthState = (): void => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
};

// Make authenticated API requests
export const authenticatedFetch = async (url: string, options: RequestInit = {}): Promise<Response> => {
  const { token } = getAuthState();
  
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Token ${token}` }),
    ...options.headers,
  };

  return fetch(url, {
    ...options,
    headers,
  });
};

// Logout function
export const logout = async (): Promise<void> => {
  const { token } = getAuthState();
  
  if (token) {
    try {
      await authenticatedFetch('http://localhost:8000/api/auth/logout/', {
        method: 'POST',
      });
    } catch (error) {
      console.error('Logout error:', error);
    }
  }
  
  clearAuthState();
  
  // Redirect to login page
  if (typeof window !== 'undefined') {
    window.location.href = '/auth/login';
  }
};

// Check if user is authenticated
export const isAuthenticated = (): boolean => {
  return getAuthState().isAuthenticated;
};

// Get current user
export const getCurrentUser = (): User | null => {
  return getAuthState().user;
};

// Get auth token
export const getAuthToken = (): string | null => {
  return getAuthState().token;
};

// Validate token with backend
export const validateToken = async (): Promise<boolean> => {
  const { token } = getAuthState();
  
  if (!token) return false;
  
  try {
    const response = await authenticatedFetch('http://localhost:8000/api/auth/profile/');
    return response.ok;
  } catch (error) {
    return false;
  }
};

// Refresh user data
export const refreshUserData = async (): Promise<User | null> => {
  try {
    const response = await authenticatedFetch('http://localhost:8000/api/auth/profile/');
    
    if (response.ok) {
      const user = await response.json();
      const { token } = getAuthState();
      if (token) {
        setAuthState(user, token);
      }
      return user;
    }
  } catch (error) {
    console.error('Failed to refresh user data:', error);
  }
  
  return null;
};

// Get user statistics
export const getUserStats = async () => {
  try {
    const response = await authenticatedFetch('http://localhost:8000/api/auth/stats/');
    
    if (response.ok) {
      return await response.json();
    }
  } catch (error) {
    console.error('Failed to get user stats:', error);
  }
  
  return null;
};