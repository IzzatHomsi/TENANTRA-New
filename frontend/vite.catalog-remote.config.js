import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import federation from "@originjs/vite-plugin-federation";

export default defineConfig({
  plugins: [
    react(),
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
    }),
  ],
  build: {
    modulePreload: false,
    target: "esnext",
    outDir: "dist/catalog-remote",
    emptyOutDir: false,
    rollupOptions: {
      output: {
        format: "esm",
      },
    },
  },
});
