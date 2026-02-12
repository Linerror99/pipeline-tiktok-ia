import { useState, useEffect } from 'react';

export interface User {
  id: string;
  name: string;
  email: string;
  avatar: string;
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate checking local storage
    const storedUser = localStorage.getItem('cinema_user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  const login = async (email: string) => {
    setLoading(true);
    // Mock login delay
    await new Promise((resolve) => setTimeout(resolve, 1000));

    const mockUser: User = {
      id: '1',
      name: 'Director Smith',
      email,
      avatar:
      'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?q=80&w=100&auto=format&fit=crop'
    };

    setUser(mockUser);
    localStorage.setItem('cinema_user', JSON.stringify(mockUser));
    setLoading(false);
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('cinema_user');
  };

  return { user, loading, login, logout };
}