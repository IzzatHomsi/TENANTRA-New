import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import Button from "../components/ui/Button.jsx";

const featureHighlights = [
  {
    title: "Unified Compliance Dashboard",
    description:
      "Tenantra connects policies, controls, and evidence across frameworks in one command center so you can respond to audits in minutes instead of days.",
  },
  {
    title: "Real-Time Risk Monitoring",
    description:
      "Live integrations surface configuration drift, vulnerable assets, and overdue tasks before they become business incidents.",
  },
  {
    title: "Automated Evidence Collection",
    description:
      "Schedule recurring evidence requests, collect attestations, and let Tenantra chase stakeholders with smart reminders.",
  },
  {
    title: "Role-Based Orchestration",
    description:
      "Give every team a tailored workspace with granular permissions, workflows, and automation tuned to their responsibilities.",
  },
];

export default function Landing() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", company: "", plan: "growth" });
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/app/dashboard", { replace: true });
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
    <div className="bg-neutral text-gray-800">
      <header className="bg-white shadow-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <h1 className="text-3xl font-bold text-primary">tenantra</h1>
          <nav className="flex items-center space-x-4">
            <Link to="/login" className="text-gray-600 hover:text-primary">Login</Link>
            <Link to="/app/faq" className="text-gray-600 hover:text-primary">FAQ</Link>
            <Button as={Link} to="/login">Get Started</Button>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-24">
        <div className="text-center">
          <h2 className="text-5xl font-bold">Tell a stronger security story with Tenantra.</h2>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-gray-600">
            Tenantra is the operating system for compliance teams who need to move fast. Automate evidence, monitor controls, and surface actionable risk insights in a single intuitive workspace.
          </p>
          <div className="mt-8 flex justify-center space-x-4">
            <Button as={Link} to="/login" size="lg">Get Started</Button>
            <Button as="a" href="#features" variant="outline" size="lg">Explore Capabilities</Button>
          </div>
        </div>

        <section id="features" className="mt-24">
          <div className="grid grid-cols-1 gap-12 md:grid-cols-2">
            {featureHighlights.map((feature) => (
              <div key={feature.title}>
                <h3 className="text-2xl font-bold">{feature.title}</h3>
                <p className="mt-4 text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </section>

        <section id="subscribe" className="mt-24 rounded-lg bg-white p-12 shadow-lg">
          <div className="grid grid-cols-1 gap-12 md:grid-cols-2">
            <div>
              <h2 className="text-3xl font-bold">Subscribe to Tenantra</h2>
              <p className="mt-4 text-gray-600">
                Ready to orchestrate compliance without the chaos? Submit your details and our onboarding specialists will schedule a tailored walkthrough within one business day.
              </p>
            </div>
            {
              submitted ? (
                <div className="flex items-center justify-center rounded-lg bg-green-100 p-8 text-center">
                  <p className="text-lg text-green-800">Thank you! We received your walkthrough request and will reach out shortly.</p>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Name</label>
                    <input
                      type="text"
                      name="name"
                      value={form.name}
                      onChange={handleChange}
                      required
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Work email</label>
                    <input
                      type="email"
                      name="email"
                      value={form.email}
                      onChange={handleChange}
                      required
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Company</label>
                    <input
                      type="text"
                      name="company"
                      value={form.company}
                      onChange={handleChange}
                      required
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Plan interest</label>
                    <select
                      name="plan"
                      value={form.plan}
                      onChange={handleChange}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                    >
                      <option value="starter">Starter – launch your first framework</option>
                      <option value="growth">Growth – scale compliance across teams</option>
                      <option value="enterprise">Enterprise – advanced automation &amp; support</option>
                    </select>
                  </div>
                  <Button type="submit" className="w-full">Request a walkthrough</Button>
                </form>
              )
            }
          </div>
        </section>
      </main>

      <footer className="bg-white">
        <div className="mx-auto max-w-6xl px-6 py-12">
          <div className="flex items-center justify-between">
            <p className="text-gray-600">&copy; {new Date().getFullYear()} Tenantra. All rights reserved.</p>
            <div className="flex space-x-4">
              <Link to="/login" className="text-gray-600 hover:text-primary">Login</Link>
              <a href="#subscribe" className="text-gray-600 hover:text-primary">Subscribe</a>
              <Link to="/app/dashboard" className="text-gray-600 hover:text-primary">Product tour</Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
