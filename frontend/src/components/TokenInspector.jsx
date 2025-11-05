import React from "react";
import jwtDecode from "jwt-decode";
import { useAuth } from "../context/AuthContext.jsx";

export default function TokenInspector() {
  const { token } = useAuth();
  if (!token) return <p className="text-sm text-slate-500">No token available.</p>;

  let decoded;
  try {
    decoded = jwtDecode(token);
  } catch (err) {
    return <p className="text-sm text-red-500">Error decoding token: {err.message}</p>;
  }

  const expiryDate = new Date(decoded.exp * 1000).toLocaleString();

  return (
    <div className="mt-6 rounded-lg bg-slate-100 p-4 text-sm text-slate-800 shadow">
      <h3 className="text-lg font-semibold text-slate-900">🔍 Token Inspector</h3>
      <pre className="mt-3 whitespace-pre-wrap break-words text-xs text-slate-700">
        {JSON.stringify(decoded, null, 2)}
      </pre>
      <p className="mt-3 text-emerald-600">⏰ Token expires on: {expiryDate}</p>
    </div>
  );
}
