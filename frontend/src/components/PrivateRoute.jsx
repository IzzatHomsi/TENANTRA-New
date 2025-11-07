// Filename: frontend/src/components/PrivateRoute.jsx
// Purpose: Guard routes based on authentication (token) and optional admin role.
// Contract:
//   <Route element={<PrivateRoute/>}> ... </Route>
//   <Route element={<PrivateRoute requireAdmin/>}> ... </Route>
import React from "react";
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import { isAdminRole } from "../utils/rbac.js";

export default function PrivateRoute({ requireAdmin = false }) {
  const { token, role } = useAuth();

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  if (requireAdmin && !isAdminRole(role)) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}
