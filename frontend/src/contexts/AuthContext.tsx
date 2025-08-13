'use client';

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { User, AuthState, getAuthState, clearAuthState, validateToken } from '@/lib/auth';

interface AuthContextType extends AuthState {
  login: (user: User, token: string) => void;
  logout: () => void;
  loading: boolean;
  refreshAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    token: null,
    isAuthenticated: false,
  });
  const [loading, setLoading] = useState(true);

  // Initialize auth state from localStorage
  useEffect(() => {
    const initializeAuth = async () => {
      const storedAuthState = getAuthState();
      
      if (storedAuthState.isAuthenticated) {
        // Validate token with backend
        const isValid = await validateToken();
        
        if (isValid) {
          setAuthState(storedAuthState);
        } else {
          // Token is invalid, clear auth state
          clearAuthState();
          setAuthState({ user: null, token: null, isAuthenticated: false });
        }
      }
      
      setLoading(false);
    };

    initializeAuth();
  }, []);

  const login = (user: User, token: string) => {
    const newAuthState = { user, token, isAuthenticated: true };
    setAuthState(newAuthState);
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
  };

  const logout = () => {
    setAuthState({ user: null, token: null, isAuthenticated: false });
    clearAuthState();
  };

  const refreshAuth = async () => {
    const storedAuthState = getAuthState();
    
    if (storedAuthState.isAuthenticated) {
      const isValid = await validateToken();
      
      if (isValid) {
        setAuthState(storedAuthState);
      } else {
        logout();
      }
    }
  };

  const value: AuthContextType = {
    ...authState,
    login,
    logout,
    loading,
    refreshAuth,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;