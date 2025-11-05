import { jsx } from "react/jsx-runtime";
import { createContext, useContext, useState, useEffect, useCallback, useMemo, lazy, Suspense } from "react";
import { useLocation, Navigate, useRoutes, matchRoutes } from "react-router-dom";
import { QueryClientProvider, QueryClient, useQuery } from "@tanstack/react-query";
import { StaticRouter } from "react-router-dom/server.mjs";
function getApiBase() {
  const raw = "/api".toString().trim();
  if (/^https?:\/\//i.test(raw)) {
    return raw.replace(/\/+$/, "");
  }
  const path = raw.startsWith("/") ? raw : `/${raw}`;
  if (typeof window !== "undefined" && window.location?.origin) {
    return `${window.location.origin}${path}`.replace(/\/+$/, "");
  }
  return path.replace(/\/+$/, "") || "/api";
}
function normalizeRole(role) {
  return (role ?? "").toString().trim().toLowerCase().replace(/^role[_:\s-]*/, "").replace(/\s+/g, "_");
}
const ADMIN_SET = /* @__PURE__ */ new Set([
  "admin",
  "administrator",
  "super_admin",
  "system_admin",
  "sysadmin",
  "root"
]);
function isAdminRole(role) {
  return ADMIN_SET.has(normalizeRole(role));
}
function deriveRoleFromUser(userLike) {
  if (!userLike) return null;
  const r = userLike.role ?? userLike.role_name ?? userLike.roleKey ?? userLike.roleType ?? null;
  return r ? normalizeRole(r) : null;
}
const AuthContext = createContext(null);
function useAuth() {
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
function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);
  const [role, setRole] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const API_BASE = getApiBase();
  useEffect(() => {
    try {
      const savedToken = localStorage.getItem("token");
      if (savedToken) setToken(savedToken);
    } finally {
    }
  }, []);
  useEffect(() => {
    if (!token) {
      setIsLoading(false);
      return;
    }
    (async () => {
      try {
        const res = await fetch(`${API_BASE}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (!res.ok) throw new Error(await safeErrorMessage(res));
        const me = await res.json();
        const nextUser = me.user || me;
        const derived = normalizeRole(me.role ?? deriveRoleFromUser(nextUser) ?? role ?? "standard_user");
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
  }, [token, API_BASE]);
  const signIn = useCallback(
    async ({ username, password }) => {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ username, password })
      });
      if (!res.ok) throw new Error(await safeErrorMessage(res) || "Login failed");
      const data = await res.json();
      const accessToken = data.access_token;
      if (!accessToken) throw new Error("Login response missing access_token");
      const userObj = data.user || null;
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
      role,
      // already normalized
      isLoading,
      isAuthenticated: Boolean(token),
      signIn,
      signOut
    }),
    [token, user, role, isLoading, signIn, signOut]
  );
  return /* @__PURE__ */ jsx(AuthContext.Provider, { value, children });
}
function PrivateRoute({ children, requireAdmin = false }) {
  const location = useLocation();
  const { isLoading, isAuthenticated, role } = useAuth();
  if (isLoading) {
    return /* @__PURE__ */ jsx("div", { style: { padding: 16 }, children: "Loading..." });
  }
  if (!isAuthenticated) {
    return /* @__PURE__ */ jsx(Navigate, { to: "/login", state: { from: location }, replace: true });
  }
  if (requireAdmin && !isAdminRole(role)) {
    return /* @__PURE__ */ jsx(Navigate, { to: "/app/dashboard", replace: true });
  }
  return children;
}
const Landing = lazy(() => import("./assets/Landing-CrXokz_X.js"));
const Login = lazy(() => import("./assets/Login-DQtsHhID.js"));
const Dashboard = lazy(() => import("./assets/Dashboard-CNOko9Jd.js"));
const Users = lazy(() => import("./assets/Users-CDMMtKcv.js"));
const Profile = lazy(() => import("./assets/Profile-DsAhSA4v.js"));
const ComplianceTrends = lazy(() => import("./assets/ComplianceTrends-DHrcXDeK.js"));
const Notifications = lazy(() => import("./assets/Notifications-DxYiG2_C.js"));
const Persistence = lazy(() => import("./assets/Persistence-D1zPDAGP.js"));
const ProcessMonitoring = lazy(() => import("./assets/ProcessMonitoring-UfZSuuxE.js"));
const Integrity = lazy(() => import("./assets/Integrity-a0QlXV5U.js"));
const ThreatIntel = lazy(() => import("./assets/ThreatIntel-XK7baGPH.js"));
const ComplianceMatrix = lazy(() => import("./assets/ComplianceMatrix-DETvzAk9.js"));
const RetentionExports = lazy(() => import("./assets/RetentionExports-Djiz442Z.js"));
const Billing = lazy(() => import("./assets/Billing-DBshk0DV.js"));
const ScanOrchestration = lazy(() => import("./assets/ScanOrchestration-CXbsk3LB.js"));
const NotificationHistory = lazy(() => import("./assets/NotificationHistory-BzDqGlOM.js"));
const ModuleCatalog = lazy(() => import("./assets/ModuleCatalog-DHcWY8F7.js"));
const CloudDiscovery = lazy(() => import("./assets/CloudDiscovery-85ipAa8g.js"));
const Discovery = lazy(() => import("./assets/Discovery-CuWE_oHq.js"));
const Onboarding = lazy(() => import("./assets/Onboarding-DMnBNYfp.js"));
const FeatureFlags = lazy(() => import("./assets/FeatureFlags-DRoRVQip.js"));
const AlertSettings = lazy(() => import("./assets/AlertSettings-CHaGdiai.js"));
const ObservabilitySetup = lazy(() => import("./assets/ObservabilitySetup-DNn8HApr.js"));
const Metrics = lazy(() => import("./assets/Metrics-BvOTSv0m.js"));
const FAQ = lazy(() => import("./assets/FAQ-C88yxBoP.js"));
const AuditLogs = lazy(() => import("./assets/AuditLogs-DkvBVJxc.js"));
const Search = lazy(() => import("./assets/Search-GcN8-b_x.js"));
const ShellLayout = lazy(() => import("./assets/Shell-CDIByGrg.js"));
const AdminSettings = lazy(() => import("./assets/AdminSettings-5YnJ_579.js"));
const routeConfig = [
  {
    path: "/",
    element: /* @__PURE__ */ jsx(Landing, {})
  },
  {
    path: "/login",
    element: /* @__PURE__ */ jsx(Login, {})
  },
  {
    path: "/app",
    element: /* @__PURE__ */ jsx(PrivateRoute, { children: /* @__PURE__ */ jsx(ShellLayout, {}) }),
    children: [
      { index: true, element: /* @__PURE__ */ jsx(Navigate, { to: "dashboard", replace: true }) },
      { path: "dashboard", element: /* @__PURE__ */ jsx(Dashboard, {}) },
      { path: "profile", element: /* @__PURE__ */ jsx(Profile, {}) },
      { path: "compliance-trends", element: /* @__PURE__ */ jsx(ComplianceTrends, {}) },
      { path: "compliance-matrix", element: /* @__PURE__ */ jsx(ComplianceMatrix, {}) },
      { path: "notifications", element: /* @__PURE__ */ jsx(Notifications, {}) },
      { path: "metrics", element: /* @__PURE__ */ jsx(Metrics, {}) },
      { path: "persistence", element: /* @__PURE__ */ jsx(Persistence, {}) },
      { path: "process-monitoring", element: /* @__PURE__ */ jsx(ProcessMonitoring, {}) },
      { path: "integrity", element: /* @__PURE__ */ jsx(Integrity, {}) },
      {
        path: "threat-intel",
        element: /* @__PURE__ */ jsx(PrivateRoute, { requireAdmin: true, children: /* @__PURE__ */ jsx(ThreatIntel, {}) })
      },
      { path: "retention", element: /* @__PURE__ */ jsx(RetentionExports, {}) },
      { path: "billing", element: /* @__PURE__ */ jsx(Billing, {}) },
      { path: "scans", element: /* @__PURE__ */ jsx(ScanOrchestration, {}) },
      { path: "modules", element: /* @__PURE__ */ jsx(ModuleCatalog, {}) },
      { path: "notification-history", element: /* @__PURE__ */ jsx(NotificationHistory, {}) },
      { path: "cloud", element: /* @__PURE__ */ jsx(CloudDiscovery, {}) },
      { path: "discovery", element: /* @__PURE__ */ jsx(Discovery, {}) },
      { path: "search", element: /* @__PURE__ */ jsx(Search, {}) },
      { path: "onboarding", element: /* @__PURE__ */ jsx(Onboarding, {}) },
      {
        path: "faq",
        element: /* @__PURE__ */ jsx(PrivateRoute, { children: /* @__PURE__ */ jsx(FAQ, {}) })
      },
      {
        path: "observability-setup",
        element: /* @__PURE__ */ jsx(PrivateRoute, { requireAdmin: true, children: /* @__PURE__ */ jsx(ObservabilitySetup, {}) })
      },
      {
        path: "users",
        element: /* @__PURE__ */ jsx(PrivateRoute, { requireAdmin: true, children: /* @__PURE__ */ jsx(Users, {}) })
      },
      {
        path: "admin-settings",
        element: /* @__PURE__ */ jsx(PrivateRoute, { requireAdmin: true, children: /* @__PURE__ */ jsx(AdminSettings, {}) })
      },
      {
        path: "feature-flags",
        element: /* @__PURE__ */ jsx(PrivateRoute, { requireAdmin: true, children: /* @__PURE__ */ jsx(FeatureFlags, {}) })
      },
      {
        path: "alert-settings",
        element: /* @__PURE__ */ jsx(PrivateRoute, { requireAdmin: true, children: /* @__PURE__ */ jsx(AlertSettings, {}) })
      },
      {
        path: "audit-logs",
        element: /* @__PURE__ */ jsx(PrivateRoute, { requireAdmin: true, children: /* @__PURE__ */ jsx(AuditLogs, {}) })
      }
    ]
  },
  {
    path: "*",
    element: /* @__PURE__ */ jsx(Navigate, { to: "/", replace: true })
  }
];
const fallback = /* @__PURE__ */ jsx("div", { className: "p-8 text-center text-gray-500", children: "Loading..." });
function App() {
  const element = useRoutes(routeConfig);
  return /* @__PURE__ */ jsx(Suspense, { fallback, children: element });
}
const THEME_STORAGE_KEY = "tena_theme";
const ThemeContext = createContext(null);
function readStoredTheme() {
  if (typeof window === "undefined") return "system";
  try {
    let stored = localStorage.getItem(THEME_STORAGE_KEY);
    if (!stored) {
      const legacy = localStorage.getItem("tenat_theme");
      if (legacy) {
        stored = legacy;
        localStorage.setItem(THEME_STORAGE_KEY, legacy);
        localStorage.removeItem("tenat_theme");
      }
    }
    return stored === "light" || stored === "dark" || stored === "system" ? stored : "system";
  } catch {
    return "system";
  }
}
function applyColorScheme(mode) {
  if (typeof document === "undefined") {
    return;
  }
  const isDark = mode === "dark";
  const root = document.documentElement;
  root.classList.toggle("dark", isDark);
  root.setAttribute("data-theme", mode);
  root.style.setProperty("color-scheme", isDark ? "dark" : "light");
}
function ThemeProvider({ children }) {
  const [theme, setThemeState] = useState(() => readStoredTheme());
  const [resolvedTheme, setResolvedTheme] = useState("light");
  const updateResolvedTheme = useCallback(
    (nextTheme) => {
      const prefersDark = typeof window !== "undefined" && window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
      const resolved = nextTheme === "system" ? prefersDark ? "dark" : "light" : nextTheme;
      setResolvedTheme(resolved);
      applyColorScheme(resolved);
    },
    []
  );
  useEffect(() => {
    updateResolvedTheme(theme);
    try {
      localStorage.setItem(THEME_STORAGE_KEY, theme);
    } catch {
    }
  }, [theme, updateResolvedTheme]);
  useEffect(() => {
    if (typeof window === "undefined" || !window.matchMedia) {
      return;
    }
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const handler = () => {
      if (theme === "system") {
        updateResolvedTheme("system");
      }
    };
    media.addEventListener("change", handler);
    return () => media.removeEventListener("change", handler);
  }, [theme, updateResolvedTheme]);
  useEffect(() => {
    updateResolvedTheme(readStoredTheme());
  }, [updateResolvedTheme]);
  const value = useMemo(
    () => ({
      theme,
      resolvedTheme,
      setTheme: setThemeState
    }),
    [theme, resolvedTheme]
  );
  return /* @__PURE__ */ jsx(ThemeContext.Provider, { value, children });
}
function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return ctx;
}
function AppProviders({ children, queryClient }) {
  if (!queryClient) {
    throw new Error("AppProviders requires a queryClient instance.");
  }
  return /* @__PURE__ */ jsx(ThemeProvider, { children: /* @__PURE__ */ jsx(AuthProvider, { children: /* @__PURE__ */ jsx(QueryClientProvider, { client: queryClient, children }) }) });
}
function createQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 6e4,
        gcTime: 5 * 6e4,
        retry(failureCount, error) {
          if (error?.status === 401 || error?.status === 403) {
            return false;
          }
          return failureCount < 2;
        },
        refetchOnWindowFocus: false
      },
      mutations: {
        retry: 0
      }
    }
  });
}
createQueryClient();
const SUPPORT_SETTINGS_QUERY_KEY = ["support-settings-public"];
async function fetchSupportSettings({ signal, baseUrl }) {
  const apiBase = baseUrl ?? getApiBase();
  const response = await fetch(`${apiBase}/support/settings/public`, { signal });
  if (!response.ok) {
    const error = new Error(`Failed to load public settings (HTTP ${response.status}).`);
    error.status = response.status;
    throw error;
  }
  return response.json();
}
function useSupportSettings(options = {}) {
  return useQuery({
    queryKey: SUPPORT_SETTINGS_QUERY_KEY,
    queryFn: ({ signal }) => fetchSupportSettings({ signal }),
    staleTime: 5 * 6e4,
    ...options
  });
}
async function prefetchSupportSettings(queryClient, baseUrl) {
  try {
    await queryClient.prefetchQuery({
      queryKey: SUPPORT_SETTINGS_QUERY_KEY,
      queryFn: ({ signal }) => fetchSupportSettings({ signal, baseUrl })
    });
  } catch (error) {
    console.warn("[SSR] Unable to prefetch public settings", error);
  }
}
const loaders = [
  {
    name: "support-settings",
    matcher: () => true,
    run: async ({ queryClient, apiBase }) => {
      if (!apiBase) return;
      await prefetchSupportSettings(queryClient, apiBase);
    }
  }
];
async function runLoaders({ url, queryClient, headers, apiBase }) {
  const matches = matchRoutes(routeConfig, url) || [];
  for (const loader of loaders) {
    try {
      const shouldRun = loader.matcher({ url, matches, headers });
      if (shouldRun) {
        await loader.run({ url, matches, headers, queryClient, apiBase });
      }
    } catch (error) {
      console.error(`[SSR] loader ${loader.name} failed`, error);
    }
  }
}
const SSR_API_BASE = process.env.SSR_API_BASE || process.env.VITE_API_URL || process.env.VITE_API_BASE || null;
const NORMALIZED_API_BASE = SSR_API_BASE ? SSR_API_BASE.replace(/\/+$/, "") : null;
async function createApp({ url, headers }) {
  const queryClient = createQueryClient();
  await runLoaders({
    url,
    headers,
    queryClient,
    apiBase: NORMALIZED_API_BASE
  });
  const app = /* @__PURE__ */ jsx(AppProviders, { queryClient, children: /* @__PURE__ */ jsx(StaticRouter, { location: url, children: /* @__PURE__ */ jsx(App, {}) }) });
  return { app, queryClient };
}
export {
  useTheme as a,
  useSupportSettings as b,
  createApp,
  getApiBase as g,
  isAdminRole as i,
  useAuth as u
};
