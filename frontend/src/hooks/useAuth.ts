// src/hooks/useAuth.ts
import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import api from "@/services/api";

interface User {
  id: string;
  username: string;
  email?: string;
  full_name?: string;
  profile_picture?: string;
}

interface UseAuth {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

export function useAuth(): UseAuth {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const navigate = useNavigate();

  const fetchUser = useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.get<User>("/auth/me");
      setUser(response.data);
      setIsAuthenticated(true);
    } catch (error: any) {
      if (error.response && error.response.status === 401) {
        setUser(null);
        setIsAuthenticated(false);
        navigate("/auth/login"); 
      } else {
        setUser(null);
        setIsAuthenticated(false);
      }
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  const login = useCallback(async (email: string, password: string) => {
    setLoading(true);
    try {
      await api.post("/auth/login", { email, password });
      await fetchUser(); 
      navigate("/dashboard");
    } catch (error) {
      setUser(null);
      setIsAuthenticated(false);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [fetchUser]);

  const logout = useCallback(async () => {
    setLoading(true);
    try {
      await api.post("/auth/logout");
    } finally {
      setUser(null);
      setIsAuthenticated(false);
      setLoading(false);
      navigate("/auth/login");
    }
  }, [navigate]);

  return {
    user,
    isAuthenticated,
    loading,
    login,
    logout,
  };
}
