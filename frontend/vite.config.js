import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { visualizer } from "rollup-plugin-visualizer";
import { VitePWA } from "vite-plugin-pwa";

// Dev proxy: FE calls /api/* (and some legacy /auth, /users, /export) → backend:5000
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
        start_url: "/",
        icons: [
          {
            src: "/frontend_public_favicon.ico",
            sizes: "48x48",
            type: "image/x-icon",
          },
        ],
      },
      workbox: {
        navigateFallback: "/index.html",
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
          {
            urlPattern: ({ url }) => url.pathname.startsWith("/api/"),
            handler: "NetworkFirst",
            options: {
              cacheName: "api-cache",
              networkTimeoutSeconds: 5,
              expiration: { maxEntries: 50, maxAgeSeconds: 60 * 5 },
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
      port: 5173,
      proxy: {
        "/api": { target: "http://localhost:5000", changeOrigin: true, secure: false },
        "/auth": { target: "http://localhost:5000", changeOrigin: true, secure: false },
        "/users": { target: "http://localhost:5000", changeOrigin: true, secure: false },
        "/export": { target: "http://localhost:5000", changeOrigin: true, secure: false },
      },
    },
  };
});
