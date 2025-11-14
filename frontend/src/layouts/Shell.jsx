import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import { useTheme } from "../context/ThemeContext.jsx";
import { getApiBase } from "../utils/apiBase";
import { isAdminRole } from "../utils/rbac.js";
import GlobalNotice from "../components/GlobalNotice.jsx";
import { useSupportSettings } from "../queries/supportSettings.js";
import { useUIStore } from "../store/uiStore";
import { fetchFeatureFlags } from "../api/features";
import { fetchTenants } from "../api/tenants";

const APP_ROOT = (import.meta.env.BASE_URL?.replace(/\/$/, "") || "");
const toRoute = (path) => (path.startsWith("/") ? path : `/${path}`);
const normalizePathname = (pathname = "/") => {
  if (!APP_ROOT) return pathname || "/";
  if (!pathname.startsWith(APP_ROOT)) return pathname || "/";
  const next = pathname.slice(APP_ROOT.length) || "/";
  return next.startsWith("/") ? next : `/${next}`;
};

const NAV_TEMPLATE = [
  {
    label: "Observability",
    items: [
      { to: toRoute("/dashboard"), label: "Dashboard", exact: true },
      { to: toRoute("/metrics"), label: "Metrics" },
      { to: toRoute("/discovery"), label: "Discovery" },
      { to: toRoute("/notifications"), label: "Notifications" },
      { to: toRoute("/notification-history"), label: "Notification History", featureKey: "notificationHistory" },
      { to: toRoute("/alert-settings"), label: "Alert Settings", adminOnly: true, featureKey: "alertSettings" },
      { to: toRoute("/audit-logs"), label: "Audit Logs", adminOnly: true, featureKey: "auditLogs" },
      { to: toRoute("/agent-management"), label: "Agent Management", adminOnly: true },
    ],
  },
  {
    label: "Compliance",
    items: [
      { to: toRoute("/compliance-trends"), label: "Compliance Trends" },
      { to: toRoute("/compliance-matrix"), label: "Compliance Matrix" },
      { to: toRoute("/retention"), label: "Retention Exports" },
      { to: toRoute("/scans"), label: "Scan Orchestration" },
      { to: toRoute("/modules"), label: "Module Catalog" },
    ],
  },
  {
    label: "Runtime Fabric",
    items: [
      { to: toRoute("/process-monitoring"), label: "Process Monitoring" },
      { to: toRoute("/persistence"), label: "Persistence" },
      { to: toRoute("/cloud"), label: "Cloud Discovery" },
      { to: toRoute("/threat-intel"), label: "Threat Intelligence", adminOnly: true, featureKey: "threatIntel" },
    ],
  },
  // Administration links moved under gear menu
];

export default function Shell() {
  const { user, role, signOut } = useAuth();
  const { theme, setTheme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const {
    tenantId,
    tenantName,
    tenants,
    setTenant,
    setTenants,
    featureFlags,
    setFeatureFlags,
  } = useUIStore();
  const onboardingChecked = useRef(false);
  const fetchedTenantsRef = useRef(false);
  const extensionHintsRef = useRef(new Set());
  const extensionDismissedRef = useRef(
    typeof window !== "undefined" && localStorage.getItem("tena_extension_notice") === "1"
  );
  const [features, setFeatureState] = useState(featureFlags || {});
  const [searchQuery, setSearchQuery] = useState("");
  const [extensionWarning, setExtensionWarning] = useState(false);
  const [extensionHints, setExtensionHints] = useState([]);

  const { data: supportSettings } = useSupportSettings({ suspense: false, retry: 1 });

  // Apply public theming config once fetched
  useEffect(() => {
    const colorSetting = supportSettings?.["theme.colors.primary"];
    let color = colorSetting;
    if (!color || String(color).toLowerCase() === "#0ea5e9") {
      color = "#111827";
    }
    try {
      document.documentElement.style.setProperty("--tena-primary", color);
    } catch {}
  }, [supportSettings]);

  // Load tenants for MSSP admin to allow quick switching (once per session)
  useEffect(() => {
    (async () => {
      try {
        const isAdmin = isAdminRole(role);
        if (!isAdmin) return;
        if (fetchedTenantsRef.current) return;
        const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
        const list = await fetchTenants(token);
        setTenants(list);
        if (!tenantId && list.length > 0) {
          setTenant(list[0].id, list[0].name);
        }
        fetchedTenantsRef.current = true;
      } catch {}
    })();
  }, [role, setTenant, setTenants, tenantId]);

  // Fetch feature flags for current user/tenant
  useEffect(() => {
    (async () => {
      try {
        const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
        const json = await fetchFeatureFlags(token);
        setFeatureState(json || {});
        setFeatureFlags(json || {});
      } catch {}
    })();
  }, [setFeatureState, setFeatureFlags]);

  useEffect(() => {
    setFeatureState(featureFlags || {});
  }, [featureFlags]);

  // Redirect to onboarding if not completed (admin users only) and not already on onboarding route (once)
  useEffect(() => {
    (async () => {
      try {
        // Only gate paths under /app and not onboarding itself
        if (!location.pathname.startsWith(`${APP_ROOT}`)) return;
        if (location.pathname.startsWith(`${APP_ROOT}/onboarding`)) return;
        if (onboardingChecked.current) return;
        // Check admin settings to see if onboarding is done
        const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
        const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
        const res = await fetch(`${getApiBase()}/admin/settings`, { headers });
        if (!res.ok) return;
        const items = await res.json();
        const map = Object.fromEntries(items.map((x) => [x.key, x.value]));
        if (!map['onboarding.done']) {
          navigate("/onboarding", { replace: true });
        }
        onboardingChecked.current = true;
      } catch {}
    })();
  }, [location.pathname, navigate]);

  // API connection indicator (always visible)
  const [apiStatus, setApiStatus] = useState({ state: "checking", lastChecked: "" });
  useEffect(() => {
    let cancelled = false;
    let timer;
    async function probe() {
      try {
        const res = await fetch(`${getApiBase()}/health`, { cache: "no-store" });
        if (cancelled) return;
        setApiStatus({
          state: res.ok ? "online" : "degraded",
          lastChecked: new Date().toLocaleTimeString(),
        });
      } catch {
        if (cancelled) return;
        setApiStatus({
          state: "offline",
          lastChecked: new Date().toLocaleTimeString(),
        });
      }
    }
    probe();
    timer = window.setInterval(probe, 15000);
    return () => {
      cancelled = true;
      if (timer) {
        clearInterval(timer);
      }
    };
  }, []);

  const dismissExtensionWarning = useCallback(() => {
    extensionDismissedRef.current = true;
    setExtensionWarning(false);
    setExtensionHints([]);
    try {
      localStorage.setItem("tena_extension_notice", "1");
    } catch {}
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") return;
    if (extensionDismissedRef.current) return;

    const markers = ["chrome-extension://", "moz-extension://", "safari-web-extension://"];
    const messageTriggers = ["runtime.lastError", "content_script"];

    const recordHint = (hint) => {
      if (extensionDismissedRef.current) return;
      if (!hint) hint = "browser extension";
      extensionHintsRef.current.add(hint);
      setExtensionHints(Array.from(extensionHintsRef.current));
      setExtensionWarning(true);
    };

    const sanitizeSource = (source) => {
      if (!source) return "";
      const match = source.match(/^[a-z-]+:\/\/([^/]+)/);
      return match ? match[1] : source;
    };

    const scanResources = () => {
      try {
        const entries = performance.getEntriesByType("resource") || [];
        for (const entry of entries) {
          if (typeof entry?.name === "string" && markers.some((marker) => entry.name.startsWith(marker))) {
            recordHint(sanitizeSource(entry.name));
          }
        }
      } catch {}
      try {
        document.querySelectorAll("script[src]").forEach((script) => {
          const src = script.getAttribute("src") || "";
          if (markers.some((marker) => src.startsWith(marker))) {
            recordHint(sanitizeSource(src));
          }
        });
      } catch {}
    };

    const onError = (event) => {
      if (extensionDismissedRef.current) return;
      const filename = event?.filename || "";
      const message = event?.message || "";
      if (
        markers.some((marker) => filename.startsWith(marker) || message.includes(marker)) ||
        messageTriggers.some((needle) => message.includes(needle))
      ) {
        recordHint(sanitizeSource(filename) || "extension runtime");
      }
    };

    const onRejection = (event) => {
      if (extensionDismissedRef.current) return;
      const reason = event?.reason;
      const text =
        typeof reason === "string"
          ? reason
          : reason && typeof reason.message === "string"
            ? reason.message
            : "";
      if (!text) return;
      if (
        markers.some((marker) => text.includes(marker)) ||
        messageTriggers.some((needle) => text.includes(needle))
      ) {
        recordHint("extension runtime");
      }
    };

    scanResources();
    const rescanTimer = window.setTimeout(scanResources, 1500);

    window.addEventListener("error", onError);
    window.addEventListener("unhandledrejection", onRejection);

    return () => {
      window.removeEventListener("error", onError);
      window.removeEventListener("unhandledrejection", onRejection);
      window.clearTimeout(rescanTimer);
    };
  }, []);

  // Listen for runtime settings updates (e.g., theme color) and show a toast
  useEffect(() => {
    function onSettingsUpdated(e) {
      const d = (e && e.detail) || {};
      if (d.key === 'theme.colors.primary' && d.value) {
        try { document.documentElement.style.setProperty('--tena-primary', d.value); } catch {}
        setToast('Theme color updated');
        try { setGlobalToast('Theme color updated'); } catch {}
      }
    }
    window.addEventListener('tena:settings-updated', onSettingsUpdated);
    return () => window.removeEventListener('tena:settings-updated', onSettingsUpdated);
  }, []);

  // small toast when settings updated
  const [toast, setToast] = useState("");
  const [globalToast, setGlobalToast] = useState("");
  const [notice, setNotice] = useState({ kind: "info", message: "" });
  // Keyboard shortcut: '/' opens search unless typing in an input/textarea/select
  useEffect(() => {
    function onKey(e) {
      try {
        const tag = (e.target && e.target.tagName) || '';
        if (e.key === '/' && !e.ctrlKey && !e.metaKey && !e.altKey && !/INPUT|TEXTAREA|SELECT/.test(tag)) {
          e.preventDefault();
          navigate("/search");
        }
      } catch {}
    }
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [navigate]);
  useEffect(() => {
    if (!settingsOpen) return;
    if (toast) {
      const t = setTimeout(() => setToast(""), 1800);
      return () => clearTimeout(t);
    }
  }, [toast, settingsOpen]);
  useEffect(() => {
    if (!globalToast) return;
    const t = setTimeout(() => setGlobalToast(""), 1800);
    return () => clearTimeout(t);
  }, [globalToast]);

  // Global notices and auth error handling
  useEffect(() => {
    function onNotice(e) {
      const d = (e && e.detail) || {};
      const msg = typeof d === "string" ? d : d.message || "";
      const kind = typeof d === "string" ? "info" : d.kind || d.type || "info";
      setNotice({ kind, message: msg });
    }
    async function onAuthError(e) {
      setNotice({ kind: "error", message: "Session expired or unauthorized. Please sign in again." });
      try { await new Promise(r => setTimeout(r, 10)); } catch {}
      signOut();
      navigate("/login", { replace: true, state: { from: location } });
    }
    window.addEventListener("tena:notice", onNotice);
    window.addEventListener("tena:auth-error", onAuthError);
    return () => {
      window.removeEventListener("tena:notice", onNotice);
      window.removeEventListener("tena:auth-error", onAuthError);
    };
  }, [navigate, location, signOut]);

  const isAdmin = useMemo(() => isAdminRole(role), [role]);

  const navSections = useMemo(() => {
    const q = (searchQuery || "").toLowerCase();
    return NAV_TEMPLATE.map((section) => ({
      ...section,
      items: section.items.filter((item) => {
        if (item.adminOnly && !isAdmin) return false;
        if (item.featureKey && features && Object.prototype.hasOwnProperty.call(features, item.featureKey)) {
          return !!features[item.featureKey];
        }
        if (!q) return true;
        return String(item.label || "").toLowerCase().includes(q);
      }),
    })).filter((section) => section.items.length > 0);
  }, [isAdmin, features, searchQuery]);

  const flattenedNav = useMemo(
    () => navSections.flatMap((section) => section.items),
    [navSections]
  );

  const currentRouteLabel = useMemo(() => {
    const path = normalizePathname(location.pathname).replace(/\/$/, "") || "/";
    const exact = flattenedNav.find((item) => item.to === path);
    if (exact) {
      return exact.label;
    }

    const partial = flattenedNav.find((item) => path.startsWith(item.to));
    if (partial) {
      return partial.label;
    }

    if (path === "/") {
      return "Dashboard";
    }

    const segments = path.replace(/^\//, "").split("/").filter(Boolean);
    if (!segments.length) {
      return "Dashboard";
    }
    return segments
      .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1).replace(/-/g, " "))
      .join(" / ");
  }, [flattenedNav, location.pathname]);

  const apiLabelMap = {
    online: "Online",
    degraded: "Degraded",
    offline: "Offline",
    checking: "Checking…",
  };
  const apiColorMap = {
    online: "var(--tena-secondary)",
    degraded: "var(--tena-warning)",
    offline: "var(--tena-danger)",
    checking: "var(--tena-muted)",
  };
  const apiStatusLabel = apiLabelMap[apiStatus.state] || apiLabelMap.checking;
  const apiIndicatorColor = apiColorMap[apiStatus.state] || apiColorMap.checking;

  function handleLogout() {
    signOut();
    navigate("/login", { replace: true });
  }

  return (
    <div className="tena-app min-h-screen text-primary-text dark:text-primary-text">
      <GlobalNotice kind={notice.kind} message={notice.message} onClose={() => setNotice({ kind: "info", message: "" })} />
      {extensionWarning && (
        <div className="mx-auto max-w-7xl px-4 pt-4">
          <div className="flex flex-col gap-2 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800 shadow-sm md:flex-row md:items-center md:justify-between">
            <div>
              <strong className="font-semibold">Browser extensions detected.</strong>{" "}
              Some corporate extensions inject scripts (runtime.lastError / content_script) that can break Admin Settings. Disable them or add Tenantra to the allowlist for the smoothest experience.
              {extensionHints.length > 0 && (
                <span className="mt-1 block text-xs text-amber-700/80">
                  Examples: {extensionHints.slice(0, 3).join(", ")}
                  {extensionHints.length > 3 ? "…" : ""}
                </span>
              )}
            </div>
            <button
              type="button"
              onClick={dismissExtensionWarning}
              className="btn btn-ghost self-start text-sm md:self-auto"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}
      {/* Top bar */}
      <header className="tena-header sticky top-0 z-20">
        <div className="tena-header__inner mx-auto w-full max-w-7xl">
          <div className="flex items-center gap-3">
            <button
              type="button"
              className="tena-header__iconbtn inline-flex h-9 w-9 items-center justify-center border lg:hidden"
              onClick={() => setSidebarOpen((v) => !v)}
              aria-label="Toggle navigation"
            >
              <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 6h18M3 12h18M3 18h18" />
              </svg>
            </button>
            <div className="tena-brand">
              <span className="tena-brand__glyph" aria-hidden="true">T</span>
              <div>
                <div className="tena-brand__eyebrow">Tenantra Ops Fabric</div>
                <div className="tena-brand__title">{currentRouteLabel}</div>
              </div>
            </div>
          </div>
          <div className="relative flex items-center gap-3 md:gap-4">
            <input
              type="search"
              className="top-search hidden md:block"
              placeholder="Search…"
              onKeyDown={(e)=>{ if(e.key==='Enter'){ window.dispatchEvent(new CustomEvent('tena:notice',{ detail: { kind:'info', message:`Search for "${e.currentTarget.value}" not yet implemented`}})); e.currentTarget.blur(); } }}
            />
            {isAdminRole(role) && tenants.length > 0 && (
              <select
                value={tenantId || ""}
                onChange={(e) => {
                  const v = e.target.value;
                  const t = tenants.find((tenant) => tenant.id === v);
                  setTenant(v, t?.name);
                  setGlobalToast(v ? 'Tenant switched' : 'Tenant cleared');
                }}
                className="tenant-select"
                title="Select tenant scope"
              >
                <option value="">All tenants</option>
                {tenants.map(t => (
                  <option key={t.id} value={t.id}>{t.name}</option>
                ))}
              </select>
            )}
            <div className="hidden sm:block text-right">
              <div className="text-sm font-semibold">{user?.username || "user"}</div>
              <div className="text-xs text-secondary-text">{role || "role"}</div>
            </div>
            <div
              className="tena-api-pill"
              title={`API status • ${apiStatusLabel}${apiStatus.lastChecked ? ` @ ${apiStatus.lastChecked}` : ""}`}
            >
              <span
                aria-hidden="true"
                className="inline-block h-2 w-2 rounded-full"
                style={{ backgroundColor: apiIndicatorColor }}
              />
              <span className="hidden sm:inline">API</span>
              <span className="font-semibold">{apiStatusLabel}</span>
            </div>
            <div className="avatar" title={user?.username || ''}>{(user?.username||'U').toString().charAt(0).toUpperCase()}</div>
            <div className="relative">
              <button
                type="button"
                onClick={() => setSettingsOpen((v) => !v)}
                className="tena-header__iconbtn inline-flex h-9 w-9 items-center justify-center border"
                title="System settings"
                aria-haspopup="menu"
                aria-expanded={settingsOpen}
              >
                <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 15.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Z"/>
                  <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33h0A1.65 1.65 0 0 0 9 3.09V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51h0a1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82h0A1.65 1.65 0 0 0 20.91 9H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1Z"/>
                </svg>
              </button>
              {settingsOpen && (
                <div className="tena-settings-menu absolute right-0 top-12 z-30 w-64 p-4 text-primary-text">
                  <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-secondary-text">System</div>
                  <label className="mb-1 block text-sm text-secondary-text" htmlFor="themeSelect">Theme</label>
                  <select
                    id="themeSelect"
                    value={theme}
                    onChange={(e) => { setTheme(e.target.value); setToast("Theme updated"); }}
                    className="w-full rounded-md border border-border-color bg-surface px-2 py-1 text-sm text-primary-text transition-colors dark:bg-surface dark:border-border-color"
                  >
                    <option value="system">System</option>
                    <option value="light">Light</option>
                    <option value="dark">Dark</option>
                  </select>
                  {toast && (
                    <div className="mt-2 rounded bg-[#D1FAE5] px-2 py-1 text-xs text-[#065F46] dark:bg-[#065F46]/40 dark:text-[#A7F3D0]">
                      {toast}
                    </div>
                  )}
                  <div className="mt-3 h-px bg-border-color dark:bg-border-color" />
                  <div className="mt-3 text-sm text-primary-text">
                    <NavLink to="/profile" className="tena-settings-menu__link" onClick={()=>setSettingsOpen(false)}>My Profile</NavLink>
                    {isAdmin && (
                      <>
                        <NavLink to="/alert-settings" className="tena-settings-menu__link" onClick={()=>setSettingsOpen(false)}>Alert Settings</NavLink>
                        <NavLink to="/admin-settings" className="tena-settings-menu__link" onClick={()=>setSettingsOpen(false)}>Admin Settings</NavLink>
                        <NavLink to="/feature-flags" className="tena-settings-menu__link" onClick={()=>setSettingsOpen(false)}>Feature Flags</NavLink>
                        <NavLink to="/audit-logs" className="tena-settings-menu__link" onClick={()=>setSettingsOpen(false)}>Audit Logs</NavLink>
                        <NavLink to="/observability-setup" className="tena-settings-menu__link" onClick={()=>setSettingsOpen(false)}>Observability Setup</NavLink>
                        <NavLink to="/faq" className="tena-settings-menu__link" onClick={()=>setSettingsOpen(false)}>Help & FAQ</NavLink>
                        <NavLink to="/users" className="tena-settings-menu__link" onClick={()=>setSettingsOpen(false)}>User Directory</NavLink>
                      </>
                    )}
                  </div>
                </div>
              )}
            </div>
            <button
              type="button"
              onClick={handleLogout}
              className="tena-header__logout inline-flex items-center px-4 py-2 text-sm"
            >
              Logout
            </button>
          </div>
        </div>
      </header>
      {sidebarOpen && (
        <div
          className="fixed inset-x-0 bottom-0 z-10 bg-slate-900/30 backdrop-blur-sm lg:hidden"
          style={{ top: 64 }}
          onClick={() => setSidebarOpen(false)}
        />
      )}
      {globalToast && (
        <div className="fixed right-4 top-20 z-30 rounded bg-secondary px-3 py-1.5 text-xs text-white shadow">
          {globalToast}
        </div>
      )}

      {/* Shell */}
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-6 px-4 pb-10 pt-6 transition-colors duration-200 lg:flex-row lg:px-8">
        {/* Sidebar */}
        <aside
          className={`fixed inset-y-16 left-0 z-20 w-72 sidebar px-5 py-6 transition-transform duration-300 lg:relative lg:inset-auto lg:z-0 lg:block lg:h-auto lg:max-h-none lg:translate-x-0 lg:sticky lg:top-6 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}
          aria-label="Primary navigation"
        >
          <div className="tena-sidebar__intro mb-4 flex items-center gap-2">
            <span className="inline-block h-2.5 w-2.5 rounded-full bg-secondary" />
            <div>
              <div className="tena-sidebar__title">Tenantra</div>
              <div className="tena-sidebar__subtitle">Operations Fabric</div>
              {tenantId && (
                <div className="text-xs mt-0.5 text-secondary-text dark:text-secondary-text">Tenant: {tenantName || `#${tenantId}`}</div>
              )}
            </div>
          </div>

          <div className="space-y-6">
            {navSections.map((section) => (
              <div key={section.label}>
                <div className="mb-2 text-secondary-text tena-nav__section-label">{section.label}</div>
                <nav className="space-y-1">
                  {section.items.map((item) => (
                    <NavLink
                      key={item.to}
                      to={item.to}
                      end={Boolean(item.exact)}
                      className={({ isActive }) => `tena-nav__link ${isActive ? 'tena-nav__link--active' : ''}`}
                      onClick={() => setSidebarOpen(false)}
                    >
                      {item.label}
                    </NavLink>
                  ))}
                </nav>
              </div>
            ))}
          </div>

          <div className="tena-sidebar__note mt-8 border px-3 py-3 text-xs text-secondary-text">
            Resilient compliance, runtime integrity, and tenant trust in a unified workspace.
          </div>
        </aside>

        {/* Main */}
        <main className="flex-1 min-w-0">
          <div className="tena-main-panel">
            {tenantId && (
              <div className="tena-scope-banner mb-3 px-3 py-2 text-xs">
                Tenant scope: <strong className="text-primary-text dark:text-primary-text">{tenantName || `#${tenantId}`}</strong>
              </div>
            )}
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
