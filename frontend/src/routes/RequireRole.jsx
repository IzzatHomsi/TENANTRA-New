import { Navigate } from "react-router-dom";
import { getToken } from "../lib/auth";
import { hasRole } from "../utils/roleUtils.js";

export default function RequireRole({ role, children }){
  const token = getToken();
  if(!token) return <Navigate to="/login" replace />;
  if(!hasRole(role)) return <Navigate to="/app/dashboard" replace />;
  return children;
}
