// src/components/auth/ProtectedRoute.tsx
import React from "react";
import { Outlet, Navigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
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
    return (
      <div className="flex items-center justify-center h-screen text-red-500">
        دسترسی غیرمجاز - شما مجوز دسترسی به این صفحه را ندارید.
      </div>
    );
  }

  return <Outlet />;
};

export default ProtectedRoute;
