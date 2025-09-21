import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { User } from '../types';
import { userApi } from '../services/api';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (user: User) => void;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing session on app start
    const checkExistingSession = async () => {
      const userId = localStorage.getItem('userId');
      if (userId) {
        try {
          const userData = await userApi.getUser(parseInt(userId));
          setUser(userData);
        } catch (error) {
          // If user doesn't exist anymore, clear the session
          localStorage.removeItem('userId');
          console.error('Failed to restore user session:', error);
        }
      }
      setIsLoading(false);
    };

    checkExistingSession();
  }, []);

  const login = (userData: User) => {
    setUser(userData);
    localStorage.setItem('userId', userData.id.toString());
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('userId');
  };

  const value: AuthContextType = {
    user,
    isLoading,
    login,
    logout,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};