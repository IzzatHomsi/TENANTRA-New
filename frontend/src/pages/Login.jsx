import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";

const highlights = [
  { label: "Active Tenants", value: "42" },
  { label: "Agents Reporting In", value: "318" },
  { label: "Controls Automated", value: "900+" },
];

const playbook = [
  "Unified inventory, compliance, and remediation cockpit",
  "Tenant-aware RBAC and encryption everywhere",
  "Dashboards powered by Prometheus and Grafana",
];

export default function Login() {
  const { signIn, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location?.state && location.state.from && location.state.from.pathname) || "/dashboard";

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, from, navigate]);

  const handleLogin = async (event) => {
    event.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      await signIn({ username, password });
      navigate(from, { replace: true });
    } catch (err) {
      setError(err?.message || "Login failed");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top,_rgba(79,70,229,0.18),_transparent_60%)]">
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-[rgba(17,24,39,0.95)] via-[rgba(17,24,39,0.8)] to-[rgba(22,163,74,0.25)]" />
      <div className="relative z-10 flex min-h-screen flex-col lg:flex-row">
        <section className="hidden w-full flex-col justify-between px-12 py-14 text-white lg:flex lg:w-1/2">
          <div>
            <p className="inline-flex items-center rounded-full bg-white/10 px-4 py-1 text-xs uppercase tracking-wide text-white/80">
              Tenantra Security Cloud
            </p>
            <h1 className="mt-6 text-5xl font-semibold leading-tight">Unified IT discovery, compliance, and remediation</h1>
            <p className="mt-4 text-lg text-white/80">
              Real-time visibility for every tenant, intelligent alerting, and compliance automation that looks and feels like
              Tenantra.be.
            </p>
          </div>
          <div className="grid grid-cols-3 gap-6 text-center">
            {highlights.map((item) => (
              <div key={item.label} className="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur">
                <p className="text-3xl font-semibold">{item.value}</p>
                <p className="text-xs uppercase tracking-wide text-white/70">{item.label}</p>
              </div>
            ))}
          </div>
          <div className="space-y-3 rounded-2xl border border-white/10 bg-black/20 p-6 backdrop-blur">
            <p className="text-sm font-semibold uppercase tracking-wider text-white/70">Platform Highlights</p>
            <ul className="space-y-2 text-base text-white/85">
              {playbook.map((entry) => (
                <li key={entry} className="flex items-start gap-3">
                  <span className="mt-1 h-2 w-2 rounded-full bg-emerald-400" />
                  <span>{entry}</span>
                </li>
              ))}
            </ul>
          </div>
        </section>

        <section className="flex w-full items-center justify-center px-6 py-12 sm:px-10 lg:w-1/2 lg:bg-white/5 lg:py-16">
          <div className="w-full max-w-md rounded-3xl border border-white/30 bg-white/90 p-10 shadow-[var(--tena-shadow-card)] backdrop-blur-md">
            <header className="mb-8 text-center">
              <p className="text-xs font-semibold uppercase tracking-[0.3em] text-slate-500">Welcome back</p>
              <h2 className="mt-3 text-3xl font-semibold text-slate-900">Sign in to Tenantra</h2>
              <p className="mt-2 text-sm text-slate-500">Secure ops cockpit for multi-tenant environments.</p>
            </header>
            <form onSubmit={handleLogin} className="space-y-6">
              <ErrorBanner message={error} onClose={() => setError("")} />
              <div>
                <label className="mb-2 block text-sm font-semibold text-slate-600" htmlFor="username">
                  Username
                </label>
                <input
                  id="username"
                  className="field-control w-full rounded-2xl border border-slate-200 px-4 py-3 text-base focus:border-[var(--tena-primary)] focus:ring-2 focus:ring-[rgba(17,24,39,0.2)]"
                  type="text"
                  autoComplete="username"
                  value={username}
                  onChange={(event) => setUsername(event.target.value)}
                  placeholder="Username"
                  required
                />
              </div>
              <div>
                <label className="mb-2 block text-sm font-semibold text-slate-600" htmlFor="password">
                  Password
                </label>
                <input
                  id="password"
                  className="field-control w-full rounded-2xl border border-slate-200 px-4 py-3 text-base focus:border-[var(--tena-primary)] focus:ring-2 focus:ring-[rgba(17,24,39,0.2)]"
                  type="password"
                  autoComplete="current-password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="Password"
                  required
                />
              </div>
              <button
                type="submit"
                className="w-full rounded-2xl bg-[var(--tena-primary)] px-4 py-3 text-base font-semibold text-white transition hover:bg-slate-900 disabled:opacity-60"
                disabled={submitting}
              >
                {submitting ? "Logging in…" : "Login"}
              </button>
            </form>
            <div className="mt-6 flex items-center justify-between text-sm text-slate-600">
              <button type="button" className="font-semibold text-[var(--tena-primary)] hover:underline">
                Forgot password?
              </button>
              <button type="button" onClick={() => navigate("/register")} className="font-semibold text-[var(--tena-secondary)] hover:underline">
                Create account
              </button>
            </div>
            <div className="mt-10 rounded-2xl border border-slate-100 bg-slate-50/80 p-4 text-sm text-slate-600">
              <p className="font-semibold text-slate-800">Operational tip</p>
              <p className="mt-1">
                Use the seeded admin user (<span className="font-mono">admin / Admin@1234</span>) for local environments. Rotate credentials via the Admin
                Settings panel in production.
              </p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
