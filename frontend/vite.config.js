import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { visualizer } from "rollup-plugin-visualizer";

// Dev proxy: FE calls /api/* (and some legacy /auth, /users, /export) → backend:5000
export default defineConfig(() => {
  const plugins = [react()];
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
