import { useQuery } from "@tanstack/react-query";
import { getApiBase } from "../utils/apiBase";

export const SUPPORT_SETTINGS_QUERY_KEY = ["support-settings-public"];

async function fetchSupportSettings({ signal, baseUrl }) {
  const apiBase = baseUrl ?? getApiBase();
  const response = await fetch(`${apiBase}/support/settings/public`, { signal });
  if (!response.ok) {
    const error = new Error(`Failed to load public settings (HTTP ${response.status}).`);
    error.status = response.status;
    throw error;
  }
  return response.json();
}

export function useSupportSettings(options = {}) {
  return useQuery({
    queryKey: SUPPORT_SETTINGS_QUERY_KEY,
    queryFn: ({ signal }) => fetchSupportSettings({ signal }),
    staleTime: 5 * 60_000,
    ...options,
  });
}

export async function prefetchSupportSettings(queryClient, baseUrl) {
  try {
    await queryClient.prefetchQuery({
      queryKey: SUPPORT_SETTINGS_QUERY_KEY,
      queryFn: ({ signal }) => fetchSupportSettings({ signal, baseUrl }),
    });
  } catch (error) {
    console.warn("[SSR] Unable to prefetch public settings", error);
  }
}
