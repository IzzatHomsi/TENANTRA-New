import { z } from "zod";
import { getApiBase } from "../utils/apiBase";

const errorSchema = z.object({ detail: z.union([z.string(), z.object({}).passthrough()]).optional() }).passthrough();

export async function apiFetch<T>(
  path: string,
  schema: z.ZodType<T>,
  options: RequestInit = {}
): Promise<T> {
  const base = getApiBase();
  const res = await fetch(`${base}${path}`, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });
  if (!res.ok) {
    let message = `HTTP ${res.status}`;
    try {
      const json = await res.json();
      const parsed = errorSchema.parse(json);
      if (parsed.detail) {
        message = typeof parsed.detail === "string" ? parsed.detail : JSON.stringify(parsed.detail);
      }
    } catch {
      // best effort
    }
    const err = new Error(message);
    // @ts-expect-error augment error
    err.status = res.status;
    throw err;
  }
  const data = await res.json();
  return schema.parse(data);
}

export function bearerHeader(token: string | null | undefined) {
  return token
    ? {
        Authorization: `Bearer ${token}`,
      }
    : {};
}
