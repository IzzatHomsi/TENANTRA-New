import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { visualizer } from "rollup-plugin-visualizer";
import { VitePWA } from "vite-plugin-pwa";

const API_PROXY_TARGET = process.env.VITE_API_PROXY_TARGET || "http://localhost:5000";

// Dev proxy: FE calls /api/* (and some legacy /auth, /users, /export) → backend:5000
const APP_BASE = "/app/";

export default defineConfig(() => {
  const plugins = [
    react(),
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
        // The built index.html lives at repository root and Nginx rewrites /app/* → /index.html,
        // so keep the fallback aligned with the precached asset path.
        navigateFallback: "index.html",
        globPatterns: ["**/*.{js,css,html,svg,png,ico,json,woff2}"] ,
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
    }),
  ];
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

  return {
    base: '/app/',
    plugins,
    server: {
      host: "127.0.0.1",
      port: 5173,
      proxy: {
        "/api": { target: API_PROXY_TARGET, changeOrigin: true, secure: false },
        "/auth": { target: API_PROXY_TARGET, changeOrigin: true, secure: false },
        "/users": { target: API_PROXY_TARGET, changeOrigin: true, secure: false },
        "/export": { target: API_PROXY_TARGET, changeOrigin: true, secure: false },
      },
    },
    preview: {
      host: "127.0.0.1",
      port: 4173,
      proxy: {
        "/api": { target: API_PROXY_TARGET, changeOrigin: true, secure: false },
        "/auth": { target: API_PROXY_TARGET, changeOrigin: true, secure: false },
        "/users": { target: API_PROXY_TARGET, changeOrigin: true, secure: false },
        "/export": { target: API_PROXY_TARGET, changeOrigin: true, secure: false },
      },
    },
  };
});
