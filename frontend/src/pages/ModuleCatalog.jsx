import React from "react";

const remoteConfig = {
  url: import.meta.env.VITE_REMOTE_MODULE_CATALOG_URL,
  scope: import.meta.env.VITE_REMOTE_MODULE_CATALOG_SCOPE || "tenantra_catalog",
  module: import.meta.env.VITE_REMOTE_MODULE_CATALOG_MODULE || "./ModuleCatalog",
};

function loadFederatedModule() {
  if (typeof window === "undefined") {
    return import("./ModuleCatalogLocal.jsx");
  }
  const url = remoteConfig.url?.trim();
  if (!url) {
    return import("./ModuleCatalogLocal.jsx");
  }
  return import("../mf/loadRemoteModule.js")
    .then(({ loadRemoteModule }) =>
      loadRemoteModule({ url, scope: remoteConfig.scope, module: remoteConfig.module })
    )
    .catch((error) => {
      console.warn("[Federation] Falling back to local ModuleCatalog:", error);
      return import("./ModuleCatalogLocal.jsx");
    });
}

const FederatedModuleCatalog = React.lazy(loadFederatedModule);

export default function ModuleCatalog() {
  return <FederatedModuleCatalog />;
}
