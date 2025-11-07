import React, { useEffect, useMemo, useState, memo } from "react";
import CollapsibleSection from "./CollapsibleSection.jsx";

const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function BrandingTab({ form, updateField, onValidationChange }) {
  const [errors, setErrors] = useState({});

  const grafanaUrl = form["grafana.url"] || "";
  const emailEnabled = !!form["email.redirect.enabled"];
  const redirectEmail = form["email.redirect.to"] || "";

  useEffect(() => {
    const nextErrors = {};
    if (grafanaUrl && !/^https?:\/\//i.test(grafanaUrl)) {
      nextErrors["grafana.url"] = "Use the root https:// URL; Tenantra proxies /grafana automatically.";
    }
    if (emailEnabled) {
      if (!redirectEmail) {
        nextErrors["email.redirect.to"] = "Provide the inbox address that should receive redirected messages.";
      } else if (!emailRegex.test(redirectEmail)) {
        nextErrors["email.redirect.to"] = "Enter a valid email address (e.g., security@example.com).";
      }
    }
    setErrors(nextErrors);
  }, [grafanaUrl, emailEnabled, redirectEmail]);

  useEffect(() => {
    onValidationChange?.(errors);
  }, [errors, onValidationChange]);

  const httpsSuggestion = useMemo(() => {
    if (!grafanaUrl) return "";
    if (grafanaUrl.startsWith("http://grafana:3000")) {
      return "Detected docker service URL. Consider switching to your HTTPS proxy for production.";
    }
    if (grafanaUrl.startsWith("http://")) {
      return "Grafana is using HTTP. Enable TLS or front it via the Tenantra proxy for secure access.";
    }
    return "";
  }, [grafanaUrl]);

  return (
    <div className="space-y-4">
      <CollapsibleSection
        id="branding-theme"
        title="Brand identity"
        helper="Set the primary color used across the shell, dashboards, and key call-to-actions."
      >
        <div className="grid gap-4 sm:grid-cols-[max-content_1fr] sm:items-center">
          <label className="text-sm font-medium text-primary-text" htmlFor="branding-color">
            Primary color
          </label>
          <div>
            <p className="text-xs text-secondary-text">Impacts the sidebar, primary buttons, and chart accents.</p>
            <input
              id="branding-color"
              type="color"
              value={form["theme.colors.primary"] || "#1877F2"}
              onChange={(e) => updateField("theme.colors.primary", e.target.value)}
              className="mt-2 h-12 w-24 rounded-lg border border-border-color bg-surface"
            />
          </div>
        </div>
      </CollapsibleSection>

      <CollapsibleSection
        id="branding-grafana"
        title="Grafana integration"
        helper="Connect Tenantra to Grafana so metrics widgets load instantly."
        action={
          <a
            href="/observability-setup"
            className="text-sm font-medium text-primary hover:underline"
          >
            Learn more
          </a>
        }
      >
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium text-primary-text" htmlFor="grafana-url">
              Grafana URL
            </label>
            <p className="text-xs text-secondary-text">Use the root URL; Tenantra automatically proxies /grafana.</p>
            <input
              id="grafana-url"
              type="url"
              value={grafanaUrl}
              onChange={(e) => updateField("grafana.url", e.target.value.trim())}
              placeholder="https://grafana.example.com"
              className={`mt-2 block w-full rounded-lg border px-3 py-2 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40 ${
                errors["grafana.url"] ? "border-red-500 ring-red-200" : "border-border-color"
              }`}
            />
            {errors["grafana.url"] ? (
              <p className="mt-2 text-xs text-red-500">{errors["grafana.url"]}</p>
            ) : (
              <p className="mt-2 text-xs text-secondary-text">
                Example: https://observability.tenantra.com
              </p>
            )}
            {httpsSuggestion && <p className="mt-2 text-xs text-amber-600">{httpsSuggestion}</p>}
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="text-sm font-medium text-primary-text" htmlFor="grafana-dashboard">
                Dashboard UID
              </label>
              <p className="text-xs text-secondary-text">Default Tenantra overview is tenantra-overview.</p>
              <input
                id="grafana-dashboard"
                type="text"
                value={form["grafana.dashboard_uid"] || ""}
                onChange={(e) => updateField("grafana.dashboard_uid", e.target.value.trim())}
                placeholder="tenantra-overview"
                className="mt-2 block w-full rounded-lg border border-border-color px-3 py-2 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-primary-text" htmlFor="grafana-datasource">
                Datasource UID
              </label>
              <p className="text-xs text-secondary-text">Optional. Required if Grafana panels depend on non-default sources.</p>
              <input
                id="grafana-datasource"
                type="text"
                value={form["grafana.datasource_uid"] || ""}
                onChange={(e) => updateField("grafana.datasource_uid", e.target.value.trim())}
                placeholder="prometheus"
                className="mt-2 block w-full rounded-lg border border-border-color px-3 py-2 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40"
              />
            </div>
          </div>
        </div>
      </CollapsibleSection>

      <CollapsibleSection
        id="branding-email"
        title="Email routing"
        helper="Redirect system email traffic during staging or incident triage."
      >
        <div className="space-y-4">
          <label className="flex items-center gap-3 text-sm text-primary-text" htmlFor="email-redirect-enabled">
            <input
              id="email-redirect-enabled"
              type="checkbox"
              checked={emailEnabled}
              onChange={(e) => updateField("email.redirect.enabled", e.target.checked)}
              className="h-4 w-4 rounded border-border-color text-primary focus:ring-primary"
            />
            Enable redirect
          </label>
          <div>
            <label className="text-sm font-medium text-primary-text" htmlFor="email-redirect-to">
              Redirect to
            </label>
            <p className="text-xs text-secondary-text">All outbound emails will be BCC’d to this address.</p>
            <input
              id="email-redirect-to"
              type="email"
              disabled={!emailEnabled}
              value={redirectEmail}
              onChange={(e) => updateField("email.redirect.to", e.target.value.trim())}
              placeholder="security@example.com"
              className={`mt-2 block w-full rounded-lg border px-3 py-2 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40 ${
                errors["email.redirect.to"] ? "border-red-500 ring-red-200" : "border-border-color"
              } ${!emailEnabled ? "bg-gray-100 text-secondary-text" : ""}`}
            />
            {emailEnabled && errors["email.redirect.to"] && (
              <p className="mt-2 text-xs text-red-500">{errors["email.redirect.to"]}</p>
            )}
            {emailEnabled && !errors["email.redirect.to"] && (
              <p className="mt-2 text-xs text-secondary-text">Use a shared inbox so the team can monitor rerouted notifications.</p>
            )}
          </div>
        </div>
      </CollapsibleSection>
    </div>
  );
}

export default memo(BrandingTab);
