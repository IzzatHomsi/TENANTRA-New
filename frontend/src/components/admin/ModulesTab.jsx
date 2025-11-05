import React, { useEffect, useState } from "react";
import Button from "../ui/Button.jsx";

export default function ModulesTab({ headers }) {
  const [list, setList] = useState([]);
  const [saving, setSaving] = useState(false);
  const [groupBy, setGroupBy] = useState("category");

  useEffect(() => {
    (async () => {
      try {
        const r = await fetch("/api/admin/modules", { headers });
        if (r.ok) {
          setList(await r.json());
        }
      } catch {}
    })();
  }, [headers]);

  const toggle = (id) => {
    setList((prev) =>
      prev.map((m) => (m.id === id ? { ...m, enabled: !m.enabled } : m))
    );
  };

  const save = async () => {
    setSaving(true);
    try {
      const enable = list.filter((m) => m.enabled).map((m) => m.id);
      const disable = list.filter((m) => !m.enabled).map((m) => m.id);
      await fetch("/api/admin/modules/bulk", {
        method: "PUT",
        headers,
        body: JSON.stringify({ enable, disable }),
      });
    } finally {
      setSaving(false);
    }
  };

  const grouped = (() => {
    if (groupBy === "none") return { All: list };
    const map = {};
    for (const m of list) {
      const key =
        groupBy === "category"
          ? m.category || "Uncategorized"
          : `Phase ${m.phase ?? "-"}`;
      (map[key] || (map[key] = [])).push(m);
    }
    return map;
  })();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-primary-text">Modules & Plans</h3>
        <div className="flex items-center space-x-4">
          <select
            value={groupBy}
            onChange={(e) => setGroupBy(e.target.value)}
            className="rounded-md border border-border-color px-3 py-2 text-sm shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40"
          >
            <option value="category">Category</option>
            <option value="phase">Phase</option>
            <option value="none">None</option>
          </select>
          <Button onClick={save} disabled={saving}>
            {saving ? "Saving..." : "Save"}
          </Button>
        </div>
      </div>
      <div className="space-y-6">
        {Object.entries(grouped).map(([label, items]) => (
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
