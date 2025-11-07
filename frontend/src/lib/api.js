import { getApiBase } from "../utils/apiBase";
import { getToken, clearAuth } from "./auth";

const API_URL = getApiBase();

function headers(extra = {}) {
  const token = getToken();
  let tenantHeaders = {};
  try {
    const tid = localStorage.getItem('tenant_id');
    if (tid) tenantHeaders['X-Tenant-Id'] = tid;
  } catch (error) {
    // Ignore storage errors (e.g., SSR or private-mode restrictions)
  }
  return {
    Accept: "application/json",
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...tenantHeaders,
    ...extra,
  };
}

async function handle(res) {
  const ct = res.headers.get("content-type") || "";
  const body = ct.includes("application/json") ? await res.json() : null;
  if (!res.ok) {
    if (res.status === 401) {
      try {
        const noLogout = typeof window !== 'undefined' && localStorage.getItem('tena_debug_no_logout') === '1';
        if (!noLogout) clearAuth();
      } catch { clearAuth(); }
    }
    const msg = body?.detail || `HTTP ${res.status}`;
    const err = new Error(msg);
    err.status = res.status;
    err.body = body;
    throw err;
  }
  return body;
}

export const api = {
  get: async (path) => {
    try {
      return await handle(await fetch(`${API_URL}${path}`, { method: "GET", headers: headers() }));
    } catch (e) {
      if (e && e.status === 404) return null;
      throw e;
    }
  },
  post: async (path, data) => handle(await fetch(`${API_URL}${path}`, { method: "POST", headers: headers(), body: JSON.stringify(data ?? {}) })),
  put: async (path, data) => handle(await fetch(`${API_URL}${path}`, { method: "PUT", headers: headers(), body: JSON.stringify(data ?? {}) })),
  del: async (path) => handle(await fetch(`${API_URL}${path}`, { method: "DELETE", headers: headers() })),
};

