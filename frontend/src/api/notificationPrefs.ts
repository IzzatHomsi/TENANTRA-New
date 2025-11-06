import { z } from "zod";
import { apiFetch, bearerHeader } from "../lib/apiClient";

const channelsSchema = z.object({
  email: z.boolean().optional().default(true),
  webhook: z.boolean().optional().default(false),
  sms: z.boolean().optional().default(false),
});

const eventsSchema = z.object({
  scan_failed: z.boolean().optional().default(true),
  compliance_violation: z.boolean().optional().default(true),
  agent_offline: z.boolean().optional().default(true),
  threshold_breach: z.boolean().optional().default(false),
}).catchall(z.boolean());

const notificationPrefsSchema = z.object({
  channels: channelsSchema.optional().default({ email: true, webhook: false }),
  events: eventsSchema.optional().default({
    scan_failed: true,
    compliance_violation: true,
    agent_offline: true,
    threshold_breach: false,
  }),
  digest: z.string().optional().default("immediate"),
});

export type NotificationPreferences = z.infer<typeof notificationPrefsSchema>;

export async function fetchNotificationPreferences(token: string | null) {
  const headers: Record<string, string> = {
    ...bearerHeader(token),
  };
  return apiFetch("/notification-prefs", notificationPrefsSchema, { headers });
}

export async function updateNotificationPreferences(
  token: string | null,
  payload: Partial<NotificationPreferences> & Record<string, unknown>
) {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...bearerHeader(token),
  };
  return apiFetch("/notification-prefs", notificationPrefsSchema, {
    method: "PUT",
    headers,
    body: JSON.stringify(payload),
  });
}
