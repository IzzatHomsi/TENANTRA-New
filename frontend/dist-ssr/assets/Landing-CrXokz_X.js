import { jsxs, jsx } from "react/jsx-runtime";
import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { u as useAuth } from "../entry-server.js";
import { B as Button } from "./Button-C2WBf5y3.js";
import "@tanstack/react-query";
import "react-router-dom/server.mjs";
const featureHighlights = [
  {
    title: "Unified Compliance Dashboard",
    description: "Tenantra connects policies, controls, and evidence across frameworks in one command center so you can respond to audits in minutes instead of days."
  },
  {
    title: "Real-Time Risk Monitoring",
    description: "Live integrations surface configuration drift, vulnerable assets, and overdue tasks before they become business incidents."
  },
  {
    title: "Automated Evidence Collection",
    description: "Schedule recurring evidence requests, collect attestations, and let Tenantra chase stakeholders with smart reminders."
  },
  {
    title: "Role-Based Orchestration",
    description: "Give every team a tailored workspace with granular permissions, workflows, and automation tuned to their responsibilities."
  }
];
function Landing() {
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
          referrer: window?.location?.href || void 0
        })
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setSubmitted(true);
    } catch (e) {
      console.error("Walkthrough request failed", e);
      alert("Could not submit request. Please try again later.");
    }
  }
  return /* @__PURE__ */ jsxs("div", { className: "bg-facebook-gray text-gray-800", children: [
    /* @__PURE__ */ jsx("header", { className: "bg-white shadow-md", children: /* @__PURE__ */ jsxs("div", { className: "mx-auto flex max-w-6xl items-center justify-between px-6 py-4", children: [
      /* @__PURE__ */ jsx("h1", { className: "text-3xl font-bold text-facebook-blue", children: "tenantra" }),
      /* @__PURE__ */ jsxs("nav", { className: "flex items-center space-x-4", children: [
        /* @__PURE__ */ jsx(Link, { to: "/login", className: "text-gray-600 hover:text-facebook-blue", children: "Login" }),
        /* @__PURE__ */ jsx(Link, { to: "/app/faq", className: "text-gray-600 hover:text-facebook-blue", children: "FAQ" }),
        /* @__PURE__ */ jsx(Button, { as: Link, to: "/login", children: "Get Started" })
      ] })
    ] }) }),
    /* @__PURE__ */ jsxs("main", { className: "mx-auto max-w-6xl px-6 py-24", children: [
      /* @__PURE__ */ jsxs("div", { className: "text-center", children: [
        /* @__PURE__ */ jsx("h2", { className: "text-5xl font-bold", children: "Tell a stronger security story with Tenantra." }),
        /* @__PURE__ */ jsx("p", { className: "mx-auto mt-6 max-w-2xl text-lg text-gray-600", children: "Tenantra is the operating system for compliance teams who need to move fast. Automate evidence, monitor controls, and surface actionable risk insights in a single intuitive workspace." }),
        /* @__PURE__ */ jsxs("div", { className: "mt-8 flex justify-center space-x-4", children: [
          /* @__PURE__ */ jsx(Button, { as: Link, to: "/login", size: "lg", children: "Get Started" }),
          /* @__PURE__ */ jsx(Button, { as: "a", href: "#features", variant: "outline", size: "lg", children: "Explore Capabilities" })
        ] })
      ] }),
      /* @__PURE__ */ jsx("section", { id: "features", className: "mt-24", children: /* @__PURE__ */ jsx("div", { className: "grid grid-cols-1 gap-12 md:grid-cols-2", children: featureHighlights.map((feature) => /* @__PURE__ */ jsxs("div", { children: [
        /* @__PURE__ */ jsx("h3", { className: "text-2xl font-bold", children: feature.title }),
        /* @__PURE__ */ jsx("p", { className: "mt-4 text-gray-600", children: feature.description })
      ] }, feature.title)) }) }),
      /* @__PURE__ */ jsx("section", { id: "subscribe", className: "mt-24 rounded-lg bg-white p-12 shadow-lg", children: /* @__PURE__ */ jsxs("div", { className: "grid grid-cols-1 gap-12 md:grid-cols-2", children: [
        /* @__PURE__ */ jsxs("div", { children: [
          /* @__PURE__ */ jsx("h2", { className: "text-3xl font-bold", children: "Subscribe to Tenantra" }),
          /* @__PURE__ */ jsx("p", { className: "mt-4 text-gray-600", children: "Ready to orchestrate compliance without the chaos? Submit your details and our onboarding specialists will schedule a tailored walkthrough within one business day." })
        ] }),
        submitted ? /* @__PURE__ */ jsx("div", { className: "flex items-center justify-center rounded-lg bg-green-100 p-8 text-center", children: /* @__PURE__ */ jsx("p", { className: "text-lg text-green-800", children: "Thank you! We received your walkthrough request and will reach out shortly." }) }) : /* @__PURE__ */ jsxs("form", { onSubmit: handleSubmit, className: "space-y-6", children: [
          /* @__PURE__ */ jsxs("div", { children: [
            /* @__PURE__ */ jsx("label", { className: "block text-sm font-medium text-gray-700", children: "Name" }),
            /* @__PURE__ */ jsx(
              "input",
              {
                type: "text",
                name: "name",
                value: form.name,
                onChange: handleChange,
                required: true,
                className: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
              }
            )
          ] }),
          /* @__PURE__ */ jsxs("div", { children: [
            /* @__PURE__ */ jsx("label", { className: "block text-sm font-medium text-gray-700", children: "Work email" }),
            /* @__PURE__ */ jsx(
              "input",
              {
                type: "email",
                name: "email",
                value: form.email,
                onChange: handleChange,
                required: true,
                className: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
              }
            )
          ] }),
          /* @__PURE__ */ jsxs("div", { children: [
            /* @__PURE__ */ jsx("label", { className: "block text-sm font-medium text-gray-700", children: "Company" }),
            /* @__PURE__ */ jsx(
              "input",
              {
                type: "text",
                name: "company",
                value: form.company,
                onChange: handleChange,
                required: true,
                className: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
              }
            )
          ] }),
          /* @__PURE__ */ jsxs("div", { children: [
            /* @__PURE__ */ jsx("label", { className: "block text-sm font-medium text-gray-700", children: "Plan interest" }),
            /* @__PURE__ */ jsxs(
              "select",
              {
                name: "plan",
                value: form.plan,
                onChange: handleChange,
                className: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm",
                children: [
                  /* @__PURE__ */ jsx("option", { value: "starter", children: "Starter – launch your first framework" }),
                  /* @__PURE__ */ jsx("option", { value: "growth", children: "Growth – scale compliance across teams" }),
                  /* @__PURE__ */ jsx("option", { value: "enterprise", children: "Enterprise – advanced automation & support" })
                ]
              }
            )
          ] }),
          /* @__PURE__ */ jsx(Button, { type: "submit", className: "w-full", children: "Request a walkthrough" })
        ] })
      ] }) })
    ] }),
    /* @__PURE__ */ jsx("footer", { className: "bg-white", children: /* @__PURE__ */ jsx("div", { className: "mx-auto max-w-6xl px-6 py-12", children: /* @__PURE__ */ jsxs("div", { className: "flex items-center justify-between", children: [
      /* @__PURE__ */ jsxs("p", { className: "text-gray-600", children: [
        "© ",
        (/* @__PURE__ */ new Date()).getFullYear(),
        " Tenantra. All rights reserved."
      ] }),
      /* @__PURE__ */ jsxs("div", { className: "flex space-x-4", children: [
        /* @__PURE__ */ jsx(Link, { to: "/login", className: "text-gray-600 hover:text-facebook-blue", children: "Login" }),
        /* @__PURE__ */ jsx("a", { href: "#subscribe", className: "text-gray-600 hover:text-facebook-blue", children: "Subscribe" }),
        /* @__PURE__ */ jsx(Link, { to: "/app/dashboard", className: "text-gray-600 hover:text-facebook-blue", children: "Product tour" })
      ] })
    ] }) }) })
  ] });
}
export {
  Landing as default
};
