// src/routes/PrivateRoute.jsx
import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import { isAdminRole } from "../utils/rbac.js"; // ⬅️ NEW

export function PrivateRoute({ children, requireAdmin = false }) {
  const location = useLocation();
  const { isLoading, isAuthenticated, role } = useAuth();

  if (isLoading) {
    return <div style={{ padding: 16 }}>Loading...</div>;
  }
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  if (requireAdmin && !isAdminRole(role)) {
    // Not an admin → bounce to dashboard
    return <Navigate to="/dashboard" replace />;
  }
  return children;
}
