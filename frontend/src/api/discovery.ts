import { z } from "zod";
import { apiFetch, bearerHeader } from "../lib/apiClient";

const portSchema = z.number().int().min(1).max(65535);

const targetSchema = z.object({
  host: z.string(),
  ports: z.array(portSchema).optional().default([]),
});

const discoveryResultSchema = z.object({
  findings: z.array(z.any()).optional().default([]),
  started_at: z.string().optional(),
  completed_at: z.string().optional(),
  status: z.string().optional(),
});

export type DiscoveryTarget = z.infer<typeof targetSchema>;
export type DiscoveryResult = z.infer<typeof discoveryResultSchema>;

export async function runDiscoveryScan(
  token: string | null,
  payload: { targets: DiscoveryTarget[] }
) {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...bearerHeader(token),
  };
  return apiFetch("/admin/network/port-scan", discoveryResultSchema, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });
}
