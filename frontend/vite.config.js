import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { visualizer } from "rollup-plugin-visualizer";
import { VitePWA } from "vite-plugin-pwa";
import federation from "@originjs/vite-plugin-federation";

const API_PROXY_TARGET = process.env.VITE_API_PROXY_TARGET || "http://localhost:5000";
const APP_BASE = "/app/";

const sharedProxy = {
  "/api": { target: API_PROXY_TARGET, changeOrigin: true, secure: false },
  "/auth": { target: API_PROXY_TARGET, changeOrigin: true, secure: false },
  "/users": { target: API_PROXY_TARGET, changeOrigin: true, secure: false },
  "/export": { target: API_PROXY_TARGET, changeOrigin: true, secure: false },
};

const createPwaPlugin = () =>
  VitePWA({
    registerType: "autoUpdate",
    includeAssets: ["frontend_public_favicon.ico", "robots.txt", "sitemap.xml"],
    manifest: {
      name: "Tenantra Platform",
      short_name: "Tenantra",
      description: "Unified IT discovery, security, and compliance dashboard.",
      theme_color: "#1877F2",
      background_color: "#f0f2f5",
      display: "standalone",
      start_url: APP_BASE,
      scope: APP_BASE,
      icons: [
        {
          src: `${APP_BASE}frontend_public_favicon.ico`,
          sizes: "48x48",
          type: "image/x-icon",
        },
      ],
    },
    workbox: {
      navigateFallback: "index.html",
      globPatterns: ["**/*.{js,css,html,svg,png,ico,json,woff2}"],
      runtimeCaching: [
        {
          urlPattern: /^https:\/\/fonts\.gstatic\.com\//,
          handler: "CacheFirst",
          options: {
            cacheName: "google-fonts",
            expiration: { maxEntries: 10, maxAgeSeconds: 60 * 60 * 24 * 365 },
          },
        },
      ],
    },
  });

const catalogFederationPlugin = () =>
  federation({
    name: "tenantra_catalog",
    filename: "remoteEntry.js",
    exposes: {
      "./ModuleCatalog": "./src/mf/catalogRemoteEntry.jsx",
    },
    shared: {
      react: {
        singleton: true,
        eager: true,
        requiredVersion: "^18.3.1",
      },
      "react-dom": {
        singleton: true,
        eager: true,
        requiredVersion: "^18.3.1",
      },
      "@tanstack/react-query": {
        singleton: true,
        eager: true,
        requiredVersion: "^5.59.16",
      },
    },
  });

const resolveBuildTarget = (mode = "") => {
  const hint = (process.env.VITE_BUILD_TARGET || mode || "").toLowerCase();
  if (["catalog-remote", "catalog_remote", "catalogremote", "catalog"].includes(hint)) {
    return "catalog-remote";
  }
  if (hint === "ssr") {
    return "ssr";
  }
  return "spa";
};

export default defineConfig(({ mode }) => {
  const target = resolveBuildTarget(mode);
  const isSsr = target === "ssr";
  const isCatalogRemote = target === "catalog-remote";
  const base = isSsr || isCatalogRemote ? "/" : APP_BASE;

  const plugins = [react()];
  if (!isSsr && !isCatalogRemote) {
    plugins.push(createPwaPlugin());
  }
  if (isCatalogRemote) {
    plugins.push(catalogFederationPlugin());
  }
  if (process.env.ANALYZE === "true") {
    plugins.push(
      visualizer({
        open: false,
        filename: "dist/bundle-analysis.html",
        template: "treemap",
        gzipSize: true,
        brotliSize: true,
      })
    );
  }

  let build = {};
  if (isCatalogRemote) {
    build = {
      modulePreload: false,
      target: "esnext",
      outDir: "dist/catalog-remote",
      emptyOutDir: false,
      rollupOptions: {
        output: {
          format: "esm",
        },
      },
    };
  } else if (isSsr) {
    build = {
      ssr: "src/entry-server.jsx",
      outDir: "dist-ssr",
      minify: false,
      target: "node18",
    };
  }

  return {
    base,
    plugins,
    server: {
      host: "127.0.0.1",
      port: 5173,
      proxy: sharedProxy,
    },
    preview: {
      host: "127.0.0.1",
      port: 4173,
      proxy: sharedProxy,
    },
    build,
  };
});
