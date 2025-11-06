import { z } from "zod";
import { apiFetch, bearerHeader } from "../lib/apiClient";

const appSettingSchema = z.object({
  id: z.union([z.number(), z.string()]).transform((value) => String(value)),
  tenant_id: z.union([z.string(), z.number()]).nullable().optional().transform((value) => {
    if (value === undefined) return null;
    if (value === null || value === "") return null;
    return String(value);
  }),
  key: z.string(),
  value: z.any(),
});

const settingListSchema = z.array(appSettingSchema);

export type AppSetting = z.infer<typeof appSettingSchema>;

export async function fetchGlobalSettings(token: string | null, tenantId?: string | null) {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...bearerHeader(token),
  };
  if (tenantId) headers["X-Tenant-Id"] = tenantId;
  return apiFetch("/admin/settings", settingListSchema, {
    headers,
  });
}

export async function updateGlobalSettings(token: string | null, payload: Record<string, unknown>, tenantId?: string | null) {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...bearerHeader(token),
  };
  if (tenantId) headers["X-Tenant-Id"] = tenantId;
  return apiFetch("/admin/settings", settingListSchema, {
    method: "PUT",
    headers,
    body: JSON.stringify(payload),
  });
}

export async function fetchTenantSettings(token: string | null, tenantId?: string | null) {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...bearerHeader(token),
  };
  if (tenantId) headers["X-Tenant-Id"] = tenantId;
  return apiFetch("/admin/settings/tenant", settingListSchema, {
    headers,
  });
}

export async function updateTenantSettings(token: string | null, payload: Record<string, unknown>, tenantId?: string | null) {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...bearerHeader(token),
  };
  if (tenantId) headers["X-Tenant-Id"] = tenantId;
  return apiFetch("/admin/settings/tenant", settingListSchema, {
    method: "PUT",
    headers,
    body: JSON.stringify(payload),
  });
}
