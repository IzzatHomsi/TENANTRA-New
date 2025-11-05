import React, { useEffect, useState } from "react";
import { getApiBase } from "../utils/apiBase";
import Card from "../components/ui/Card.jsx";
import Button from "../components/ui/Button.jsx";

const API_BASE = getApiBase();

export default function Onboarding() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [mode, setMode] = useState("single");
  const [tenantName, setTenantName] = useState("");
  const [tenantSlug, setTenantSlug] = useState("");
  const [msg, setMsg] = useState("");

  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const headers = token ? { Authorization: `Bearer ${token}`, "Content-Type": "application/json" } : { "Content-Type": "application/json" };

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API_BASE}/admin/settings`, { headers });
        if (res.ok) {
          const items = await res.json();
          const map = Object.fromEntries(items.map((x) => [x.key, x.value]));
          if (map["tenant.mode"]) setMode(map["tenant.mode"]);
          if (map["onboarding.done"]) {
            window.location.assign("/app/dashboard");
            return;
          }
        }
      } catch {}
      setLoading(false);
    })();
  }, [headers]);

  async function handleSave() {
    setSaving(true);
    setMsg("");
    try {
      const body = { "tenant.mode": mode, "onboarding.done": true };
      const s = await fetch(`${API_BASE}/admin/settings`, { method: "PUT", headers, body: JSON.stringify(body) });
      if (!s.ok) throw new Error(`HTTP ${s.status}`);

      if (mode === "single") {
        const name = tenantName.trim() || "Default Tenant";
        const slug = tenantSlug.trim() || "default";
        try {
          await fetch(`${API_BASE}/admin/tenants`, { method: "POST", headers, body: JSON.stringify({ name, slug }) });
        } catch {}
      }

      setMsg("Onboarding complete. Redirecting...");
      setTimeout(() => window.location.assign("/app/dashboard"), 700);
    } catch (e) {
      setMsg(String(e?.message || e || "Failed to save"));
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <div className="p-8 text-center">Loading...</div>;

  return (
    <div className="flex min-h-screen items-center justify-center bg-facebook-gray p-8">
      <Card className="w-full max-w-2xl">
        <header className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-900">Tenantra Setup</h1>
          <p className="mt-2 text-sm text-gray-600">Choose tenant mode and create your first tenant if needed.</p>
        </header>

        <div className="space-y-6">
          <div>
            <h2 className="mb-4 text-xl font-bold text-gray-900">Mode</h2>
            <div className="flex space-x-4">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="mode"
                  checked={mode === "single"}
                  onChange={() => setMode("single")}
                  className="h-4 w-4 border-gray-300 text-facebook-blue focus:ring-facebook-blue"
                />
                <span className="ml-2 text-sm text-gray-700">Single tenant</span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="mode"
                  checked={mode === "multi"}
                  onChange={() => setMode("multi")}
                  className="h-4 w-4 border-gray-300 text-facebook-blue focus:ring-facebook-blue"
                />
                <span className="ml-2 text-sm text-gray-700">Multi-tenant (MSSP)</span>
              </label>
            </div>
          </div>

          {mode === "single" && (
            <div>
              <h2 className="mb-4 text-xl font-bold text-gray-900">Default Tenant</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Tenant Name</label>
                  <input
                    value={tenantName}
                    onChange={(e) => setTenantName(e.target.value)}
                    placeholder="Acme Corp"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Tenant Slug</label>
                  <input
                    value={tenantSlug}
                    onChange={(e) => setTenantSlug(e.target.value)}
                    placeholder="acme"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
                  />
                </div>
              </div>
            </div>
          )}

          {msg && <div className="rounded-md bg-green-100 p-4 text-green-700">{msg}</div>}

          <div className="flex justify-end">
            <Button onClick={handleSave} disabled={saving}>
              {saving ? "Saving..." : "Finish"}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}