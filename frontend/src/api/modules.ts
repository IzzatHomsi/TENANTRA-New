import { z } from "zod";
import { apiFetch, bearerHeader } from "../lib/apiClient";

const moduleSchema = z.object({
  id: z.union([z.string(), z.number()]).transform((value) => String(value)),
  name: z.string().optional().default(""),
  category: z.string().nullable().optional(),
  description: z.string().nullable().optional(),
  purpose: z.string().nullable().optional(),
  phase: z.union([z.number(), z.string()]).nullable().optional(),
  enabled: z.boolean().optional().default(false),
  has_runner: z.boolean().optional().default(false),
});

export const moduleListSchema = z.array(moduleSchema);

export async function fetchModules(token: string | null) {
  const headers: Record<string, string> = {
    ...bearerHeader(token),
  };
  return apiFetch("/modules/", moduleListSchema, { headers });
}

export async function updateModule(id: string, payload: unknown, token: string | null) {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...bearerHeader(token),
  };
  const schema = moduleSchema;
  return apiFetch(`/modules/${id}`, schema, {
    method: "PUT",
    headers,
    body: JSON.stringify(payload),
  });
}
