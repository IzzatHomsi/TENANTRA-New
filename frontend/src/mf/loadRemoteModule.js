const remoteCache = new Map();

async function loadRemoteEntry(url, scope) {
  if (typeof window === "undefined") {
    throw new Error("Remote loading is not available during SSR.");
  }
  if (remoteCache.has(scope)) {
    return remoteCache.get(scope);
  }

  const existing = document.querySelector(`script[data-remote-scope="${scope}"]`);
  if (existing && existing.dataset.loaded === "true") {
    const container = window[scope];
    if (!container) throw new Error(`Remote scope "${scope}" not found after existing script load.`);
    remoteCache.set(scope, container);
    return container;
  }

  await new Promise((resolve, reject) => {
    if (existing) {
      existing.addEventListener("load", resolve, { once: true });
      existing.addEventListener("error", () => reject(new Error(`Failed to load remote script ${url}`)), {
        once: true,
      });
      return;
    }

    const script = document.createElement("script");
    script.src = url;
    script.type = "text/javascript";
    script.async = true;
    script.dataset.remoteScope = scope;
    script.onload = () => {
      script.dataset.loaded = "true";
      resolve();
    };
    script.onerror = () => reject(new Error(`Failed to load remote script ${url}`));
    document.head.appendChild(script);
  });

  const container = window[scope];
  if (!container) {
    throw new Error(`Remote scope "${scope}" not found on window after loading ${url}.`);
  }
  remoteCache.set(scope, container);
  return container;
}

export async function loadRemoteModule({ url, scope, module }) {
  const container = await loadRemoteEntry(url, scope);
  // Webpack Module Federation style
  if (typeof container.get === "function") {
    const factory = await container.get(module);
    if (typeof factory !== "function") {
      throw new Error(`Remote module "${module}" from scope "${scope}" did not return a factory function.`);
    }
    const mod = factory();
    return mod;
  }
  // Simple namespace style: container.modules?.[module] or container[module]
  if (container.modules && container.modules[module]) {
    return container.modules[module];
  }
  if (container[module]) {
    return container[module];
  }
  throw new Error(`Remote module "${module}" not found in scope "${scope}".`);
}

export function resetRemoteModuleCache() {
  remoteCache.clear();
  if (typeof window !== "undefined") {
    document
      .querySelectorAll("script[data-remote-scope]")
      .forEach((script) => script.parentElement?.removeChild(script));
  }
}
