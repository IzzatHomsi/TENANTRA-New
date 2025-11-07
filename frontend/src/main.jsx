import React from "react";
import { createRoot, hydrateRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App.jsx";
import { hydrate as hydrateQueryClient } from "@tanstack/react-query";
import { createQueryClient } from "./lib/queryClient.js";
import { registerWebVitals } from "./lib/webVitals.js";
import { AppProviders } from "./AppProviders.jsx";
import { registerSW } from "virtual:pwa-register";
import { prefetchRoutes } from "./lib/prefetchRoutes.js";
import "./index.css";
import "./styles/theme.css";

const queryClient = createQueryClient();
const rawBase = import.meta.env.BASE_URL || "/";
const normalizedBase = rawBase.endsWith("/")
  ? rawBase.slice(0, -1) || "/"
  : rawBase;

let swOptOut = false;
if (typeof window !== "undefined") {
  try {
    const params = new URLSearchParams(window.location.search);
    const swParam = params.get("sw");
    if (swParam === "off") {
      window.sessionStorage.setItem("TENANTRA_DISABLE_SW", "true");
    } else if (swParam === "on") {
      window.sessionStorage.removeItem("TENANTRA_DISABLE_SW");
    }
    swOptOut = window.sessionStorage.getItem("TENANTRA_DISABLE_SW") === "true";
  } catch {
    swOptOut = false;
  }
}

const shouldRegisterSW =
  typeof window !== "undefined" &&
  import.meta.env.VITE_DISABLE_SW !== "true" &&
  !swOptOut;

if (typeof window !== "undefined") {
  const scope = normalizedBase === "/" ? "/" : `${normalizedBase}/`;
  if (shouldRegisterSW) {
    registerSW({ immediate: true, scope });
  }

  if (scope !== "/" && "serviceWorker" in navigator) {
    navigator.serviceWorker
      .getRegistration("/")
      .then((registration) => registration?.unregister())
      .catch(() => {
        /* ignore cleanup errors */
      });
  }

  const state = window.__TANSTACK_DEHYDRATED_STATE__;
  if (state) {
    hydrateQueryClient(queryClient, state);
    try {
      delete window.__TANSTACK_DEHYDRATED_STATE__;
    } catch {
      window.__TANSTACK_DEHYDRATED_STATE__ = undefined;
    }
  }
}

const container = document.getElementById("root");

if (typeof window !== "undefined" && normalizedBase !== "/") {
  const hasBasePrefix =
    window.location.pathname === normalizedBase ||
    window.location.pathname.startsWith(`${normalizedBase}/`);
  if (!hasBasePrefix) {
    const targetUrl = new URL(window.location.href);
    const nextPath =
      window.location.pathname === "/"
        ? `${normalizedBase}/`
        : `${normalizedBase}${window.location.pathname.startsWith("/") ? "" : "/"}${
            window.location.pathname.startsWith("/") ? window.location.pathname.slice(1) : window.location.pathname
          }`;
    targetUrl.pathname = nextPath.replace(/\/{2,}/g, "/");
    window.location.replace(targetUrl.toString());
  }
}

const app = (
  <React.StrictMode>
    <AppProviders queryClient={queryClient}>
      <BrowserRouter basename={normalizedBase === "/" ? undefined : normalizedBase}>
        <App />
      </BrowserRouter>
    </AppProviders>
  </React.StrictMode>
);

if (container?.hasChildNodes()) {
  hydrateRoot(container, app);
} else if (container) {
  createRoot(container).render(app);
}

registerWebVitals();

if (typeof window !== "undefined") {
  prefetchRoutes();
}
