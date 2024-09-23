import React, { createContext, ReactNode, useEffect, useState } from 'react';
import axios from './axiosConfig';

interface User {
  user_id: string;
  display_name: string;
  picture_url: string;
  status_message: string;
}

interface AuthContextType {
  authenticated: boolean;
  user: User | null;
  login: () => void;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextType>({
  authenticated: false,
  user: null,
  login: () => {},
  logout: () => {},
});

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [authenticated, setAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);

  const fetchUser = async () => {
    try {
      console.log('Fetching user...');
      const response = await axios.get('/api/user');
      console.log('User response:', response);
      if (response.status === 200 && response.data.authenticated) {
        setAuthenticated(true);
        setUser(response.data.user);
        console.log('User authenticated:', response.data.user);
      } else {
        setAuthenticated(false);
        setUser(null);
        console.log('User not authenticated');
      }
    } catch (error) {
      setAuthenticated(false);
      setUser(null);
      console.error('Error fetching user:', error);
    }
  };

  useEffect(() => {
    fetchUser();
  }, []);

  const login = () => {
    console.log('Redirecting to LINE Login...');
    window.location.href = 'http://localhost:5000/auth/line'; // 后端登录端点
  };

  const logout = async () => {
    try {
      await axios.post('/api/logout');
      setAuthenticated(false);
      setUser(null);
      console.log('User logged out.');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <AuthContext.Provider value={{ authenticated, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
