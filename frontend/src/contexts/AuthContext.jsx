
import { createContext, useContext, useState, useEffect } from "react";
import authAPI from "../api/auth";
import { env } from 'process';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) return JSON.parse(savedUser);
    // In dev, optionally provide a demo user to avoid auth flow
    try {
      if (process.env.REACT_APP_DEV_DISABLE_AUTH === '1' || process.env.REACT_APP_DEV_DISABLE_AUTH === 'true') {
        return { id: 1, email: process.env.REACT_APP_DEV_DEMO_EMAIL || 'demo@example.com', name: 'Demo User' };
      }
    } catch (e) {
      // ignore
    }
    return null;
  });
  const [loading, setLoading] = useState(false);

  // Save user to localStorage whenever it changes
  useEffect(() => {
    if (user) {
      localStorage.setItem('user', JSON.stringify(user));
    } else {
      localStorage.removeItem('user');
    }
  }, [user]);


  const login = async ({ email, password }) => {
    // No-op in prototype mode; if not in prototype mode, call real API
    setLoading(true);
    try {
      if (process.env.REACT_APP_DEV_DISABLE_AUTH === '1' || process.env.REACT_APP_DEV_DISABLE_AUTH === 'true') {
        setUser({ id: 1, email: email || process.env.REACT_APP_DEV_DEMO_EMAIL || 'demo@example.com', name: 'Demo User' });
        setLoading(false);
        return true;
      }
      const res = await authAPI.login({ email, password });
      localStorage.setItem("access_token", res.access_token);
      if (res.refresh_token) localStorage.setItem("refresh_token", res.refresh_token);
      const profile = await authAPI.getCurrentUserProfile();
      setUser(profile);
      setLoading(false);
      return true;
    } catch (error) {
      setLoading(false);
      return false;
    }
  };

  const register = ({ name, email, password }) => {
    // In a real app, this would call an API to register the user
    setLoading(true);
    try {
      // Simulate API call delay
      setTimeout(() => {
        // For demo purposes, we'll just create a new user
        const userData = { email, name };
        setUser(userData);
        setLoading(false);
      }, 1000);
      return true;
    } catch (error) {
      console.error("Registration error:", error);
      setLoading(false);
      return false;
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
