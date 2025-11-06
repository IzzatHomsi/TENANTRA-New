import { z } from "zod";
import { apiFetch, bearerHeader } from "../lib/apiClient";

const moduleToggleSchema = z.object({
  id: z.union([z.string(), z.number()]).transform((value) => String(value)),
  name: z.string().optional().default(""),
  category: z.string().nullable().optional(),
  phase: z.union([z.number(), z.string()]).nullable().optional(),
  enabled: z.boolean().optional().default(false),
  plan: z.string().nullable().optional(),
});

export type AdminModuleRecord = z.infer<typeof moduleToggleSchema>;

const moduleListSchema = z.array(moduleToggleSchema);

const bulkToggleSchema = z.object({
  enable: z.array(z.union([z.string(), z.number()])).optional().default([]),
  disable: z.array(z.union([z.string(), z.number()])).optional().default([]),
});

export async function fetchAdminModules(headers: Record<string, string>) {
  return apiFetch("/admin/modules", moduleListSchema, { headers });
}

export async function updateAdminModules(
  headers: Record<string, string>,
  payload: { enable: Array<string | number>; disable: Array<string | number> }
) {
  return apiFetch("/admin/modules/bulk", bulkToggleSchema, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      ...headers,
    },
    body: JSON.stringify(payload),
  });
}
