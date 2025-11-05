import { jsxs, jsx } from "react/jsx-runtime";
import { useState, useCallback, useEffect } from "react";
import { g as getApiBase } from "../entry-server.js";
import { C as Card } from "./Card-BYs02NaX.js";
import { B as Button } from "./Button-C2WBf5y3.js";
import { T as Table } from "./Table-CLWnewy9.js";
import "react-router-dom";
import "@tanstack/react-query";
import "react-router-dom/server.mjs";
const API_BASE = getApiBase();
const authHeaders = (token) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`
});
const fetchCloudData = async (token, endpoint, params = {}) => {
  const qs = new URLSearchParams(params);
  const url = `${API_BASE}${endpoint}?${qs.toString()}`;
  const res = await fetch(url, { headers: authHeaders(token) });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`);
  }
  return res.json();
};
function CloudDiscovery() {
  const [accounts, setAccounts] = useState([]);
  const [assets, setAssets] = useState([]);
  const [filters, setFilters] = useState({ provider: "", account: "" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [accResp, assetResp] = await Promise.all([
        fetchCloudData(token, "/cloud/accounts", { provider: filters.provider }),
        fetchCloudData(token, "/cloud/assets", { provider: filters.provider, account_id: filters.account })
      ]);
      setAccounts(accResp || []);
      setAssets(assetResp || []);
    } catch (err) {
      setError(err.message || "Failed to load cloud inventory");
    } finally {
      setLoading(false);
    }
  }, [token, filters]);
  useEffect(() => {
    loadData();
  }, [loadData]);
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };
  return /* @__PURE__ */ jsxs("div", { className: "bg-facebook-gray p-8", children: [
    /* @__PURE__ */ jsxs("header", { className: "mb-8", children: [
      /* @__PURE__ */ jsx("h1", { className: "text-3xl font-bold text-gray-900", children: "Cloud & Hybrid Discovery" }),
      /* @__PURE__ */ jsx("p", { className: "mt-2 text-sm text-gray-600", children: "Visualize connected cloud accounts and discovered resources across AWS, Azure, and GCP tenants." })
    ] }),
    /* @__PURE__ */ jsx(Card, { className: "mb-8", children: /* @__PURE__ */ jsxs("div", { className: "flex items-center space-x-4", children: [
      /* @__PURE__ */ jsxs(
        "select",
        {
          name: "provider",
          value: filters.provider,
          onChange: handleFilterChange,
          className: "rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm",
          children: [
            /* @__PURE__ */ jsx("option", { value: "", children: "All providers" }),
            /* @__PURE__ */ jsx("option", { value: "aws", children: "AWS" }),
            /* @__PURE__ */ jsx("option", { value: "azure", children: "Azure" }),
            /* @__PURE__ */ jsx("option", { value: "gcp", children: "GCP" })
          ]
        }
      ),
      /* @__PURE__ */ jsx(
        "input",
        {
          name: "account",
          value: filters.account,
          onChange: handleFilterChange,
          placeholder: "Account ID",
          className: "w-48 rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
        }
      ),
      /* @__PURE__ */ jsx(Button, { onClick: loadData, disabled: loading, children: loading ? "Refreshing..." : "Apply" })
    ] }) }),
    error && /* @__PURE__ */ jsx("div", { className: "mb-8 rounded-md bg-red-100 p-4 text-red-700", children: error }),
    /* @__PURE__ */ jsxs("div", { className: "space-y-8", children: [
      /* @__PURE__ */ jsxs(Card, { children: [
        /* @__PURE__ */ jsx("h2", { className: "mb-4 text-xl font-bold text-gray-900", children: "Accounts" }),
        /* @__PURE__ */ jsx("div", { className: "grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3", children: accounts.length === 0 ? /* @__PURE__ */ jsx("div", { className: "text-sm text-gray-500", children: "No cloud accounts connected." }) : accounts.map((account) => /* @__PURE__ */ jsxs("div", { className: "rounded-lg bg-white p-4 shadow", children: [
          /* @__PURE__ */ jsx("div", { className: "text-sm font-medium text-gray-900", children: account.account_identifier }),
          /* @__PURE__ */ jsx("div", { className: "mt-1 text-xs text-gray-500", children: account.provider?.toUpperCase() }),
          /* @__PURE__ */ jsxs("div", { className: "mt-2 text-xs text-gray-500", children: [
            "Status: ",
            account.status
          ] }),
          /* @__PURE__ */ jsxs("div", { className: "text-xs text-gray-500", children: [
            "Last Sync: ",
            account.last_synced_at || "Never"
          ] }),
          /* @__PURE__ */ jsx("p", { className: "mt-2 text-xs text-gray-500", children: account.notes || "" })
        ] }, account.id)) })
      ] }),
      /* @__PURE__ */ jsxs(Card, { children: [
        /* @__PURE__ */ jsx("h2", { className: "mb-4 text-xl font-bold text-gray-900", children: "Discovered Assets" }),
        /* @__PURE__ */ jsx(
          Table,
          {
            columns: [
              { key: "account_id", label: "Account" },
              { key: "name", label: "Name" },
              { key: "asset_type", label: "Type" },
              { key: "region", label: "Region" },
              { key: "status", label: "Status" },
              { key: "metadata", label: "Metadata" }
            ],
            rows: assets,
            empty: "No assets discovered for this filter."
          }
        )
      ] })
    ] })
  ] });
}
export {
  CloudDiscovery as default
};
