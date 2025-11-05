import { z } from "zod";
import { apiFetch } from "../lib/apiClient";
import { useUIStore, TenantInfo } from "../store/uiStore";

const tenantSchema = z.object({
  id: z.union([z.string(), z.number()]).transform((value) => String(value)),
  name: z.string().optional().default(""),
});

const tenantListSchema = z.array(tenantSchema);

export async function fetchTenants(token: string | null): Promise<TenantInfo[]> {
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const tenants = await apiFetch("/admin/tenants", tenantListSchema, { headers });
  const normalized = tenants.map((tenant) => ({ id: tenant.id, name: tenant.name ?? "" }));
  useUIStore.getState().setTenants(normalized);
  return normalized;
}
