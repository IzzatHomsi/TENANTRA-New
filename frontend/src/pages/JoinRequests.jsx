import React, { useCallback, useEffect, useState } from "react";
import ErrorBanner from "../components/ErrorBanner.jsx";
import Button from "../components/ui/Button.jsx";
import { useAuth } from "../context/AuthContext.jsx";
import { getApiBase } from "../utils/apiBase";

const API_BASE = getApiBase();

export default function JoinRequests() {
  const { token } = useAuth();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionError, setActionError] = useState("");

  const fetchItems = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/admin/tenant-join-requests`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setItems(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err?.message || "Failed to load join requests");
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  const decide = async (requestId, decision) => {
    setActionError("");
    try {
      const res = await fetch(`${API_BASE}/admin/tenant-join-requests/${requestId}/decision`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ decision }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body?.detail || body?.message || "Unable to update request");
      }
      const updated = await res.json();
      setItems((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
    } catch (err) {
      setActionError(err?.message || "Failed to update request");
    }
  };

  return (
    <div className="space-y-6">
      <header className="rounded-3xl border border-white/10 bg-white/70 px-6 py-5 shadow-[var(--tena-shadow-card)] backdrop-blur">
        <h1 className="text-2xl font-semibold text-slate-900">Tenant Join Requests</h1>
        <p className="mt-1 text-sm text-slate-500">Approve or deny requests to join your tenant.</p>
      </header>
      <ErrorBanner message={error || actionError} onClose={() => { setError(""); setActionError(""); }} />
      <div className="overflow-hidden rounded-3xl border border-white/20 bg-white/90 shadow-[var(--tena-shadow-card)]">
        <table className="min-w-full divide-y divide-slate-200">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">Name</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">Email</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">Message</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">Status</th>
              <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-500">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-sm">
            {loading && (
              <tr>
                <td colSpan={5} className="px-4 py-6 text-center text-slate-500">
                  Loading…
                </td>
              </tr>
            )}
            {!loading && !items.length && (
              <tr>
                <td colSpan={5} className="px-4 py-6 text-center text-slate-500">
                  No requests yet.
                </td>
              </tr>
            )}
            {items.map((item) => (
              <tr key={item.id}>
                <td className="px-4 py-4 font-medium text-slate-900">{item.full_name}</td>
                <td className="px-4 py-4 text-slate-600">{item.email}</td>
                <td className="px-4 py-4 text-slate-600">{item.message || "—"}</td>
                <td className="px-4 py-4">
                  <span
                    className={`rounded-full px-3 py-1 text-xs font-semibold ${
                      item.status === "approved"
                        ? "bg-emerald-50 text-emerald-700"
                        : item.status === "denied"
                          ? "bg-rose-50 text-rose-700"
                          : "bg-slate-100 text-slate-600"
                    }`}
                  >
                    {item.status}
                  </span>
                </td>
                <td className="px-4 py-4 text-right">
                  {item.status === "pending" ? (
                    <div className="flex justify-end gap-2">
                      <Button variant="outline" size="sm" onClick={() => decide(item.id, "denied")}>
                        Deny
                      </Button>
                      <Button size="sm" onClick={() => decide(item.id, "approved")}>
                        Approve
                      </Button>
                    </div>
                  ) : (
                    <span className="text-xs text-slate-400">{item.decision_note || "Processed"}</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
