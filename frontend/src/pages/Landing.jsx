import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import Button from "../components/ui/Button.jsx";

const featureHighlights = [
  {
    title: "Asset Discovery & Inventory",
    description:
      "Automated discovery of servers, endpoints, and network devices, with OS, role, and application fingerprinting.",
  },
  {
    title: "Security & Compliance",
    description:
      "Continuous vulnerability and compliance scanning with built-in frameworks like CIS Benchmarks, ISO 27001, and NIST 800-53.",
  },
  {
    title: "Alerting & Incident Management",
    description:
      "Configurable thresholds and rules, with branded HTML notifications and integration hooks for SIEM and ticketing tools.",
  },
  {
    title: "DevSecOps & Automation",
    description:
      "GitHub Actions CI/CD pipelines, Dockerized deployment, and automated migration and seed scripts.",
  },
  {
    title: "Monitoring & Analytics",
    description:
      "Metrics exported to Prometheus and visualized in Grafana dashboards, with compliance trends and SLA metrics over time.",
  },
  {
    title: "User & Tenant Management",
    description:
      "Multi-tenant structure with isolated schemas and role-based dashboard views and permissions.",
  },
];

const testimonials = [
  {
    quote:
      "Tenantra has been a game-changer for our compliance team. We can now respond to audits in minutes instead of days.",
    author: "John Doe, CISO at a Fortune 500 company",
  },
  {
    quote:
      "The automated evidence collection and smart reminders have saved us countless hours of manual work.",
    author: "Jane Smith, Security Manager at a mid-size enterprise",
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
    <div className="bg-gray-50 text-gray-800">
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-3xl font-bold text-gray-900">Tenantra</h1>
          <nav className="flex items-center space-x-6">
            <Link to="/login" className="text-base font-medium text-gray-500 hover:text-gray-900">Login</Link>
            <Link to="/app/faq" className="text-base font-medium text-gray-500 hover:text-gray-900">FAQ</Link>
            <Button as={Link} to="/login" className="ml-4">Get Started</Button>
          </nav>
        </div>
      </header>

      <main>
        <div className="bg-white">
          <div className="mx-auto max-w-7xl py-24 sm:py-32 px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <h2 className="text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl md:text-6xl">The Unified IT Discovery & Compliance Platform</h2>
              <p className="mt-6 max-w-2xl mx-auto text-xl text-gray-500">
                Tenantra is a multi-tenant, cloud-ready IT discovery, security, and compliance automation platform. It continuously scans, inventories, and secures complex IT environments—covering infrastructure, endpoints, networks, identities, configurations, and compliance posture—under a single intelligent dashboard.
              </p>
              <div className="mt-10 flex justify-center gap-x-6">
                <Button as={Link} to="/login" size="lg">Get Started</Button>
                <Button as="a" href="#features" variant="outline" size="lg">Explore Capabilities</Button>
              </div>
            </div>
          </div>
        </div>

        <div id="who-is-it-for" className="py-24 sm:py-32">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <h2 className="text-3xl font-extrabold tracking-tight text-gray-900 sm:text-4xl">Who is it for?</h2>
              <p className="mt-4 max-w-2xl mx-auto text-lg text-gray-500">
                Tenantra is designed for a wide range of organizations and teams that need to manage IT assets, security, and compliance at scale.
              </p>
            </div>
            <div className="mt-16 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
              <div className="bg-white rounded-lg shadow-md p-8">
                <h3 className="text-xl font-bold text-gray-900">Enterprises</h3>
                <p className="mt-4 text-gray-500">Gain full visibility into your IT assets, automate compliance reporting, and reduce your attack surface.</p>
              </div>
              <div className="bg-white rounded-lg shadow-md p-8">
                <h3 className="text-xl font-bold text-gray-900">Managed Service Providers (MSPs)</h3>
                <p className="mt-4 text-gray-500">Offer discovery, security, and compliance as a service to your clients with our multi-tenant platform.</p>
              </div>
              <div className="bg-white rounded-lg shadow-md p-8">
                <h3 className="text-xl font-bold text-gray-900">Government & Regulated Entities</h3>
                <p className="mt-4 text-gray-500">Meet strict compliance requirements with our built-in support for ISO 27001, NIST 800-53, and more.</p>
              </div>
            </div>
          </div>
        </div>

        <div id="why-tenantra" className="bg-white py-24 sm:py-32">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <h2 className="text-3xl font-extrabold tracking-tight text-gray-900 sm:text-4xl">Why Tenantra?</h2>
              <p className="mt-4 max-w-2xl mx-auto text-lg text-gray-500">
                Tenantra is more than just a monitoring tool—it's a full-stack DevSecOps and compliance automation platform.
              </p>
            </div>
            <div className="mt-16 grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
              <div className="p-8">
                <h3 className="text-xl font-bold text-gray-900">True Multi-Tenant Isolation</h3>
                <p className="mt-4 text-gray-500">Each tenant’s data is fully isolated by schema and RBAC policy, with per-client encryption and audit trail.</p>
              </div>
              <div className="p-8">
                <h3 className="text-xl font-bold text-gray-900">Modular Scanning Engine</h3>
                <p className="mt-4 text-gray-500">Covering system, network, identity, and compliance layers with over 900 modular scans.</p>
              </div>
              <div className="p-8">
                <h3 className="text-xl font-bold text-gray-900">Compliance-as-a-Service</h3>
                <p className="mt-4 text-gray-500">Enable MSPs to resell scanning and reporting with our white-label ready platform.</p>
              </div>
            </div>
          </div>
        </div>

        <div id="features" className="py-24 sm:py-32">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <h2 className="text-3xl font-extrabold tracking-tight text-gray-900 sm:text-4xl">A feature for every need</h2>
              <p className="mt-4 max-w-2xl mx-auto text-lg text-gray-500">
                Tenantra provides a comprehensive suite of tools to help you manage your IT environment.
              </p>
            </div>
            <div className="mt-16 grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3">
              {featureHighlights.map((feature) => (
                <div key={feature.title} className="bg-white rounded-lg shadow-md p-8">
                  <h3 className="text-xl font-bold text-gray-900">{feature.title}</h3>
                  <p className="mt-4 text-gray-500">{feature.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div id="pricing" className="bg-white py-24 sm:py-32">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <h2 className="text-3xl font-extrabold tracking-tight text-gray-900 sm:text-4xl">Flexible pricing for teams of all sizes</h2>
              <p className="mt-4 max-w-2xl mx-auto text-lg text-gray-500">
                Choose the plan that's right for you and get started with Tenantra today.
              </p>
            </div>
            <div className="mt-16 grid grid-cols-1 gap-8 lg:grid-cols-3">
              <div className="border border-gray-200 rounded-lg shadow-sm divide-y divide-gray-200">
                <div className="p-6">
                  <h2 className="text-lg leading-6 font-medium text-gray-900">Free</h2>
                  <p className="mt-4 text-sm text-gray-500">A free plan for individuals and small teams to get started with Tenantra.</p>
                  <p className="mt-8">
                    <span className="text-4xl font-extrabold text-gray-900">$0</span>
                    <span className="text-base font-medium text-gray-500">/mo</span>
                  </p>
                  <Button as={Link} to="/login" className="mt-8 w-full">Get Started</Button>
                </div>
                <div className="pt-6 pb-8 px-6">
                  <h3 className="text-xs font-medium text-gray-900 tracking-wide uppercase">What's included</h3>
                  <ul className="mt-6 space-y-4">
                    <li className="flex space-x-3">
                      <span>1 User</span>
                    </li>
                    <li className="flex space-x-3">
                      <span>100 Assets</span>
                    </li>
                    <li className="flex space-x-3">
                      <span>Basic Compliance Reporting</span>
                    </li>
                  </ul>
                </div>
              </div>
              <div className="border-2 border-primary rounded-lg shadow-sm divide-y divide-gray-200">
                <div className="p-6">
                  <h2 className="text-lg leading-6 font-medium text-gray-900">Pro</h2>
                  <p className="mt-4 text-sm text-gray-500">A plan for growing teams that need more power and support.</p>
                  <p className="mt-8">
                    <span className="text-4xl font-extrabold text-gray-900">$99</span>
                    <span className="text-base font-medium text-gray-500">/mo</span>
                  </p>
                  <Button as={Link} to="/login" className="mt-8 w-full">Get Started</Button>
                </div>
                <div className="pt-6 pb-8 px-6">
                  <h3 className="text-xs font-medium text-gray-900 tracking-wide uppercase">What's included</h3>
                  <ul className="mt-6 space-y-4">
                    <li className="flex space-x-3">
                      <span>10 Users</span>
                    </li>
                    <li className="flex space-x-3">
                      <span>1000 Assets</span>
                    </li>
                    <li className="flex space-x-3">
                      <span>Advanced Compliance Reporting</span>
                    </li>
                    <li className="flex space-x-3">
                      <span>Email Support</span>
                    </li>
                  </ul>
                </div>
              </div>
              <div className="border border-gray-200 rounded-lg shadow-sm divide-y divide-gray-200">
                <div className="p-6">
                  <h2 className="text-lg leading-6 font-medium text-gray-900">Enterprise</h2>
                  <p className="mt-4 text-sm text-gray-500">A plan for large organizations with complex needs.</p>
                  <p className="mt-8">
                    <span className="text-4xl font-extrabold text-gray-900">Contact us</span>
                  </p>
                  <Button as="a" href="#subscribe" variant="outline" className="mt-8 w-full">Contact Sales</Button>
                </div>
                <div className="pt-6 pb-8 px-6">
                  <h3 className="text-xs font-medium text-gray-900 tracking-wide uppercase">What's included</h3>
                  <ul className="mt-6 space-y-4">
                    <li className="flex space-x-3">
                      <span>Unlimited Users</span>
                    </li>
                    <li className="flex space-x-3">
                      <span>Unlimited Assets</span>
                    </li>
                    <li className="flex space-x-3">
                      <span>Custom Compliance Reporting</span>
                    </li>
                    <li className="flex space-x-3">
                      <span>24/7 Phone Support</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div id="testimonials" className="py-24 sm:py-32">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <h2 className="text-3xl font-extrabold tracking-tight text-gray-900 sm:text-4xl">What our customers are saying</h2>
            </div>
            <div className="mt-16 grid grid-cols-1 gap-8 lg:grid-cols-2">
              {testimonials.map((testimonial) => (
                <div key={testimonial.author} className="bg-white rounded-lg shadow-md p-8">
                  <blockquote className="text-xl text-gray-900">
                    <p>“{testimonial.quote}”</p>
                  </blockquote>
                  <figcaption className="mt-6">
                    <p className="text-base font-medium text-gray-900">{testimonial.author}</p>
                  </figcaption>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div id="subscribe" className="bg-primary text-white">
          <div className="mx-auto max-w-7xl py-24 sm:py-32 px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl font-extrabold tracking-tight sm:text-4xl">Ready to get started?</h2>
            <p className="mt-4 text-lg text-primary-light">
              Request a walkthrough and one of our specialists will be in touch.
            </p>
            <Button as="a" href="#subscribe-form" size="lg" className="mt-10">Request a walkthrough</Button>
          </div>
        </div>

        <div id="subscribe-form" className="py-24 sm:py-32">
          <div className="mx-auto max-w-md px-4 sm:px-6 lg:px-8">
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
        </div>
      </main>

      <footer className="bg-white">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-12">
          <div className="flex items-center justify-between">
            <p className="text-base text-gray-400">&copy; {new Date().getFullYear()} Tenantra. All rights reserved.</p>
            <div className="flex space-x-6">
              <Link to="/login" className="text-base font-medium text-gray-500 hover:text-gray-900">Login</Link>
              <a href="#subscribe" className="text-base font-medium text-gray-500 hover:text-gray-900">Subscribe</a>
              <Link to="/app/dashboard" className="text-base font-medium text-gray-500 hover:text-gray-900">Product tour</Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
