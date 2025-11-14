import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Button from "../components/ui/Button.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import { getApiBase } from "../utils/apiBase";

const API_BASE = getApiBase();

export default function Register() {
  const navigate = useNavigate();
  const [tenantName, setTenantName] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [registered, setRegistered] = useState(null);

  const readError = async (res) => {
    try {
      const body = await res.json();
      return body?.detail || body?.message || `HTTP ${res.status}`;
    } catch {
      return `HTTP ${res.status}`;
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tenant_name: tenantName,
          username,
          email,
          password,
        }),
      });
      if (!res.ok) {
        throw new Error(await readError(res));
      }
      const data = await res.json();
      setRegistered(data);
    } catch (err) {
      setError(err?.message || "Registration failed");
    } finally {
      setSubmitting(false);
    }
  };

  if (registered) {
    return (
      <div className="bg-neutral flex min-h-screen flex-col items-center justify-center px-4">
        <div className="w-full max-w-lg rounded-xl bg-surface p-8 shadow-lg text-center space-y-4">
          <h1 className="text-3xl font-semibold text-primary-text">Welcome to Tenantra</h1>
          <p className="text-sm text-secondary-text">
            Tenant <strong>{registered.tenant_slug}</strong> is ready. You can now sign in with the credentials you created.
          </p>
          <Button onClick={() => navigate("/login")} className="w-full">
            Go to Login
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-neutral flex min-h-screen flex-col items-center justify-center px-4">
      <div className="w-full max-w-lg rounded-xl bg-surface p-8 shadow-lg">
        <div className="mb-6 text-center space-y-2">
          <h1 className="text-3xl font-semibold text-primary-text">Create your Tenantra tenant</h1>
          <p className="text-sm text-secondary-text">Provision a dedicated workspace for your team in minutes.</p>
        </div>
        <form className="space-y-4" onSubmit={handleSubmit}>
          <ErrorBanner message={error} onClose={() => setError("")} />
          <div>
            <label className="block text-sm font-medium text-primary-text">Organization or Tenant Name</label>
            <input
              type="text"
              required
              value={tenantName}
              onChange={(event) => setTenantName(event.target.value)}
              className="mt-1 block w-full rounded-md border border-border-color px-4 py-3 text-sm text-primary-text focus:border-primary focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-primary-text">Work Email</label>
            <input
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="mt-1 block w-full rounded-md border border-border-color px-4 py-3 text-sm text-primary-text focus:border-primary focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-primary-text">Username</label>
            <input
              type="text"
              autoComplete="username"
              required
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              className="mt-1 block w-full rounded-md border border-border-color px-4 py-3 text-sm text-primary-text focus:border-primary focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-primary-text">Password</label>
            <input
              type="password"
              autoComplete="new-password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="mt-1 block w-full rounded-md border border-border-color px-4 py-3 text-sm text-primary-text focus:border-primary focus:outline-none"
            />
            <p className="mt-1 text-xs text-secondary-text">
              Use at least 8 characters with upper/lowercase letters, a number, and a symbol.
            </p>
          </div>
          <Button type="submit" className="w-full" disabled={submitting}>
            {submitting ? "Creating…" : "Create Tenant"}
          </Button>
          <p className="text-center text-sm text-secondary-text">
            Already have an account?{" "}
            <button type="button" className="text-primary hover:underline" onClick={() => navigate("/login")}>
              Sign in
            </button>
          </p>
        </form>
      </div>
    </div>
  );
}
