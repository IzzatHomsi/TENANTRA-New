import React from "react";
import App from "./App.jsx";
import { AppProviders } from "./AppProviders.jsx";
import { StaticRouter } from "react-router-dom/server";
import { createQueryClient } from "./lib/queryClient.js";
import { runLoaders } from "../server/loaders.mjs";

const SSR_API_BASE =
  process.env.SSR_API_BASE ||
  process.env.VITE_API_URL ||
  process.env.VITE_API_BASE ||
  null;

const NORMALIZED_API_BASE = SSR_API_BASE ? SSR_API_BASE.replace(/\/+$/, "") : null;

export async function createApp({ url, headers }) {
  const queryClient = createQueryClient();

  await runLoaders({
    url,
    headers,
    queryClient,
    apiBase: NORMALIZED_API_BASE,
  });

  const app = (
    <AppProviders queryClient={queryClient}>
      <StaticRouter location={url}>
        <App />
      </StaticRouter>
    </AppProviders>
  );

  return { app, queryClient };
}
