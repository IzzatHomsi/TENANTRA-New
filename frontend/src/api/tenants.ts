import { z } from "zod";
import { apiFetch, bearerHeader } from "../lib/apiClient";
import { useUIStore, TenantInfo } from "../store/uiStore";

const tenantSchema = z.object({
  id: z.union([z.string(), z.number()]).transform((value) => String(value)),
  name: z.string().optional().default(""),
});

const tenantListSchema = z.array(tenantSchema);

export async function fetchTenants(token: string | null): Promise<TenantInfo[]> {
  const headers: Record<string, string> = {
    ...bearerHeader(token),
  };
  const tenants = await apiFetch("/admin/tenants", tenantListSchema, { headers });
  const normalized: TenantInfo[] = tenants.map((tenant) => ({ id: String(tenant.id), name: tenant.name ?? "" }));
  useUIStore.getState().setTenants(normalized);
  return normalized;
}
