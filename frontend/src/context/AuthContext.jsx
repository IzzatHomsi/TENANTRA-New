import { getApiBase } from "../utils/apiBase";
// src/context/AuthContext.jsx
import React, {
  createContext, useCallback, useContext, useEffect, useMemo, useState,
} from "react";
import { normalizeRole, deriveRoleFromUser } from "../utils/rbac.js"; // ⬅️ NEW

const AuthContext = createContext(null);

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth() must be used within <AuthProvider>.");
  return ctx;
}

async function safeErrorMessage(res) {
  try {
    const t = await res.text();
    try {
      const j = JSON.parse(t);
      return j?.detail || j?.message || t || `HTTP ${res.status}`;
    } catch {
      return t || `HTTP ${res.status}`;
    }
  } catch {
    return `HTTP ${res.status}`;
  }
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);
  const [role, setRole] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const API_BASE = getApiBase();

  // Restore from localStorage (optimistic)
  useEffect(() => {
    try {
      const savedToken = localStorage.getItem("token");
      if (savedToken) setToken(savedToken);
    } finally {
      // /auth/me will validate if token exists
    }
  }, []);

  // Bootstrap via /auth/me if we have a token
  useEffect(() => {
    if (!token) {
      setIsLoading(false);
      return;
    }
    (async () => {
      try {
        const res = await fetch(`${API_BASE}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) throw new Error(await safeErrorMessage(res));
        const me = await res.json();
        const nextUser = me.user || me;
        // ⬇️ derive role, then normalize
        const derived =
          normalizeRole(me.role ?? deriveRoleFromUser(nextUser) ?? role ?? "standard_user");

        setUser(nextUser);
        setRole(derived);
      } catch {
        localStorage.removeItem("token");
        setToken(null);
        setUser(null);
        setRole(null);
      } finally {
        setIsLoading(false);
      }
    })();
  }, [token, API_BASE]); // eslint-disable-line react-hooks/exhaustive-deps

  const signIn = useCallback(
    async ({ username, password }) => {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ username, password }),
      });
      if (!res.ok) throw new Error((await safeErrorMessage(res)) || "Login failed");

      const data = await res.json();
      const accessToken = data.access_token;
      if (!accessToken) throw new Error("Login response missing access_token");

      const userObj = data.user || null;
      // ⬇️ derive & normalize role from response or user object
      const derived = normalizeRole(
        data.role ?? deriveRoleFromUser(userObj) ?? "standard_user"
      );

      localStorage.setItem("token", accessToken);

      setToken(accessToken);
      setUser(userObj);
      setRole(derived);

      return { token: accessToken, user: userObj, role: derived };
    },
    [API_BASE]
  );

  const signOut = useCallback(() => {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
    setRole(null);
  }, []);

  const value = useMemo(
    () => ({
      token,
      user,
      role, // already normalized
      isLoading,
      isAuthenticated: Boolean(token),
      signIn,
      signOut,
    }),
    [token, user, role, isLoading, signIn, signOut]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

