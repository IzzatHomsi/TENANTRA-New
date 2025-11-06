import { z } from "zod";
import { apiFetch } from "../lib/apiClient";

const auditEntrySchema = z.object({
  id: z.union([z.string(), z.number()]).optional(),
  timestamp: z.string().optional(),
  created_at: z.string().optional(),
  user_id: z.string().nullable().optional(),
  action: z.string().optional().default(""),
  result: z.string().optional().default(""),
  metadata: z.record(z.any()).optional(),
  detail: z.any().optional(),
});

const auditListSchema = z.object({
  items: z.array(auditEntrySchema).optional().default([]),
  total: z.number().optional().default(0),
});

const exportResponseSchema = z.object({ success: z.boolean().optional() }).passthrough();

export type AuditList = z.infer<typeof auditListSchema>;

export async function fetchAuditLogs(
  headers: Record<string, string>,
  params: Record<string, string | number | undefined>
) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== "") search.set(key, String(value));
  });
  const path = `/audit-logs${search.size ? `?${search.toString()}` : ""}`;
  return apiFetch(path, auditListSchema, { headers });
}

export async function exportAuditLogs(headers: Record<string, string>, params: Record<string, string | number | undefined>) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== "") search.set(key, String(value));
  });
  const path = `/audit-logs/export${search.size ? `?${search.toString()}` : ""}`;
  return apiFetch(path, exportResponseSchema, { headers });
}
