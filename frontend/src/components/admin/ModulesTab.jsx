import React, { useEffect, useState, memo, useMemo, useCallback } from "react";
import Button from "../ui/Button.jsx";
import { fetchAdminModules, updateAdminModules } from "../../api/adminModules.ts";

function ModulesTab({ headers }) {
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [saving, setSaving] = useState(false);
  const [actionNotice, setActionNotice] = useState("");
  const [groupBy, setGroupBy] = useState("category");

  useEffect(() => {
    let ignore = false;
    async function loadModules() {
      setLoading(true);
      setLoadError("");
      try {
        const data = await fetchAdminModules(headers);
        if (!ignore) {
          setList(Array.isArray(data) ? data : []);
        }
      } catch (error) {
        if (!ignore) {
          console.error("Failed to load admin modules", error);
          setLoadError("Unable to load modules right now.");
        }
      } finally {
        if (!ignore) {
          setLoading(false);
        }
      }
    }
    loadModules();
    return () => {
      ignore = true;
    };
  }, [headers]);

  const toggle = useCallback((id) => {
    setList((prev) => prev.map((m) => (m.id === id ? { ...m, enabled: !m.enabled } : m)));
  }, []);

  const save = useCallback(async () => {
    setSaving(true);
    setActionNotice("");
    try {
      const enable = list.filter((m) => m.enabled).map((m) => m.id);
      const disable = list.filter((m) => !m.enabled).map((m) => m.id);
      await updateAdminModules(headers, { enable, disable });
      setActionNotice("Changes saved successfully.");
    } catch (error) {
      setActionNotice(error instanceof Error ? error.message : "Unable to save module toggles.");
    } finally {
      setSaving(false);
    }
  }, [headers, list]);

  const grouped = useMemo(() => {
    if (groupBy === "none") return { All: list };
    const map = {};
    for (const m of list) {
      const key = groupBy === "category" ? m.category || "Uncategorized" : `Phase ${m.phase ?? "-"}`;
      (map[key] || (map[key] = [])).push(m);
    }
    return map;
  }, [groupBy, list]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-primary-text">Modules & Plans</h3>
        <div className="flex items-center space-x-4">
          <select
            value={groupBy}
            onChange={(e) => setGroupBy(e.target.value)}
            className="rounded-md border border-border-color px-3 py-2 text-sm shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40"
            disabled={loading}
          >
            <option value="category">Category</option>
            <option value="phase">Phase</option>
            <option value="none">None</option>
          </select>
          <Button onClick={save} disabled={saving || loading}>
            {saving ? "Saving..." : "Save"}
          </Button>
        </div>
      </div>
      {loadError && (
        <div className="rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-700">
          {loadError}
        </div>
      )}
      {actionNotice && !saving && (
        <div
          className={`rounded-md border p-3 text-sm ${/fail|unable|error|unauthor/i.test(actionNotice)
            ? "border-red-200 bg-red-50 text-red-700"
            : "border-emerald-200 bg-emerald-50 text-emerald-700"}`}
        >
          {actionNotice}
        </div>
      )}
      {loading && !loadError && (
        <div className="text-sm text-secondary-text">Loading modules…</div>
      )}
      <div className="space-y-6">
        {!loading &&
          Object.entries(grouped).map(([label, items]) => (
            <div key={label}>
              <h4 className="mb-4 text-base font-medium text-primary-text">{label}</h4>
              <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                {items.map((m) => (
                  <label
                    key={m.id}
                    className="flex items-center rounded-lg border border-border-color bg-surface p-4 shadow-sm"
                  >
                    <input
                      type="checkbox"
                      checked={!!m.enabled}
                      onChange={() => toggle(m.id)}
                      className="h-4 w-4 rounded border-border-color text-primary focus:ring-primary"
                      disabled={saving}
                    />
                    <div className="ml-4">
                      <div className="text-sm font-medium text-primary-text">{m.name}</div>
                      <div className="text-xs text-secondary-text">
                        Phase {m.phase ?? "-"} &middot; {m.category ?? "-"}
                      </div>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          ))}
      </div>
    </div>
  );
}

export default memo(ModulesTab);
