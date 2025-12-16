import { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  // Configuration axios avec le token
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      // Récupérer les infos utilisateur
      fetchUser();
    } else {
      delete axios.defaults.headers.common['Authorization'];
      setLoading(false);
    }
  }, [token]);

  const fetchUser = async () => {
    try {
      // Par défaut en production le frontend proxy les requêtes vers /api
      const apiUrl = import.meta.env.VITE_API_URL || '/api';
      const response = await axios.get(`${apiUrl}/auth/me`);
      setUser(response.data);
    } catch (error) {
      console.error('Erreur récupération utilisateur:', error);
      // Token invalide ou expiré
      logout();
    } finally {
      setLoading(false);
    }
  };

  const register = async (email, password) => {
    const apiUrl = import.meta.env.VITE_API_URL || '/api';
    const response = await axios.post(`${apiUrl}/auth/register`, {
      email,
      password
    });
    
    const { access_token, user: userData } = response.data;
    
    // Sauvegarder le token
    localStorage.setItem('token', access_token);
    setToken(access_token);
    setUser(userData);
    
    return userData;
  };

  const login = async (email, password) => {
    const apiUrl = import.meta.env.VITE_API_URL || '/api';
    const response = await axios.post(`${apiUrl}/auth/login`, {
      email,
      password
    });
    
    const { access_token, user: userData } = response.data;
    
    // Sauvegarder le token
    localStorage.setItem('token', access_token);
    setToken(access_token);
    setUser(userData);
    
    return userData;
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    delete axios.defaults.headers.common['Authorization'];
  };

  const value = {
    user,
    token,
    loading,
    isAuthenticated: !!user,
    register,
    login,
    logout,
    refreshUser: fetchUser
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth doit être utilisé dans un AuthProvider');
  }
  return context;
};
