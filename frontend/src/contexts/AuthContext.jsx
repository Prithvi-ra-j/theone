
import { createContext, useContext, useState, useEffect } from "react";
import authAPI from "../api/auth";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('user');
    return savedUser ? JSON.parse(savedUser) : null;
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
    setLoading(true);
    try {
      // Call backend login API
      const res = await authAPI.login({ email, password });
      // Store tokens
      localStorage.setItem("access_token", res.access_token);
      if (res.refresh_token) {
        localStorage.setItem("refresh_token", res.refresh_token);
      }
      // Fetch user profile
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
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
