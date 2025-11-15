import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import Button from "../components/ui/Button.jsx";

const featureHighlights = [
  {
    title: "Asset Discovery & Inventory",
    description:
      "Agent and agentless discovery with OS fingerprinting, role detection, and hybrid-cloud connectors for AWS, Azure, and GCP.",
  },
  {
    title: "Security & Compliance",
    description:
      "Continuous CIS/NIST/ISO enforcement, automated evidence lockers, and exportable audit packs built for MSP resale.",
  },
  {
    title: "Alerting & Incident Management",
    description: "Tenant-scoped rule builder, branded notifications, and outbound hooks for SIEM/ticketing pipelines.",
  },
  {
    title: "DevSecOps & Automation",
    description: "GitHub Actions CI/CD, Dockerized delivery, tenant-aware feature flags, and zero-downtime migrations.",
  },
  {
    title: "Monitoring & Analytics",
    description: "Prometheus metrics, Grafana dashboards, and health overlays surfaced directly inside the Tenantra shell.",
  },
  {
    title: "User & Tenant Management",
    description: "Schema-isolated tenants, RBAC with fine-grained controls, and billing/feature toggles for MSP programs.",
  },
];

const testimonials = [
  {
    quote: "Tenantra cut our audit prep from weeks to hours—the UI mirrors tenantra.be and keeps execs confident.",
    author: "CISO, Global MSP",
  },
  {
    quote: "The embedded Grafana and automated exports let us prove compliance without leaving the platform.",
    author: "Security Manager, Regulated SaaS",
  },
];

export default function Landing() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", company: "", plan: "growth" });
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/dashboard", { replace: true });
    }
  }, [isAuthenticated, navigate]);

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    try {
      const res = await fetch(`/api/support/walkthrough`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: form.name,
          email: form.email,
          company: form.company,
          plan: form.plan,
          referrer: window?.location?.href || undefined,
        }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setSubmitted(true);
    } catch (e) {
      console.error("Walkthrough request failed", e);
      alert("Could not submit request. Please try again later.");
    }
  }

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(79,70,229,0.2),_transparent_65%)] text-slate-900">
      <div className="relative isolate overflow-hidden bg-gradient-to-br from-slate-900 via-slate-900/85 to-emerald-700/30 text-white">
        <div className="absolute inset-y-0 right-0 -z-10 hidden w-1/2 bg-[radial-gradient(circle_at_top,_rgba(99,102,241,0.55),_transparent_60%)] lg:block" aria-hidden="true" />
        <header className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6 lg:px-10">
          <div className="flex items-center gap-3">
            <span className="inline-flex h-11 w-11 items-center justify-center rounded-2xl bg-white/10 text-lg font-semibold">T</span>
            <div>
              <p className="text-xs uppercase tracking-[0.4em] text-white/60">Tenantra</p>
              <p className="text-xl font-semibold">Security Cloud</p>
            </div>
          </div>
          <nav className="hidden items-center gap-6 text-sm font-semibold text-white/75 lg:flex">
            <Link to="/faq" className="hover:text-white">
              FAQ
            </Link>
            <Link to="/login" className="hover:text-white">
              Docs
            </Link>
            <a href="#features" className="hover:text-white">
              Capabilities
            </a>
            <Button as={Link} to="/login" variant="soft" className="bg-white text-slate-900 hover:bg-slate-100">
              Launch Console
            </Button>
          </nav>
        </header>

        <main className="mx-auto max-w-7xl px-6 pb-16 pt-10 lg:px-10 lg:pt-20">
          <section className="flex flex-col gap-12 lg:flex-row">
            <div className="flex-1 space-y-8">
              <p className="inline-flex items-center rounded-full bg-white/10 px-4 py-1 text-xs uppercase tracking-widest text-white/70">
                Multi-tenant observability & compliance
              </p>
              <h1 className="text-5xl font-semibold leading-tight text-white lg:text-6xl">Discover. Secure. Prove compliance from a single cockpit.</h1>
              <p className="text-lg text-white/80">
                The landing experience now mirrors Tenantra.be—elevated cards, emerald accents, and modern typography—while highlighting live capabilities: agent orchestration, compliance engines, and tenant RBAC.
              </p>
              <div className="flex flex-wrap gap-4">
                <Button as={Link} to="/login" size="lg">
                  Enter Console
                </Button>
                <Button as="a" href="#features" variant="outline" size="lg" className="border-white/40 text-white hover:bg-white/10">
                  Explore Features
                </Button>
              </div>
            </div>
            <div className="flex-1">
              <div className="rounded-3xl border border-white/15 bg-white/5 p-8 text-white/80 backdrop-blur">
                <p className="text-sm uppercase tracking-wider text-emerald-200">Operational pulse</p>
                <div className="mt-6 grid grid-cols-2 gap-6 text-center">
                  <div className="rounded-2xl border border-white/10 bg-black/10 p-4">
                    <p className="text-4xl font-semibold text-white">99.95%</p>
                    <p className="text-xs uppercase tracking-widest text-white/70">API uptime</p>
                  </div>
                  <div className="rounded-2xl border border-white/10 bg-black/10 p-4">
                    <p className="text-4xl font-semibold text-white">24</p>
                    <p className="text-xs uppercase tracking-widest text-white/70">Frameworks</p>
                  </div>
                  <div className="rounded-2xl border border-white/10 bg-black/10 p-4">
                    <p className="text-4xl font-semibold text-white">650k</p>
                    <p className="text-xs uppercase tracking-widest text-white/70">Signals/day</p>
                  </div>
                  <div className="rounded-2xl border border-white/10 bg-black/10 p-4">
                    <p className="text-4xl font-semibold text-white">0-touch</p>
                    <p className="text-xs uppercase tracking-widest text-white/70">Agent onboarding</p>
                  </div>
                </div>
                <div className="mt-6 space-y-2 text-sm">
                  <p className="font-semibold text-white">Why operators switch:</p>
                  <ul className="space-y-2 text-white/80">
                    <li className="flex gap-3">
                      <span className="mt-1 h-2 w-2 rounded-full bg-emerald-400" />
                      Tenant-scoped RBAC + encryption mirrored from Tenantra.be.
                    </li>
                    <li className="flex gap-3">
                      <span className="mt-1 h-2 w-2 rounded-full bg-emerald-400" />
                      Prometheus + Grafana surfaced via embedded shell cards.
                    </li>
                    <li className="flex gap-3">
                      <span className="mt-1 h-2 w-2 rounded-full bg-emerald-400" />
                      Automated evidence lockers and remediation playbooks.
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </section>
        </main>
      </div>

      <section id="features" className="mx-auto max-w-6xl px-4 py-20 sm:px-6 lg:px-8">
        <div className="relative overflow-hidden rounded-[36px] bg-white/90 p-10 shadow-[var(--tena-shadow-card)]">
          <div className="absolute inset-0 -z-10 opacity-40 blur-3xl" style={{ background: "radial-gradient(circle at top, rgba(79,70,229,0.35), transparent 60%)" }} />
          <div className="relative">
            <h2 className="text-3xl font-semibold text-slate-900">Operational Coverage</h2>
            <p className="mt-3 max-w-3xl text-lg text-slate-600">
              Every capability from Tenantra.be is mirrored here with Tailwind-driven surfaces—consistent typography, elevated cards, and the same emerald accenting.
            </p>
            <div className="mt-10 grid gap-6 md:grid-cols-2">
              {featureHighlights.map((feature) => (
                <div key={feature.title} className="rounded-3xl border border-slate-100 bg-slate-50/80 p-6">
                  <h3 className="text-xl font-semibold text-slate-900">{feature.title}</h3>
                  <p className="mt-3 text-sm text-slate-600">{feature.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 pb-20 sm:px-6 lg:px-8">
        <div className="grid gap-8 lg:grid-cols-2">
          <div className="rounded-3xl border border-slate-100 bg-white/90 p-8 shadow-[var(--tena-shadow-card)]">
            <h3 className="text-2xl font-semibold text-slate-900">Who runs on Tenantra</h3>
            <p className="mt-3 text-slate-600">MSPs, regulated enterprises, and hybrid-cloud operators standardize on Tenantra for:</p>
            <ul className="mt-6 space-y-3 text-slate-700">
              <li className="flex items-start gap-3">
                <span className="mt-1 h-2.5 w-2.5 rounded-full bg-emerald-500" />
                Multi-tenant RBAC paired with schema isolation.
              </li>
              <li className="flex items-start gap-3">
                <span className="mt-1 h-2.5 w-2.5 rounded-full bg-emerald-500" />
                Compliance-as-a-service exports with automated evidence lockers.
              </li>
              <li className="flex items-start gap-3">
                <span className="mt-1 h-2.5 w-2.5 rounded-full bg-emerald-500" />
                Prometheus, Grafana, and alerting pipelines included out of the box.
              </li>
            </ul>
          </div>
          <div className="rounded-3xl border border-slate-100 bg-slate-900/90 p-8 text-white shadow-[var(--tena-shadow-card)]">
            <h3 className="text-2xl font-semibold">Testimonials</h3>
            <div className="mt-6 space-y-6">
              {testimonials.map((testimonial) => (
                <blockquote key={testimonial.author} className="rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur">
                  <p className="text-white/90">&ldquo;{testimonial.quote}&rdquo;</p>
                  <footer className="mt-4 text-sm text-white/70">{testimonial.author}</footer>
                </blockquote>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="bg-white/90 py-16">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <div className="rounded-3xl border border-slate-100 bg-slate-50/80 p-8 shadow-sm">
            <div className="grid gap-10 lg:grid-cols-2">
              <div>
                <h3 className="text-2xl font-semibold text-slate-900">Schedule a guided walkthrough</h3>
                <p className="mt-3 text-slate-600">Submit the form to have our customer success team provision a tenant sandbox identical to the production experience.</p>
              </div>
              <div>
                {submitted ? (
                  <div className="rounded-2xl border border-emerald-200 bg-emerald-50/80 p-6 text-emerald-700">
                    <p className="font-semibold">Request received.</p>
                    <p className="mt-2 text-sm">We&apos;ll reach out within one business day with onboarding steps.</p>
                  </div>
                ) : (
                  <form onSubmit={handleSubmit} className="space-y-4">
                    <input name="name" value={form.name} onChange={handleChange} placeholder="Full name" className="field-control w-full rounded-2xl border border-slate-200 px-4 py-3" required />
                    <input name="email" type="email" value={form.email} onChange={handleChange} placeholder="Work email" className="field-control w-full rounded-2xl border border-slate-200 px-4 py-3" required />
                    <input name="company" value={form.company} onChange={handleChange} placeholder="Company" className="field-control w-full rounded-2xl border border-slate-200 px-4 py-3" />
                    <select name="plan" value={form.plan} onChange={handleChange} className="field-control w-full rounded-2xl border border-slate-200 px-4 py-3">
                      <option value="growth">Growth</option>
                      <option value="enterprise">Enterprise</option>
                      <option value="msp">MSP / MSSP</option>
                    </select>
                    <Button type="submit" className="w-full">
                      Request Walkthrough
                    </Button>
                  </form>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
