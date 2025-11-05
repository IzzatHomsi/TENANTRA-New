import { matchRoutes } from "react-router-dom";
import { routeConfig } from "../src/routes/routeConfig.jsx";
import { prefetchSupportSettings } from "../src/queries/supportSettings.js";

const loaders = [
  {
    name: "support-settings",
    matcher: () => true,
    run: async ({ queryClient, apiBase }) => {
      if (!apiBase) return;
      await prefetchSupportSettings(queryClient, apiBase);
    },
  },
];

export async function runLoaders({ url, queryClient, headers, apiBase }) {
  const matches = matchRoutes(routeConfig, url) || [];
  for (const loader of loaders) {
    try {
      const shouldRun = loader.matcher({ url, matches, headers });
      if (shouldRun) {
        await loader.run({ url, matches, headers, queryClient, apiBase });
      }
    } catch (error) {
      console.error(`[SSR] loader ${loader.name} failed`, error);
    }
  }
}
