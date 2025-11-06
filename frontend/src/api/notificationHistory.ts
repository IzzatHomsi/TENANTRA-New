import { z } from "zod";
import { apiFetch, bearerHeader } from "../lib/apiClient";

const historyEntrySchema = z.object({
  id: z.union([z.string(), z.number()]).optional(),
  sent_at: z.string().optional().default(""),
  channel: z.string().optional().default(""),
  recipient: z.string().optional().default(""),
  subject: z.string().optional().default(""),
  status: z.string().optional().default("queued"),
  error: z.string().nullable().optional().transform((value) => value || null),
});

const historyListSchema = z.array(historyEntrySchema);

export async function fetchNotificationHistory(
  token: string | null,
  params: { channel?: string; recipient?: string; limit?: number | string } = {}
) {
  const headers: Record<string, string> = {
    ...bearerHeader(token),
  };
  const search = new URLSearchParams();
  if (params.channel) search.set("channel", params.channel);
  if (params.recipient) search.set("recipient", params.recipient);
  if (params.limit) search.set("limit", String(params.limit));
  const query = search.toString();
  const path = query ? `/notification-history?${query}` : "/notification-history";
  return apiFetch(path, historyListSchema, { headers });
}
