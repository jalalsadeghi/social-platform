// src/components/auth/ProtectedRoute.tsx
import React from "react";
import { Outlet, Navigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { Skeleton } from "@/components/ui/skeleton";

interface Props {
  module?: string; 
  action?: "read" | "create" | "update" | "delete";
}

const ProtectedRoute: React.FC<Props> = ({ module, action = "read" }) => {
  const { isAuthenticated, loading, user } = useAuth();

  if (loading) {
    return <Skeleton className="w-full h-screen" />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/auth/login" replace />;
  }

  if (module && (!user || !user.role.permissions[module]?.[action])) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
};

export default ProtectedRoute;
