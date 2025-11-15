import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import ErrorBanner from "../components/ErrorBanner.jsx";
import Button from "../components/ui/Button.jsx";
import { getApiBase } from "../utils/apiBase";

const API_BASE = getApiBase();

export default function ForgotPassword() {
  const [identifier, setIdentifier] = useState("");
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setSuccess("");
    setSubmitting(true);
    try {
      const payload = identifier.includes("@") ? { email: identifier } : { username: identifier };
      const res = await fetch(`${API_BASE}/auth/forgot-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body?.detail || body?.message || "Unable to start reset flow");
      }
      setSuccess("If the account exists, a password reset link was sent.");
      setIdentifier("");
    } catch (err) {
      setError(err?.message || "Unable to send reset instructions");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-[radial-gradient(circle_at_top,_rgba(79,70,229,0.18),_transparent_60%)]">
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-[rgba(17,24,39,0.95)] via-[rgba(17,24,39,0.8)] to-[rgba(22,163,74,0.25)]" />
      <div className="relative z-10 flex min-h-screen items-center justify-center px-6 py-12">
        <div className="w-full max-w-lg rounded-3xl border border-white/30 bg-white/95 p-10 shadow-[var(--tena-shadow-card)]">
          <h1 className="text-3xl font-semibold text-slate-900">Forgot password</h1>
          <p className="mt-2 text-sm text-slate-500">Enter your username or email address to receive reset instructions.</p>
          <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
            <ErrorBanner message={error} onClose={() => setError("")} />
            {success && (
              <div className="rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{success}</div>
            )}
            <div>
              <label className="mb-2 block text-sm font-semibold text-slate-600">Username or email</label>
              <input
                type="text"
                value={identifier}
                onChange={(event) => setIdentifier(event.target.value)}
                className="w-full rounded-2xl border border-slate-200 px-4 py-3 text-base focus:border-[var(--tena-primary)] focus:ring-2 focus:ring-[rgba(17,24,39,0.2)]"
                required
              />
            </div>
            <Button type="submit" className="w-full" disabled={submitting}>
              {submitting ? "Sending…" : "Send reset link"}
            </Button>
            <button type="button" onClick={() => navigate("/login")} className="w-full text-sm text-[var(--tena-primary)] hover:underline">
              Back to login
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
