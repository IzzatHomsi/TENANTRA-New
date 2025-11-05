import { create } from "zustand";
import { persist } from "zustand/middleware";
import { z } from "zod";
import { g as getApiBase } from "../entry-server.js";
const initialState = {
  tenantId: "",
  tenantName: "",
  tenants: [],
  featureFlags: {}
};
const useUIStore = create()(
  persist(
    (set) => ({
      ...initialState,
      setTenant: (id, name) => set(() => {
        const tenantName = name || "";
        if (typeof window !== "undefined") {
          try {
            if (id) {
              localStorage.setItem("tenant_id", id);
            } else {
              localStorage.removeItem("tenant_id");
            }
            if (tenantName) {
              localStorage.setItem("tenant_name", tenantName);
            } else {
              localStorage.removeItem("tenant_name");
            }
          } catch {
          }
        }
        return { tenantId: id, tenantName };
      }),
      setTenants: (tenants) => set(() => ({ tenants: tenants.map((t) => ({ id: String(t.id), name: t.name || "" })) })),
      setFeatureFlags: (flags) => set(() => ({ featureFlags: { ...flags } })),
      reset: () => set(() => ({ ...initialState }))
    }),
    {
      name: "tena-ui-store",
      partialize: (state) => ({
        tenantId: state.tenantId,
        tenantName: state.tenantName,
        tenants: state.tenants,
        featureFlags: state.featureFlags
      })
    }
  )
);
const errorSchema = z.object({ detail: z.union([z.string(), z.object({}).passthrough()]).optional() }).passthrough();
async function apiFetch(path, schema, options = {}) {
  const base = getApiBase();
  const res = await fetch(`${base}${path}`, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...options.headers || {}
    },
    ...options
  });
  if (!res.ok) {
    let message = `HTTP ${res.status}`;
    try {
      const json = await res.json();
      const parsed = errorSchema.parse(json);
      if (parsed.detail) {
        message = typeof parsed.detail === "string" ? parsed.detail : JSON.stringify(parsed.detail);
      }
    } catch {
    }
    const err = new Error(message);
    err.status = res.status;
    throw err;
  }
  const data = await res.json();
  return schema.parse(data);
}
export {
  apiFetch as a,
  useUIStore as u
};
