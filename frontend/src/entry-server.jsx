import React from "react";
import App from "./App.jsx";
import { AppProviders } from "./AppProviders.jsx";
import { StaticRouter } from "react-router-dom/server";
import { createQueryClient } from "./lib/queryClient.js";
import { prefetchSupportSettings } from "./queries/supportSettings.js";

const SSR_API_BASE =
  process.env.SSR_API_BASE ||
  process.env.VITE_API_URL ||
  process.env.VITE_API_BASE ||
  null;

export async function createApp(url) {
  const queryClient = createQueryClient();

  if (SSR_API_BASE) {
    await prefetchSupportSettings(queryClient, SSR_API_BASE.replace(/\/+$/, ""));
  }

  const app = (
    <AppProviders queryClient={queryClient}>
      <StaticRouter location={url}>
        <App />
      </StaticRouter>
    </AppProviders>
  );

  return { app, queryClient };
}
