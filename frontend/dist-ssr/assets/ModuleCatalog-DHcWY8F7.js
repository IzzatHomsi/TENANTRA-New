import { jsx } from "react/jsx-runtime";
import React from "react";
function loadFederatedModule() {
  if (typeof window === "undefined") {
    return import("./ModuleCatalogLocal-Dl3QisGC.js");
  }
  {
    return import("./ModuleCatalogLocal-Dl3QisGC.js");
  }
}
const FederatedModuleCatalog = React.lazy(loadFederatedModule);
function ModuleCatalog() {
  return /* @__PURE__ */ jsx(FederatedModuleCatalog, {});
}
export {
  ModuleCatalog as default
};
