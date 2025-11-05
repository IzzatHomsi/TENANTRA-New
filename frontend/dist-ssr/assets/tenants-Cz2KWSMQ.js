import { z } from "zod";
import { a as apiFetch, u as useUIStore } from "./apiClient-Y8eZ7muQ.js";
const tenantSchema = z.object({
  id: z.union([z.string(), z.number()]).transform((value) => String(value)),
  name: z.string().optional().default("")
});
const tenantListSchema = z.array(tenantSchema);
async function fetchTenants(token) {
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const tenants = await apiFetch("/admin/tenants", tenantListSchema, { headers });
  const normalized = tenants.map((tenant) => ({ id: tenant.id, name: tenant.name ?? "" }));
  useUIStore.getState().setTenants(normalized);
  return normalized;
}
export {
  fetchTenants as f
};
