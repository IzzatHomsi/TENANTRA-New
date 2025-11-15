import React, { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import ErrorBanner from "../components/ErrorBanner.jsx";
import Button from "../components/ui/Button.jsx";
import { getApiBase } from "../utils/apiBase";

const API_BASE = getApiBase();

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const initialToken = searchParams.get("token") || "";
  const [token, setToken] = useState(initialToken);
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setSuccess("");
    if (!token) {
      setError("Reset token is required.");
      return;
    }
    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }
    setSubmitting(true);
    try {
      const res = await fetch(`${API_BASE}/auth/reset-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, new_password: password }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body?.detail || body?.message || "Failed to reset password");
      }
      setSuccess("Password updated. You can now sign in with your new password.");
      setPassword("");
      setConfirm("");
    } catch (err) {
      setError(err?.message || "Unable to reset password");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-[radial-gradient(circle_at_top,_rgba(79,70,229,0.18),_transparent_60%)]">
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-[rgba(17,24,39,0.95)] via-[rgba(17,24,39,0.8)] to-[rgba(22,163,74,0.25)]" />
      <div className="relative z-10 flex min-h-screen items-center justify-center px-6 py-12">
        <div className="w-full max-w-lg rounded-3xl border border-white/30 bg-white/95 p-10 shadow-[var(--tena-shadow-card)]">
          <h1 className="text-3xl font-semibold text-slate-900">Reset password</h1>
          <p className="mt-2 text-sm text-slate-500">Paste the token from your email, set a new password, and get back to work.</p>
          <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
            <ErrorBanner message={error} onClose={() => setError("")} />
            {success && (
              <div className="rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{success}</div>
            )}
            <div>
              <label className="mb-2 block text-sm font-semibold text-slate-600">Reset token</label>
              <input
                type="text"
                value={token}
                onChange={(event) => setToken(event.target.value)}
                className="w-full rounded-2xl border border-slate-200 px-4 py-3 text-base focus:border-[var(--tena-primary)] focus:ring-2 focus:ring-[rgba(17,24,39,0.2)]"
                required
              />
            </div>
            <div>
              <label className="mb-2 block text-sm font-semibold text-slate-600">New password</label>
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="w-full rounded-2xl border border-slate-200 px-4 py-3 text-base focus:border-[var(--tena-primary)] focus:ring-2 focus:ring-[rgba(17,24,39,0.2)]"
                required
              />
            </div>
            <div>
              <label className="mb-2 block text-sm font-semibold text-slate-600">Confirm password</label>
              <input
                type="password"
                value={confirm}
                onChange={(event) => setConfirm(event.target.value)}
                className="w-full rounded-2xl border border-slate-200 px-4 py-3 text-base focus:border-[var(--tena-primary)] focus:ring-2 focus:ring-[rgba(17,24,39,0.2)]"
                required
              />
            </div>
            <Button type="submit" className="w-full" disabled={submitting}>
              {submitting ? "Updating…" : "Update password"}
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
