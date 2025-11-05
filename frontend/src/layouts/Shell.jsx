import React, { useEffect, useMemo, useRef, useState } from "react";
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

const APP_ROOT = "/app";

const NAV_TEMPLATE = [
  {
    label: "Observability",
    items: [
      { to: `${APP_ROOT}/dashboard`, label: "Dashboard", exact: true },
      { to: `${APP_ROOT}/metrics`, label: "Metrics" },
      { to: `${APP_ROOT}/discovery`, label: "Discovery" },
      { to: `${APP_ROOT}/profile`, label: "My Profile" },
      { to: `${APP_ROOT}/notifications`, label: "Notifications" },
      { to: `${APP_ROOT}/notification-history`, label: "Notification History", featureKey: "notificationHistory" },
      { to: `${APP_ROOT}/alert-settings`, label: "Alert Settings", adminOnly: true, featureKey: "alertSettings" },
      { to: `${APP_ROOT}/audit-logs`, label: "Audit Logs", adminOnly: true, featureKey: "auditLogs" },
      { to: `${APP_ROOT}/feature-flags`, label: "Feature Flags", adminOnly: true, featureKey: "featureFlags" },
    ],
  },
  {
    label: "Compliance",
    items: [
      { to: `${APP_ROOT}/compliance-trends`, label: "Compliance Trends" },
      { to: `${APP_ROOT}/compliance-matrix`, label: "Compliance Matrix" },
      { to: `${APP_ROOT}/retention`, label: "Retention Exports" },
      { to: `${APP_ROOT}/scans`, label: "Scan Orchestration" },
      { to: `${APP_ROOT}/modules`, label: "Module Catalog" },
    ],
  },
  {
    label: "Runtime Fabric",
    items: [
      { to: `${APP_ROOT}/process-monitoring`, label: "Process Monitoring" },
      { to: `${APP_ROOT}/persistence`, label: "Persistence" },
      { to: `${APP_ROOT}/cloud`, label: "Cloud Discovery" },
      { to: `${APP_ROOT}/threat-intel`, label: "Threat Intelligence", adminOnly: true, featureKey: "threatIntel" },
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
  const [features, setFeatureState] = useState(featureFlags || {});
  const [searchQuery, setSearchQuery] = useState("");

  const { data: supportSettings } = useSupportSettings({ suspense: false, retry: 1 });

  // Apply public theming config once fetched
  useEffect(() => {
    const colorSetting = supportSettings?.["theme.colors.primary"];
    let color = colorSetting;
    if (!color || String(color).toLowerCase() === "#0ea5e9") {
      color = "#1877F2";
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
          navigate(`${APP_ROOT}/onboarding`, { replace: true });
        }
        onboardingChecked.current = true;
      } catch {}
    })();
  }, [location.pathname, navigate]);

  // Micro debug widget: optional polling enabled via localStorage('tena_debug_me_poll')==='1'
  const [meStatus, setMeStatus] = useState(null);
  const [meLastAt, setMeLastAt] = useState("");
  useEffect(() => {
    let timer;
    async function probe() {
      try {
        const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
        if (!token) { setMeStatus(null); return; }
        const r = await fetch(`${getApiBase()}/auth/me`, { headers: { 'Authorization': `Bearer ${token}` } });
        setMeStatus(r.status);
        setMeLastAt(new Date().toLocaleTimeString());
      } catch {
        setMeStatus(-1);
        setMeLastAt(new Date().toLocaleTimeString());
      }
    }
    try {
      const enabled = typeof window !== 'undefined' && localStorage.getItem('tena_debug_me_poll') === '1';
      if (!enabled) return;
    } catch {}
    probe();
    timer = setInterval(probe, 5000);
    return () => { if (timer) clearInterval(timer); };
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
          navigate(`${APP_ROOT}/search`);
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
    const path = location.pathname.replace(/\/$/, "");
    const exact = flattenedNav.find((item) => item.to === path);
    if (exact) {
      return exact.label;
    }

    const partial = flattenedNav.find((item) => path.startsWith(item.to));
    if (partial) {
      return partial.label;
    }

    if (path === APP_ROOT || path === `${APP_ROOT}/`) {
      return "Dashboard";
    }

    const segments = path.replace(`${APP_ROOT}/`, "").split("/").filter(Boolean);
    if (!segments.length) {
      return "Dashboard";
    }
    return segments
      .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1).replace(/-/g, " "))
      .join(" / ");
  }, [flattenedNav, location.pathname]);

  function handleLogout() {
    signOut();
    navigate("/login", { replace: true });
  }

  return (
    <div className="min-h-screen bg-neutral text-primary-text dark:bg-neutral dark:text-primary-text">
      <GlobalNotice kind={notice.kind} message={notice.message} onClose={() => setNotice({ kind: "info", message: "" })} />
      {/* Top bar */}
      <header className="fb-header sticky top-0 z-10">
        <div className="mx-auto max-w-7xl flex items-center justify-between" style={{ paddingLeft: 'var(--space-4)', paddingRight: 'var(--space-4)', height: 56 }}>
          <div className="flex items-center gap-3">
            <button
              type="button"
              className="fb-header__iconbtn inline-flex h-9 w-9 items-center justify-center rounded-md border lg:hidden"
              onClick={() => setSidebarOpen((v) => !v)}
              aria-label="Toggle navigation"
            >
              <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
            </button>
            <div>
              <div className="text-xs uppercase tracking-wide" style={{ opacity: 0.85 }}>Tenantra Platform</div>
              <div className="text-sm font-semibold">{currentRouteLabel}</div>
            </div>
          </div>
          <div className="flex items-center gap-4 relative">
            <input
              className="hidden md:block rounded-md px-2 py-1 text-sm top-search"
              placeholder="Search…"
              onKeyDown={(e)=>{ if(e.key==='Enter'){ window.dispatchEvent(new CustomEvent('tena:notice',{ detail: { kind:'info', message:`Search for "${e.currentTarget.value}" not yet implemented`}})); e.currentTarget.blur(); } }}
            />
            {isAdminRole(role) && tenants.length > 0 && (
              <div>
                <select
                  value={tenantId || ""}
                  onChange={(e) => {
                    const v = e.target.value;
                    const t = tenants.find((tenant) => tenant.id === v);
                    setTenant(v, t?.name);
                    setGlobalToast(v ? 'Tenant switched' : 'Tenant cleared');
                  }}
                  className="tenant-select px-2 py-1 text-sm"
                  title="Select tenant scope"
                >
                  <option value="">All tenants</option>
                  {tenants.map(t => (
                    <option key={t.id} value={t.id}>{t.name}</option>
                  ))}
                </select>
              </div>
            )}
            <div className="hidden sm:block text-right">
              <div className="text-sm font-medium">{user?.username || "user"}</div>
              <div className="text-xs text-secondary-text" style={{ opacity: 0.85 }}>{role || "role"}</div>
            </div>
            {/* Micro debug indicator for /auth/me */}
            <div title={`/auth/me ${meStatus ?? ''} @ ${meLastAt || ''}`} className="flex items-center gap-1">
              <span className={`inline-block h-2.5 w-2.5 rounded-full ${meStatus===200?'bg-secondary':(meStatus==null?'bg-neutral':'bg-red-500')}`} />
              <span className="hidden md:inline text-[10px] text-secondary-text">{meStatus ?? '?'}{meLastAt?` • ${meLastAt}`:''}</span>
            </div>
            <div className="avatar" title={user?.username || ''}>{(user?.username||'U').toString().charAt(0).toUpperCase()}</div>
            <div className="relative">
            <button
              type="button"
              onClick={() => setSettingsOpen((v) => !v)}
              className="fb-header__iconbtn inline-flex h-9 w-9 items-center justify-center rounded-md border"
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
              <div className="absolute right-0 top-10 z-20 w-64 rounded-md border border-border-color bg-surface p-3 text-primary-text shadow-lg transition-colors dark:bg-surface dark:border-border-color">
                <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-secondary-text">System</div>
                <label className="mb-1 block text-sm text-secondary-text">Theme</label>
                <select
                  value={theme}
                  onChange={(e) => { setTheme(e.target.value); setToast("Theme updated"); }}
                  className="w-full rounded-md border border-border-color bg-surface px-2 py-1 text-sm text-primary-text transition-colors dark:bg-surface dark:border-border-color"
                >
                  <option value="system">System</option>
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                </select>
                {toast && (
                  <div className="mt-2 rounded bg-[#D1FAE5] text-[#065F46] px-2 py-1 text-xs dark:bg-[#065F46]/40 dark:text-[#A7F3D0]">
                    {toast}
                  </div>
                )}
                <div className="mt-3 h-px bg-border-color dark:bg-border-color" />
                <div className="mt-3 text-sm text-primary-text">
                  <NavLink to={`${APP_ROOT}/profile`} className="block rounded px-2 py-1 text-primary-text hover:bg-neutral" onClick={()=>setSettingsOpen(false)}>My Profile</NavLink>
                  {isAdmin && (
                    <>
                      <NavLink to={`${APP_ROOT}/alert-settings`} className="block rounded px-2 py-1 text-primary-text hover:bg-neutral" onClick={()=>setSettingsOpen(false)}>Alert Settings</NavLink>
                      <NavLink to={`${APP_ROOT}/admin-settings`} className="block rounded px-2 py-1 text-primary-text hover:bg-neutral" onClick={()=>setSettingsOpen(false)}>Admin Settings</NavLink>
                      <NavLink to={`${APP_ROOT}/feature-flags`} className="block rounded px-2 py-1 text-primary-text hover:bg-neutral" onClick={()=>setSettingsOpen(false)}>Feature Flags</NavLink>
                      <NavLink to={`${APP_ROOT}/audit-logs`} className="block rounded px-2 py-1 text-primary-text hover:bg-neutral" onClick={()=>setSettingsOpen(false)}>Audit Logs</NavLink>
                      <NavLink to={`${APP_ROOT}/observability-setup`} className="block rounded px-2 py-1 text-primary-text hover:bg-neutral" onClick={()=>setSettingsOpen(false)}>Observability Setup</NavLink>
                      <NavLink to={`${APP_ROOT}/faq`} className="block rounded px-2 py-1 text-primary-text hover:bg-neutral" onClick={()=>setSettingsOpen(false)}>Help & FAQ</NavLink>
                      <NavLink to={`${APP_ROOT}/users`} className="block rounded px-2 py-1 text-primary-text hover:bg-neutral" onClick={()=>setSettingsOpen(false)}>User Directory</NavLink>
                    </>
                  )}
                </div>
              </div>
            )}
            </div>
            <button
              type="button"
              onClick={handleLogout}
              className="fb-header__logout inline-flex items-center rounded-md px-3 py-1.5 text-sm font-medium hover:opacity-90"
            >
              Logout
            </button>
          </div>
        </div>
      </header>
      {globalToast && (
        <div className="fixed right-4 top-14 z-30 rounded bg-secondary px-3 py-1.5 text-xs text-white shadow">
          {globalToast}
        </div>
      )}

      {/* Shell */}
      <div className="flex w-full gap-6 px-4 sm:px-6 lg:px-8 py-6 transition-colors duration-200">
        {/* Sidebar */}
        <aside className={`fixed inset-y-14 left-0 w-72 sidebar p-4 transition-transform lg:static lg:translate-x-0 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:block`}>
          <div className="mb-4 flex items-center gap-2">
            <span className="inline-block h-2.5 w-2.5 rounded-full bg-secondary" />
            <div>
              <div className="text-sm font-semibold">Tenantra</div>
              <div className="text-xs text-secondary-text">Operations Fabric</div>
              {tenantId && (
                <div className="text-xs mt-0.5 text-secondary-text dark:text-secondary-text">Tenant: {tenantName || `#${tenantId}`}</div>
              )}
            </div>
          </div>

          <div className="space-y-6">
            {navSections.map((section) => (
              <div key={section.label}>
                <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-secondary-text">{section.label}</div>
                <nav className="space-y-1">
                  {section.items.map((item) => (
                    <NavLink
                      key={item.to}
                      to={item.to}
                      end={Boolean(item.exact)}
                      className={({ isActive }) => `block rounded-md px-3 py-2 text-sm ${isActive ? 'active' : ''}`}
                      style={({ isActive }) => isActive ? undefined : undefined}
                      onClick={() => setSidebarOpen(false)}
                    >
                      {item.label}
                    </NavLink>
                  ))}
                </nav>
              </div>
            ))}
          </div>

          <div className="mt-8 rounded-md border border-border-color p-3 text-xs text-secondary-text dark:text-secondary-text dark:border-border-color">
            Resilient compliance, runtime integrity, and tenant trust in a unified workspace.
          </div>
        </aside>

        {/* Main */}
        <main className="flex-1 min-w-0">
          <div className="rounded-lg bg-surface p-4 shadow-sm dark:bg-surface">
            {tenantId && (
              <div className="mb-3 rounded border border-dashed border-border-color p-2 text-xs text-primary-text dark:border-border-color dark:text-secondary-text">
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

function navLinkClass({ isActive }) {
  return `layout-shell__link${isActive ? " is-active" : ""}`;
}
