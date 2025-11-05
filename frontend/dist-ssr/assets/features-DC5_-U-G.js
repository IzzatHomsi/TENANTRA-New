import { z } from "zod";
import { a as apiFetch, u as useUIStore } from "./apiClient-Y8eZ7muQ.js";
const featuresSchema = z.record(z.boolean());
async function fetchFeatureFlags(token) {
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const features = await apiFetch("/features", featuresSchema, { headers });
  useUIStore.getState().setFeatureFlags(features);
  return features;
}
export {
  fetchFeatureFlags as f
};
