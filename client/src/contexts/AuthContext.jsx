import { createContext, useState, useContext, useEffect } from 'react';
import axiosInstance from '../Helper/axiosInstance';

const AuthContext = createContext();

export const useAuth = () => {
  return useContext(AuthContext);
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const accessToken = localStorage.getItem('access_token');
    const role = localStorage.getItem('role');
    const username = localStorage.getItem('username');
    
    if (accessToken) {
      setUser({
        role: role || 'USER',
        name: username || 'User',
      });
      setIsAuthenticated(true);
    }
    
    setLoading(false);

    // Listen for storage events (for multi-tab login/logout)
    const handleStorageChange = () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        setUser({
          role: localStorage.getItem('role') || 'USER',
          name: localStorage.getItem('username') || 'User',
        });
        setIsAuthenticated(true);
      } else {
        setUser(null);
        setIsAuthenticated(false);
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const login = async (email, password) => {
    try {
      const response = await axiosInstance.post('/auth/login', { email, password });
      const { access_token, refresh_token, role, username } = response.data;
      
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      localStorage.setItem('role', role);
      localStorage.setItem('username', username);
      
      setUser({
        role: role || 'USER',
        name: username || 'User',
      });
      
      setIsAuthenticated(true);
      window.dispatchEvent(new Event('storage'));
      return true;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('role');
    localStorage.removeItem('username');
    
    setUser(null);
    setIsAuthenticated(false);
    window.dispatchEvent(new Event('storage'));
  };

  const value = {
    user,
    isAuthenticated,
    loading,
    login,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Provide default export to keep exports consistent for Vite React plugin
export default AuthProvider; 