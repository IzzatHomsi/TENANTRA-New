import { create } from "zustand";
import { persist } from "zustand/middleware";

type FeatureFlags = Record<string, boolean>;

export interface TenantInfo {
  id: string;
  name: string;
}

interface UIState {
  tenantId: string;
  tenantName: string;
  tenants: TenantInfo[];
  featureFlags: FeatureFlags;
  setTenant: (id: string, name?: string) => void;
  setTenants: (tenants: TenantInfo[]) => void;
  setFeatureFlags: (flags: FeatureFlags) => void;
  reset: () => void;
}

const initialState: Pick<UIState, "tenantId" | "tenantName" | "featureFlags" | "tenants"> = {
  tenantId: "",
  tenantName: "",
  tenants: [],
  featureFlags: {},
};

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      ...initialState,
      setTenant: (id, name) =>
        set(() => {
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
            } catch {}
          }
          return { tenantId: id, tenantName };
        }),
      setTenants: (tenants) =>
        set(() => ({ tenants: tenants.map((t) => ({ id: String(t.id), name: t.name || "" })) })),
      setFeatureFlags: (flags) => set(() => ({ featureFlags: { ...flags } })),
      reset: () => set(() => ({ ...initialState })),
    }),
    {
      name: "tena-ui-store",
      partialize: (state) => ({
        tenantId: state.tenantId,
        tenantName: state.tenantName,
        tenants: state.tenants,
        featureFlags: state.featureFlags,
      }),
    }
  )
);
