const prefetchers = [
  () => import('../pages/AdminSettings.jsx'),
  () => import('../pages/ObservabilitySetup.jsx'),
  () => import('../pages/ModuleCatalog.jsx'),
];

export function prefetchRoutes() {
  if (typeof window === 'undefined') return;
  const run = () => {
    prefetchers.forEach((loader) => {
      try {
        loader();
      } catch {
        /* ignore */
      }
    });
  };
  if ('requestIdleCallback' in window) {
    window.requestIdleCallback(run, { timeout: 3000 });
  } else {
    window.setTimeout(run, 1500);
  }
}
