import { z } from "zod";
import { apiFetch, bearerHeader } from "../lib/apiClient";

const alertSchema = z.object({
  id: z.union([z.string(), z.number()]).optional(),
  name: z.string().optional().default(""),
  rule: z.string().optional().default(""),
  status: z.string().optional().default(""),
});

const alertListSchema = z.array(alertSchema);

export type AlertRecord = z.infer<typeof alertSchema>;

export async function fetchAlerts(token: string | null) {
  const headers: Record<string, string> = {
    ...bearerHeader(token),
  };
  return apiFetch("/alerts", alertListSchema, { headers });
}
