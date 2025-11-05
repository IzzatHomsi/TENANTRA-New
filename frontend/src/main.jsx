import React from "react";
import { createRoot, hydrateRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App.jsx";
import { hydrate as hydrateQueryClient } from "@tanstack/react-query";
import { createQueryClient } from "./lib/queryClient.js";
import { registerWebVitals } from "./lib/webVitals.js";
import { AppProviders } from "./AppProviders.jsx";
import "./index.css";
import "./styles/app.css";
import "./styles/theme.css";

const queryClient = createQueryClient();

if (typeof window !== "undefined") {
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
const app = (
  <React.StrictMode>
    <AppProviders queryClient={queryClient}>
      <BrowserRouter>
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
