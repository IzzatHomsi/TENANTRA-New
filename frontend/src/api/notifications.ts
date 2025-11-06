import { z } from "zod";
import { apiFetch, bearerHeader } from "../lib/apiClient";

const notificationSchema = z.object({
  id: z.union([z.string(), z.number()]).optional(),
  title: z.string().optional().default(""),
  message: z.string().optional().default(""),
  sent_at: z.string().optional().default(""),
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
  severity: z.string().optional().default("info"),
});

const notificationListSchema = z.array(notificationSchema);

export type Notification = z.infer<typeof notificationSchema>;

export async function fetchNotifications(token: string | null) {
  const headers: Record<string, string> = {
    ...bearerHeader(token),
  };
  return apiFetch("/notifications", notificationListSchema, { headers });
}
