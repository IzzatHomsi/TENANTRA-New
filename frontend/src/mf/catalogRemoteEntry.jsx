import React from "react";
import ModuleCatalogLocal from "../pages/ModuleCatalogLocal.jsx";

// The remote re-exports the same component used by the host fallback.
// All providers (Auth, Theme, Query) are expected to be supplied by the host.
export default function ModuleCatalogRemote(props) {
  return <ModuleCatalogLocal {...props} />;
}
