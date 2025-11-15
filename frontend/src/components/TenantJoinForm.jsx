import React, { useCallback, useEffect, useMemo, useState } from "react";
import ErrorBanner from "./ErrorBanner.jsx";
import Button from "./ui/Button.jsx";
import { getApiBase } from "../utils/apiBase";

const API_BASE = getApiBase();

export default function TenantJoinForm() {
  const [lookup, setLookup] = useState("");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [options, setOptions] = useState([]);
  const [selected, setSelected] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!lookup || lookup.length < 2) {
      setOptions([]);
      return;
    }
    const controller = new AbortController();
    const fetchSuggestions = async () => {
      try {
        const res = await fetch(`${API_BASE}/tenants/search?q=${encodeURIComponent(lookup)}`, {
          signal: controller.signal,
        });
        if (!res.ok) throw new Error("Search failed");
        const data = await res.json();
        setOptions(data || []);
      } catch {
        if (!controller.signal.aborted) {
          setOptions([]);
        }
      }
    };
    fetchSuggestions();
    return () => controller.abort();
  }, [lookup]);

  const onSelect = useCallback(
    (tenant) => {
      setSelected(tenant);
      setLookup(tenant.name || tenant.slug || tenant.id);
    },
    [setSelected]
  );

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setSuccess("");
    setSubmitting(true);
    try {
      const tenantIdentifier = selected?.slug || selected?.id || lookup;
      if (!tenantIdentifier) throw new Error("Select a tenant to join");
      const res = await fetch(`${API_BASE}/tenants/join-requests`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tenant_identifier: tenantIdentifier,
          full_name: name,
          email,
          message,
        }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body?.detail || body?.message || "Request failed");
      }
      setSuccess("Your request has been submitted. We'll notify the tenant admins.");
      setName("");
      setEmail("");
      setMessage("");
      setSelected(null);
    } catch (err) {
      setError(err?.message || "Unable to submit request");
    } finally {
      setSubmitting(false);
    }
  };

  const suggestionList = useMemo(() => {
    if (!options.length) return null;
    return (
      <ul className="mt-2 rounded-xl border border-slate-200 bg-white shadow-lg">
        {options.map((tenant) => (
          <li key={tenant.id} className="border-b border-slate-100 last:border-none">
            <button
              type="button"
              onClick={() => onSelect(tenant)}
              className="w-full px-4 py-2 text-left text-sm text-slate-700 hover:bg-slate-50"
            >
              <span className="font-semibold">{tenant.name}</span>
              <span className="ml-2 text-xs uppercase tracking-wide text-slate-400">{tenant.slug}</span>
            </button>
          </li>
        ))}
      </ul>
    );
  }, [options, onSelect]);

  return (
    <div className="rounded-3xl border border-white/30 bg-white/90 p-6 shadow-[var(--tena-shadow-card)] backdrop-blur">
      <h3 className="text-xl font-semibold text-slate-900">Request to join an existing tenant</h3>
      <p className="mt-2 text-sm text-slate-500">
        Search for your organization and send a join request to the administrators.
      </p>
      <form className="mt-4 space-y-4" onSubmit={handleSubmit}>
        <ErrorBanner message={error} onClose={() => setError("")} />
        {success && (
          <div className="rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
            {success}
          </div>
        )}
        <div>
          <label className="mb-2 block text-sm font-semibold text-slate-600">Tenant name or slug</label>
          <input
            type="text"
            value={lookup}
            onChange={(event) => {
              setLookup(event.target.value);
              setSelected(null);
            }}
            className="w-full rounded-2xl border border-slate-200 px-4 py-3 text-base focus:border-[var(--tena-primary)] focus:ring-2 focus:ring-[rgba(17,24,39,0.2)]"
            placeholder="acme-security"
            required
          />
          {suggestionList}
        </div>
        <div>
          <label className="mb-2 block text-sm font-semibold text-slate-600">Your name</label>
          <input
            type="text"
            value={name}
            onChange={(event) => setName(event.target.value)}
            className="w-full rounded-2xl border border-slate-200 px-4 py-3 text-base focus:border-[var(--tena-primary)] focus:ring-2 focus:ring-[rgba(17,24,39,0.2)]"
            required
          />
        </div>
        <div>
          <label className="mb-2 block text-sm font-semibold text-slate-600">Work email</label>
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="w-full rounded-2xl border border-slate-200 px-4 py-3 text-base focus:border-[var(--tena-primary)] focus:ring-2 focus:ring-[rgba(17,24,39,0.2)]"
            required
          />
        </div>
        <div>
          <label className="mb-2 block text-sm font-semibold text-slate-600">Why do you need access?</label>
          <textarea
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            rows={3}
            className="w-full rounded-2xl border border-slate-200 px-4 py-3 text-base focus:border-[var(--tena-primary)] focus:ring-2 focus:ring-[rgba(17,24,39,0.2)]"
          />
        </div>
        <Button type="submit" className="w-full" disabled={submitting || !lookup}>
          {submitting ? "Submitting…" : "Send Join Request"}
        </Button>
      </form>
    </div>
  );
}
