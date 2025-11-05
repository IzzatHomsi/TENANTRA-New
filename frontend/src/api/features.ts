import { z } from "zod";
import { apiFetch } from "../lib/apiClient";
import { useUIStore } from "../store/uiStore";

const featuresSchema = z.record(z.boolean());

export async function fetchFeatureFlags(token: string | null) {
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const features = await apiFetch("/features", featuresSchema, { headers });
  useUIStore.getState().setFeatureFlags(features);
  return features;
}
