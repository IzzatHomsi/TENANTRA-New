import React, { useEffect, useState, useCallback } from "react";
import { getApiBase } from "../utils/apiBase";
import Card from "../components/ui/Card.jsx";
import Button from "../components/ui/Button.jsx";
import { useUIStore } from "../store/uiStore";
import { fetchFeatureFlags } from "../api/features";

const API_BASE = getApiBase();

const authHeaders = (token) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`,
});

export default function FeatureFlags() {
  const { featureFlags, setFeatureFlags } = useUIStore();
  const [features, setFeatures] = useState(featureFlags || {});
  const [scope, setScope] = useState("tenant");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [toast, setToast] = useState("");

  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  const loadFeatures = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const data = await fetchFeatureFlags(token);
      setFeatures(data || {});
      setFeatureFlags(data || {});
    } catch (e) {
      setError(e.message || "Failed to load features");
    } finally {
      setLoading(false);
    }
  }, [token, setFeatureFlags]);

  useEffect(() => {
    loadFeatures();
  }, [loadFeatures]);

  const saveFeatures = async () => {
    setSaving(true);
    setError("");
    try {
      const url = scope === "global" ? `${API_BASE}/admin/settings` : `${API_BASE}/admin/settings/tenant`;
      const res = await fetch(url, {
        method: "PUT",
        headers: authHeaders(token),
        body: JSON.stringify({ features }),
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      setToast("Saved");
      setTimeout(() => setToast(""), 1500);
      loadFeatures();
    } catch (e) {
      setError(e.message || "Failed to save feature flags");
    } finally {
      setSaving(false);
    }
  };

  const toggleFeature = (key) => {
    setFeatures((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const featureKeys = Object.keys(features).sort();

  return (
    <div className="bg-facebook-gray p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Feature Flags</h1>
        <p className="mt-2 text-sm text-gray-600">
          Manage platform feature visibility globally or per-tenant (overrides).
        </p>
      </header>

      {error && <div className="mb-4 rounded-md bg-red-100 p-4 text-red-700">{error}</div>}
      {toast && <div className="mb-4 rounded-md bg-green-100 p-4 text-green-700">{toast}</div>}

      <Card>
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <label className="text-sm font-medium text-gray-700">Scope</label>
            <select
              value={scope}
              onChange={(e) => setScope(e.target.value)}
              className="rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
            >
              <option value="tenant">Tenant</option>
              <option value="global">Global</option>
            </select>
          </div>
          <Button onClick={saveFeatures} disabled={saving || loading}>
            {saving ? "Saving..." : "Save"}
          </Button>
        </div>

        {loading ? (
          <div className="py-12 text-center text-gray-500">Loading...</div>
        ) : (
          <ul className="divide-y divide-gray-200">
            {featureKeys.length === 0 ? (
              <li className="py-4 text-center text-sm text-gray-500">No features discovered</li>
            ) : (
              featureKeys.map((key) => (
                <li key={key} className="flex items-center justify-between py-4">
                  <div className="text-sm font-medium text-gray-900">{key}</div>
                  <label className="relative inline-flex cursor-pointer items-center">
                    <input
                      type="checkbox"
                      checked={!!features[key]}
                      onChange={() => toggleFeature(key)}
                      className="sr-only peer"
                    />
                    <div className="peer h-6 w-11 rounded-full bg-gray-200 after:absolute after:top-[2px] after:left-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-gray-300 after:bg-white after:transition-all after:content-[''] peer-checked:bg-facebook-blue peer-checked:after:translate-x-full peer-checked:after:border-white peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300"></div>
                    <span className="ml-3 text-sm font-medium text-gray-900">
                      {features[key] ? "Enabled" : "Disabled"}
                    </span>
                  </label>
                </li>
              ))
            )}
          </ul>
        )}
      </Card>
    </div>
  );
}
