import React, { useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import Card from "../components/ui/Card.jsx";
import Button from "../components/ui/Button.jsx";
import { NAV_CONFIG, getLocalFeatures } from "../config/nav.js";
import { useAuth } from "../context/AuthContext.jsx";

function flattenNav(role, features) {
  const items = [];
  function walk(list) {
    for (const n of list) {
      if (n.type === "divider") continue;
      if (n.type === "section" && Array.isArray(n.children)) {
        walk(n.children);
      } else if (n.type === "item") {
        if (n.roles && n.roles.length && !n.roles.includes(role || "")) continue;
        const enabled = typeof n.enabled === "function" ? !!n.enabled({ role, features }) : n.enabled !== false;
        if (!enabled) continue;
        items.push({ to: n.to, label: n.label });
      }
    }
  }
  walk(NAV_CONFIG);
  return items;
}

export default function Search() {
  const navigate = useNavigate();
  const { search } = useLocation();
  const params = new URLSearchParams(search);
  const [q, setQ] = useState(params.get("q") || "");
  const { role } = useAuth();
  const features = getLocalFeatures();

  const items = useMemo(() => flattenNav(role, features), [role, features]);
  const filtered = useMemo(() => {
    const s = (q || "").toLowerCase();
    if (!s) return items;
    return items.filter((i) => String(i.label || "").toLowerCase().includes(s));
  }, [q, items]);

  return (
    <div className="bg-facebook-gray p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Search</h1>
        <p className="mt-2 text-sm text-gray-600">Find pages and jump quickly.</p>
      </header>

      <Card className="mb-8">
        <div className="flex space-x-4">
          <input
            autoFocus
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Type to filter..."
            className="w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          />
          <Button onClick={() => {
            if (filtered[0]) navigate(filtered[0].to);
          }}>Go</Button>
        </div>
      </Card>

      <div className="space-y-4">
        {filtered.length > 0 ? (
          filtered.map((i) => (
            <Card key={i.to} className="hover:shadow-lg">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium text-gray-900">{i.label}</div>
                  <div className="text-sm text-gray-500">{i.to}</div>
                </div>
                <Button variant="outline" onClick={() => navigate(i.to)}>Open</Button>
              </div>
            </Card>
          ))
        ) : (
          <Card>
            <p className="text-center text-gray-500">No matches.</p>
          </Card>
        )}
      </div>
    </div>
  );
}