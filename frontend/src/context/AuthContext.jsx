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
  const [token, setToken] = useState(() => {
    try {
      return localStorage.getItem("token");
    } catch {
      return null;
    }
  });
  const [user, setUser] = useState(() => {
    try {
      const raw = localStorage.getItem("user");
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  });
  const [role, setRole] = useState(() => {
    try {
      const stored = localStorage.getItem("role");
      if (stored) {
        return stored;
      }
      const raw = localStorage.getItem("user");
      if (raw) {
        return normalizeRole(deriveRoleFromUser(JSON.parse(raw)) ?? "standard_user");
      }
    } catch {
      return null;
    }
    return null;
  });
  const [isLoading, setIsLoading] = useState(true);

  const API_BASE = getApiBase();

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
        try {
          localStorage.setItem("user", JSON.stringify(nextUser));
          localStorage.setItem("role", derived);
        } catch {
          /* ignore */
        }
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
      try {
        localStorage.setItem("user", JSON.stringify(userObj || null));
        localStorage.setItem("role", derived);
      } catch {
        /* ignore */
      }

      setToken(accessToken);
      setUser(userObj);
      setRole(derived);

      return { token: accessToken, user: userObj, role: derived };
    },
    [API_BASE]
  );

  const signOut = useCallback(() => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    localStorage.removeItem("role");
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

