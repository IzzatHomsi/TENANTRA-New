import { useMemo } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchGlobalSettings, updateGlobalSettings } from "../api/adminSettings.ts";
import { useAuth } from "../context/AuthContext.jsx";

const TENANT_STORAGE_KEY = "tenant_id";

const getTenantId = () =>
  typeof window !== "undefined" ? localStorage.getItem(TENANT_STORAGE_KEY) : null;

const adminSettingsKey = (tenantId) => ["admin-settings", tenantId || "global"];

export function useAdminSettingsQuery() {
  const { token, signOut } = useAuth();
  const tenantId = useMemo(() => getTenantId(), []);

  return useQuery({
    queryKey: adminSettingsKey(tenantId),
    enabled: Boolean(token),
    queryFn: async () => {
      try {
        return await fetchGlobalSettings(token, tenantId);
      } catch (error) {
        if (error?.status === 401) {
          signOut?.();
        }
        throw error;
      }
    },
  });
}

export function useUpdateAdminSettingsMutation() {
  const { token, signOut } = useAuth();
  const queryClient = useQueryClient();
  const tenantId = useMemo(() => getTenantId(), []);

  return useMutation({
    mutationFn: async (payload) => {
      try {
        return await updateGlobalSettings(token, payload, tenantId);
      } catch (error) {
        if (error?.status === 401) {
          signOut?.();
        }
        throw error;
      }
    },
    onSuccess: (data) => {
      queryClient.setQueryData(adminSettingsKey(tenantId), data);
    },
  });
}

export { adminSettingsKey };
