import { jsx, jsxs } from "react/jsx-runtime";
import { useState, useEffect, useMemo, useCallback } from "react";
import { useLocation } from "react-router-dom";
import { useQueryClient, useQuery, useMutation } from "@tanstack/react-query";
import { g as getApiBase, u as useAuth } from "../entry-server.js";
import { C as Card } from "./Card-BYs02NaX.js";
import { B as Button } from "./Button-C2WBf5y3.js";
import { T as Table } from "./Table-CLWnewy9.js";
import { u as useUIStore, a as apiFetch } from "./apiClient-Y8eZ7muQ.js";
import { f as fetchTenants } from "./tenants-Cz2KWSMQ.js";
import { z } from "zod";
import "react-router-dom/server.mjs";
import "zustand";
import "zustand/middleware";
function ModuleList({ modules, selectedId, onSelect }) {
  if (!modules.length) {
    return /* @__PURE__ */ jsx("div", { className: "text-gray-500", children: "No modules match the current filters." });
  }
  return /* @__PURE__ */ jsx("div", { className: "max-h-[70vh] space-y-3 overflow-y-auto pr-2", children: modules.map((module) => /* @__PURE__ */ jsxs(
    "button",
    {
      onClick: () => onSelect(module.id),
      className: `w-full rounded-lg border p-4 text-left ${selectedId === module.id ? "border-facebook-blue bg-blue-50" : "border-gray-200 bg-white"}`,
      children: [
        /* @__PURE__ */ jsx("div", { className: "font-semibold", children: module.name }),
        /* @__PURE__ */ jsxs("div", { className: "text-sm text-gray-500", children: [
          module.category || "Uncategorised",
          module.phase !== null && module.phase !== void 0 ? ` • Phase ${module.phase}` : ""
        ] }),
        /* @__PURE__ */ jsxs("div", { className: `text-sm ${module.enabled ? "text-green-600" : "text-red-600"}`, children: [
          module.enabled ? "Enabled" : "Disabled",
          module.has_runner ? " • Runnable" : " • No runner"
        ] })
      ]
    },
    module.id
  )) });
}
function MetadataRow({ label, value }) {
  return /* @__PURE__ */ jsxs("div", { className: "grid grid-cols-3 gap-4 text-sm", children: [
    /* @__PURE__ */ jsx("div", { className: "text-gray-500", children: label }),
    /* @__PURE__ */ jsx("div", { className: "col-span-2", children: value ?? "-" })
  ] });
}
function SchemaSummary({ schema }) {
  if (!schema || Object.keys(schema).length === 0) {
    return /* @__PURE__ */ jsx("div", { className: "text-sm text-gray-500", children: "This module accepts arbitrary parameters. Use JSON payloads when running manually." });
  }
  const properties = Object.entries(schema.properties || {});
  return /* @__PURE__ */ jsx("div", { className: "space-y-4", children: properties.length === 0 ? /* @__PURE__ */ jsx("div", { className: "text-sm text-gray-500", children: "This module accepts arbitrary parameters. Use JSON payloads when running manually." }) : properties.map(([key, descriptor]) => /* @__PURE__ */ jsxs("div", { className: "rounded-md border p-4", children: [
    /* @__PURE__ */ jsx("div", { className: "font-semibold", children: key }),
    /* @__PURE__ */ jsx("div", { className: "mt-1 text-sm text-gray-600", children: descriptor.description || "No description provided." }),
    descriptor.type && /* @__PURE__ */ jsxs("div", { className: "mt-2 text-xs text-gray-500", children: [
      "Type: ",
      descriptor.type
    ] }),
    Array.isArray(descriptor.enum) && /* @__PURE__ */ jsxs("div", { className: "mt-2 text-xs text-gray-500", children: [
      "Allowed values: ",
      descriptor.enum.join(", ")
    ] })
  ] }, key)) });
}
function ModuleDetails({ module, onToggleEnabled }) {
  if (!module) {
    return /* @__PURE__ */ jsx("div", { className: "text-gray-500", children: "Select a module to view details." });
  }
  return /* @__PURE__ */ jsxs("div", { className: "space-y-6", children: [
    /* @__PURE__ */ jsxs("div", { className: "flex items-center justify-between", children: [
      /* @__PURE__ */ jsxs("div", { children: [
        /* @__PURE__ */ jsx("h2", { className: "text-2xl font-bold", children: module.name }),
        /* @__PURE__ */ jsxs("div", { className: "text-sm text-gray-500", children: [
          module.category || "Uncategorised",
          module.phase !== null && module.phase !== void 0 ? ` • Phase ${module.phase}` : ""
        ] })
      ] }),
      /* @__PURE__ */ jsx(
        "button",
        {
          onClick: () => onToggleEnabled(module),
          className: `rounded-md px-4 py-2 text-sm font-medium ${module.enabled ? "bg-red-100 text-red-700" : "bg-green-100 text-green-700"}`,
          children: module.enabled ? "Disable" : "Enable"
        }
      )
    ] }),
    /* @__PURE__ */ jsxs("div", { className: "space-y-4", children: [
      /* @__PURE__ */ jsx(MetadataRow, { label: "Impact", value: module.impact_level }),
      /* @__PURE__ */ jsx(MetadataRow, { label: "Purpose", value: module.purpose || module.description }),
      /* @__PURE__ */ jsx(MetadataRow, { label: "Dependencies", value: module.dependencies }),
      /* @__PURE__ */ jsx(MetadataRow, { label: "Preconditions", value: module.preconditions }),
      /* @__PURE__ */ jsx(MetadataRow, { label: "Team", value: module.team }),
      /* @__PURE__ */ jsx(MetadataRow, { label: "Targets", value: module.application_target }),
      /* @__PURE__ */ jsx(MetadataRow, { label: "Supported OS", value: module.operating_systems }),
      /* @__PURE__ */ jsx(MetadataRow, { label: "Compliance", value: module.compliance_mapping }),
      /* @__PURE__ */ jsx(MetadataRow, { label: "Last update", value: new Date(module.last_update).toLocaleString() }),
      /* @__PURE__ */ jsx(MetadataRow, { label: "Runner available", value: module.has_runner ? "Yes" : "No" })
    ] }),
    /* @__PURE__ */ jsxs("div", { children: [
      /* @__PURE__ */ jsx("h3", { className: "mb-4 text-xl font-bold", children: "Parameter Schema" }),
      /* @__PURE__ */ jsx(SchemaSummary, { schema: module.parameter_schema })
    ] })
  ] });
}
function RunModule({ module, onRun, runError, runMessage, runBusy }) {
  const [useForm, setUseForm] = useState(true);
  const [formValues, setFormValues] = useState({});
  const [runPayload, setRunPayload] = useState("{}");
  useEffect(() => {
    if (!module) {
      setFormValues({});
      return;
    }
    const props = module.parameter_schema && module.parameter_schema.properties || {};
    const init = {};
    Object.entries(props).forEach(([key, desc]) => {
      if (desc && typeof desc === "object" && "default" in desc) {
        init[key] = desc.default;
      } else {
        init[key] = "";
      }
    });
    setFormValues(init);
    try {
      setRunPayload(JSON.stringify(init, null, 2));
    } catch {
    }
  }, [module]);
  const handleRun = () => {
    let payload;
    try {
      if (useForm) {
        payload = { ...formValues };
      } else {
        payload = runPayload.trim() ? JSON.parse(runPayload) : {};
      }
    } catch (err) {
      onRun(null, "Parameters must be valid JSON.");
      return;
    }
    onRun(payload);
  };
  return /* @__PURE__ */ jsxs("div", { children: [
    /* @__PURE__ */ jsx("h3", { className: "mb-4 text-xl font-bold", children: "Run Module" }),
    /* @__PURE__ */ jsxs("div", { className: "mb-4 flex items-center", children: [
      /* @__PURE__ */ jsx(
        "input",
        {
          type: "checkbox",
          checked: useForm,
          onChange: (e) => setUseForm(e.target.checked),
          className: "h-4 w-4 rounded border-gray-300 text-facebook-blue focus:ring-facebook-blue"
        }
      ),
      /* @__PURE__ */ jsx("label", { className: "ml-2 text-sm text-gray-700", children: "Use parameter form" })
    ] }),
    useForm && module?.parameter_schema?.properties ? /* @__PURE__ */ jsx("div", { className: "mb-4 space-y-4", children: Object.entries(module.parameter_schema.properties).map(([key, descriptor]) => /* @__PURE__ */ jsxs("div", { children: [
      /* @__PURE__ */ jsxs("label", { className: "block text-sm font-medium text-gray-700", children: [
        key,
        " ",
        descriptor?.type ? /* @__PURE__ */ jsxs("span", { className: "text-gray-500", children: [
          "(",
          descriptor.type,
          ")"
        ] }) : null
      ] }),
      /* @__PURE__ */ jsx(
        "input",
        {
          value: formValues[key] ?? "",
          onChange: (e) => {
            const v = e.target.value;
            const next = { ...formValues, [key]: descriptor?.type === "number" ? Number(v) : v };
            setFormValues(next);
            try {
              setRunPayload(JSON.stringify(next, null, 2));
            } catch {
            }
          },
          placeholder: descriptor?.description || "",
          className: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
        }
      )
    ] }, key)) }) : /* @__PURE__ */ jsx(
      "textarea",
      {
        value: runPayload,
        onChange: (e) => setRunPayload(e.target.value),
        rows: 8,
        className: "w-full rounded-md border-gray-300 font-mono text-sm shadow-sm focus:border-facebook-blue focus:ring-facebook-blue"
      }
    ),
    runError && /* @__PURE__ */ jsx("div", { className: "mt-4 rounded-md bg-red-100 p-4 text-red-700", children: runError }),
    runMessage && /* @__PURE__ */ jsx("div", { className: "mt-4 rounded-md bg-green-100 p-4 text-green-700", children: runMessage }),
    /* @__PURE__ */ jsx("div", { className: "mt-4 flex space-x-4", children: /* @__PURE__ */ jsx(Button, { onClick: handleRun, disabled: runBusy, children: runBusy ? "Running..." : "Execute now" }) })
  ] });
}
const API_BASE$2 = getApiBase();
const authHeaders$2 = (token) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`
});
const formatDate$1 = (value) => {
  if (!value) return "?";
  return new Date(value).toLocaleString();
};
function ScheduleModule({ module, isAdmin, token }) {
  const [schedules, setSchedules] = useState([]);
  const [loadingSchedules, setLoadingSchedules] = useState(false);
  const [scheduleError, setScheduleError] = useState("");
  const [scheduleMessage, setScheduleMessage] = useState("");
  const [scheduleForm, setScheduleForm] = useState({ cron_expr: "*/30 * * * *", agent_id: "" });
  const [agents, setAgents] = useState([]);
  const [tenantId, setTenantId] = useState("");
  const { tenants } = useUIStore();
  useEffect(() => {
    if (module) {
      loadSchedules(module.id);
    }
  }, [module]);
  useEffect(() => {
    (async () => {
      if (!isAdmin) return;
      if (tenants.length > 0) return;
      try {
        await fetchTenants(token);
      } catch {
      }
    })();
  }, [isAdmin, token, tenants.length]);
  useEffect(() => {
    (async () => {
      if (!isAdmin) return;
      try {
        const qs = tenantId ? `?tenant_id=${tenantId}` : "";
        const res = await fetch(`${API_BASE$2}/admin/agents${qs}`, { headers: authHeaders$2(token) });
        if (res.ok) {
          setAgents(await res.json());
        }
      } catch {
        setAgents([]);
      }
    })();
  }, [isAdmin, token, tenantId]);
  const loadSchedules = async (moduleId) => {
    setLoadingSchedules(true);
    setScheduleError("");
    try {
      const qs = `?module_id=${moduleId}`;
      const res = await fetch(`${API_BASE$2}/schedules${qs}`, { headers: authHeaders$2(token) });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const data = await res.json();
      setSchedules(Array.isArray(data) ? data : []);
    } catch (err) {
      setScheduleError(err.message || "Unable to load schedules");
    } finally {
      setLoadingSchedules(false);
    }
  };
  const createSchedule = async () => {
    setScheduleError("");
    setScheduleMessage("");
    let agentId = scheduleForm.agent_id.trim();
    if (agentId) {
      const parsed = Number(agentId);
      if (isNaN(parsed) || parsed < 0) {
        setScheduleError("Agent ID must be numeric.");
        return;
      }
      agentId = parsed;
    } else {
      agentId = null;
    }
    try {
      const payload = {
        module_id: module.id,
        cron_expr: scheduleForm.cron_expr.trim() || "*/30 * * * *",
        agent_id: agentId
      };
      if (isAdmin && tenantId) {
        payload.tenant_id = Number(tenantId);
      }
      const res = await fetch(`${API_BASE$2}/schedules`, {
        method: "POST",
        headers: authHeaders$2(token),
        body: JSON.stringify(payload)
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      setScheduleMessage("Schedule created.");
      setScheduleForm((prev) => ({ ...prev, agent_id: "" }));
      loadSchedules(module.id);
    } catch (err) {
      setScheduleError(err.message || "Unable to create schedule");
    }
  };
  const deleteSchedule = async (scheduleId) => {
    setScheduleError("");
    try {
      const res = await fetch(`${API_BASE$2}/schedules/${scheduleId}`, {
        method: "DELETE",
        headers: authHeaders$2(token)
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      setScheduleMessage("Schedule removed.");
      loadSchedules(module.id);
    } catch (err) {
      setScheduleError(err.message || "Unable to delete schedule");
    }
  };
  const scheduleColumns = [
    { key: "cron_expr", label: "Cron" },
    { key: "agent_id", label: "Agent" },
    { key: "next_run_at", label: "Next Run", render: (v) => formatDate$1(v) },
    { key: "status", label: "Status", render: (v) => v?.toUpperCase() ?? v },
    {
      key: "actions",
      label: "",
      render: (v, row) => /* @__PURE__ */ jsx(Button, { variant: "ghost", onClick: () => deleteSchedule(row.id), className: "text-red-600 hover:text-red-900", children: "Remove" })
    }
  ];
  return /* @__PURE__ */ jsxs("div", { children: [
    /* @__PURE__ */ jsx("h3", { className: "mb-4 text-xl font-bold", children: "Schedules" }),
    scheduleError && /* @__PURE__ */ jsx("div", { className: "mb-4 rounded-md bg-red-100 p-4 text-red-700", children: scheduleError }),
    scheduleMessage && /* @__PURE__ */ jsx("div", { className: "mb-4 rounded-md bg-green-100 p-4 text-green-700", children: scheduleMessage }),
    isAdmin && /* @__PURE__ */ jsxs("div", { className: "mb-6 rounded-lg border bg-white p-4 shadow-sm", children: [
      /* @__PURE__ */ jsx("h4", { className: "mb-4 text-lg font-medium", children: "Create New Schedule" }),
      /* @__PURE__ */ jsxs("div", { className: "grid grid-cols-1 gap-4 md:grid-cols-2", children: [
        /* @__PURE__ */ jsxs("div", { children: [
          /* @__PURE__ */ jsx("label", { className: "block text-sm font-medium text-gray-700", children: "Cron Expression" }),
          /* @__PURE__ */ jsx(
            "input",
            {
              value: scheduleForm.cron_expr,
              onChange: (e) => setScheduleForm((prev) => ({ ...prev, cron_expr: e.target.value })),
              placeholder: "*/30 * * * *",
              className: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
            }
          )
        ] }),
        /* @__PURE__ */ jsxs("div", { children: [
          /* @__PURE__ */ jsx("label", { className: "block text-sm font-medium text-gray-700", children: "Agent ID (optional)" }),
          /* @__PURE__ */ jsxs(
            "select",
            {
              value: scheduleForm.agent_id,
              onChange: (e) => setScheduleForm((prev) => ({ ...prev, agent_id: e.target.value })),
              className: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm",
              children: [
                /* @__PURE__ */ jsx("option", { value: "", children: "Unassigned" }),
                agents.map((agent) => /* @__PURE__ */ jsxs("option", { value: agent.id, children: [
                  agent.name,
                  " (#",
                  agent.id,
                  ")"
                ] }, agent.id))
              ]
            }
          )
        ] }),
        isAdmin && /* @__PURE__ */ jsxs("div", { children: [
          /* @__PURE__ */ jsx("label", { className: "block text-sm font-medium text-gray-700", children: "Tenant (admin)" }),
          /* @__PURE__ */ jsxs(
            "select",
            {
              value: tenantId,
              onChange: (e) => setTenantId(e.target.value),
              className: "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm",
              children: [
                /* @__PURE__ */ jsx("option", { value: "", children: "Current tenant" }),
                tenants.map((t) => /* @__PURE__ */ jsx("option", { value: t.id, children: t.name }, t.id))
              ]
            }
          )
        ] })
      ] }),
      /* @__PURE__ */ jsx(Button, { onClick: createSchedule, className: "mt-4", children: "Create Schedule" })
    ] }),
    /* @__PURE__ */ jsx("h4", { className: "mb-2 text-lg font-medium", children: "Existing Schedules" }),
    loadingSchedules ? /* @__PURE__ */ jsx("p", { children: "Loading schedules..." }) : schedules.length === 0 ? /* @__PURE__ */ jsx("p", { children: "No schedules defined for this module." }) : /* @__PURE__ */ jsx(Table, { columns: scheduleColumns, rows: schedules, empty: "No schedules defined for this module." })
  ] });
}
const API_BASE$1 = getApiBase();
const authHeaders$1 = (token) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`
});
const formatDate = (value) => {
  if (!value) return "?";
  return new Date(value).toLocaleString();
};
const renderFindingSummary = (f) => {
  const parts = [];
  parts.push(`${f.host}:${f.port} ${String(f.status || "").toUpperCase()}`);
  if (f.http) {
    const h = f.http;
    const code = h.status_code ? ` ${h.status_code}` : "";
    const srv = h.server ? ` ${h.server}` : "";
    parts.push(`[HTTP${code}${srv}]`);
  }
  if (Array.isArray(f.software) && f.software.length) {
    const s = f.software[0];
    parts.push(`[SW ${s.product}${s.version ? ` ${s.version}` : ""}]`);
  }
  if (f.tls) {
    const t = f.tls;
    const exp = typeof t.expires_in_days === "number" ? ` exp ${t.expires_in_days}d` : "";
    parts.push(`[TLS ${t.protocol || ""}${exp}]`);
  }
  return parts.join(" • ");
};
function ModuleRuns({ module, token }) {
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => {
    if (module) {
      loadRuns(module.id);
    }
  }, [module]);
  const loadRuns = async (moduleId) => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE$1}/module-runs?module_id=${moduleId}`, { headers: authHeaders$1(token) });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const data = await res.json();
      setRuns(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message || "Failed to load module runs");
    } finally {
      setLoading(false);
    }
  };
  const columns = [
    { key: "recorded_at", label: "Recorded At", render: (v) => formatDate(v) },
    { key: "status", label: "Status", render: (v) => v?.toUpperCase() ?? v },
    { key: "findings_count", label: "Findings", render: (v, row) => row.details?.findings?.length || 0 },
    { key: "details", label: "Details", render: (v) => v?.findings && v.findings.length ? /* @__PURE__ */ jsxs("ul", { className: "list-disc pl-5", children: [
      v.findings.slice(0, 3).map((f, i) => /* @__PURE__ */ jsx("li", { title: JSON.stringify(f, null, 2), children: renderFindingSummary(f) }, i)),
      v.findings.length > 3 && /* @__PURE__ */ jsx("li", { children: "..." })
    ] }) : "-" }
  ];
  return /* @__PURE__ */ jsxs("div", { children: [
    /* @__PURE__ */ jsx("h3", { className: "mb-4 text-xl font-bold", children: "Module Runs" }),
    error && /* @__PURE__ */ jsx("div", { className: "mb-4 rounded-md bg-red-100 p-4 text-red-700", children: error }),
    loading ? /* @__PURE__ */ jsx("p", { children: "Loading module runs..." }) : runs.length === 0 ? /* @__PURE__ */ jsx("p", { children: "No runs recorded for this module." }) : /* @__PURE__ */ jsx(Table, { columns, rows: runs, empty: "No runs recorded for this module." })
  ] });
}
const moduleSchema = z.object({
  id: z.union([z.string(), z.number()]).transform((value) => String(value)),
  name: z.string().optional().default(""),
  category: z.string().nullable().optional(),
  description: z.string().nullable().optional(),
  purpose: z.string().nullable().optional(),
  phase: z.union([z.number(), z.string()]).nullable().optional(),
  enabled: z.boolean().optional().default(false),
  has_runner: z.boolean().optional().default(false)
});
const moduleListSchema = z.array(moduleSchema);
async function fetchModules(token) {
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  return apiFetch("/modules/", moduleListSchema, { headers });
}
async function updateModule(id, payload, token) {
  const headers = {
    Authorization: token ? `Bearer ${token}` : void 0,
    "Content-Type": "application/json"
  };
  const schema = moduleSchema;
  return apiFetch(`/modules/${id}`, schema, {
    method: "PUT",
    headers,
    body: JSON.stringify(payload)
  });
}
const API_BASE = getApiBase();
const authHeaders = (token) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`
});
function ModuleCatalogLocal() {
  const { role, signOut } = useAuth();
  const location = useLocation();
  const isAdmin = role === "admin" || role === "super_admin";
  const queryClient = useQueryClient();
  const [selectedId, setSelectedId] = useState(null);
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [phaseFilter, setPhaseFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [actionError, setActionError] = useState("");
  const [runError, setRunError] = useState("");
  const [runMessage, setRunMessage] = useState("");
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const modulesQueryKey = useMemo(() => ["modules", token], [token]);
  const {
    data: modules = [],
    isPending,
    isFetching,
    error: modulesError,
    refetch
  } = useQuery({
    queryKey: modulesQueryKey,
    enabled: Boolean(token),
    queryFn: async ({ signal }) => {
      if (!token) {
        throw new Error("Not authenticated.");
      }
      if (signal.aborted) return [];
      try {
        const modules2 = await fetchModules(token);
        return modules2;
      } catch (error) {
        if (error?.status === 401) {
          signOut?.();
        }
        throw error;
      }
    }
  });
  useEffect(() => {
    try {
      const params = new URLSearchParams(location.search || "");
      const q = params.get("q");
      const cat = params.get("category");
      if (q) setSearch(q);
      if (cat) setCategoryFilter(cat);
    } catch {
    }
  }, [location.search]);
  useEffect(() => {
    if (!selectedId && modules.length) {
      setSelectedId(modules[0].id);
    }
  }, [modules, selectedId]);
  const modulesErrorMessage = modulesError instanceof Error ? modulesError.message : "";
  const errorMessage = [modulesErrorMessage, actionError].filter(Boolean).join(" • ");
  const loading = isPending || isFetching;
  const categories = useMemo(() => {
    const set = new Set(modules.map((m) => m.category).filter(Boolean));
    return Array.from(set).sort((a, b) => a.localeCompare(b));
  }, [modules]);
  const phases = useMemo(() => {
    const set = new Set(modules.map((m) => m.phase).filter((phase) => phase !== null && phase !== void 0));
    return Array.from(set).sort((a, b) => a - b);
  }, [modules]);
  const filteredModules = useMemo(() => {
    const term = search.trim().toLowerCase();
    return modules.filter((module) => {
      if (term) {
        const hay = `${module.name ?? ""} ${module.category ?? ""} ${module.description ?? ""} ${module.purpose ?? ""}`.toLowerCase();
        if (!hay.includes(term)) return false;
      }
      if (categoryFilter && module.category !== categoryFilter) {
        return false;
      }
      if (phaseFilter && String(module.phase ?? "") !== phaseFilter) {
        return false;
      }
      if (statusFilter === "enabled" && !module.enabled) {
        return false;
      }
      if (statusFilter === "disabled" && module.enabled) {
        return false;
      }
      return true;
    }).sort((a, b) => a.name.localeCompare(b.name));
  }, [modules, search, categoryFilter, phaseFilter, statusFilter]);
  const selectedModule = useMemo(
    () => modules.find((m) => m.id === selectedId) || null,
    [modules, selectedId]
  );
  const toggleModule = useMutation({
    mutationFn: async ({ module }) => {
      if (!token) {
        const err = new Error("Missing authentication token.");
        err.status = 401;
        throw err;
      }
      const payload = { enabled: !module.enabled };
      try {
        const updated = await updateModule(module.id, payload, token);
        return updated;
      } catch (error) {
        if (error?.status === 401) {
          signOut?.();
        }
        throw error;
      }
    },
    onSuccess: (updated) => {
      queryClient.setQueryData(
        modulesQueryKey,
        (prev = []) => prev.map((item) => item.id === updated.id ? { ...item, ...updated } : item)
      );
      setActionError("");
    },
    onError: (err) => {
      setActionError(err?.message || "Failed to update module state.");
    }
  });
  const handleToggleEnabled = useCallback(
    (module) => {
      if (!module) return;
      setActionError("");
      toggleModule.mutate({ module });
    },
    [toggleModule]
  );
  const runModule = useMutation({
    mutationFn: async ({ moduleId, parameters }) => {
      if (!token) {
        const err = new Error("Missing authentication token.");
        err.status = 401;
        throw err;
      }
      const res = await fetch(`${API_BASE}/module-runs/${moduleId}`, {
        method: "POST",
        headers: authHeaders(token),
        body: JSON.stringify({ parameters })
      });
      if (res.status === 401) {
        signOut?.();
        const err = new Error("Session expired. Please sign in again.");
        err.status = 401;
        throw err;
      }
      if (!res.ok) {
        const err = new Error(`Module execution failed (HTTP ${res.status}).`);
        err.status = res.status;
        throw err;
      }
      return res.json();
    },
    onSuccess: (response) => {
      const timestamp = response?.recorded_at ? new Date(response.recorded_at).toLocaleString() : (/* @__PURE__ */ new Date()).toLocaleString();
      const status = response?.status ? String(response.status).toUpperCase() : "UNKNOWN";
      setRunError("");
      setRunMessage(`Run recorded with status ${status} at ${timestamp}.`);
    },
    onError: (err) => {
      setRunMessage("");
      setRunError(err?.message || "Module execution failed.");
    }
  });
  const runBusy = runModule.isPending;
  const handleRunModule = useCallback(
    (payload, validationError) => {
      if (validationError) {
        setRunError(validationError);
        return;
      }
      if (!selectedModule) return;
      setRunMessage("");
      setRunError("");
      runModule.mutate({ moduleId: selectedModule.id, parameters: payload });
    },
    [runModule, selectedModule]
  );
  const handleReload = useCallback(() => {
    setActionError("");
    refetch();
  }, [refetch]);
  return /* @__PURE__ */ jsxs("div", { className: "bg-facebook-gray p-8", children: [
    /* @__PURE__ */ jsxs("header", { className: "mb-8", children: [
      /* @__PURE__ */ jsx("h1", { className: "text-3xl font-bold text-gray-900", children: "Module Catalog" }),
      /* @__PURE__ */ jsx("p", { className: "mt-2 text-sm text-gray-600", children: "Browse, execute, and schedule Tenantra scanning modules. Filters honour tenant subscriptions and your assigned role." })
    ] }),
    errorMessage && /* @__PURE__ */ jsx("div", { className: "mb-4 rounded-md bg-red-100 p-4 text-red-700", children: errorMessage }),
    /* @__PURE__ */ jsxs("div", { className: "mb-6 flex flex-wrap items-center gap-4", children: [
      /* @__PURE__ */ jsx(
        "input",
        {
          value: search,
          onChange: (e) => setSearch(e.target.value),
          placeholder: "Search modules...",
          className: "w-full max-w-xs rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
        }
      ),
      /* @__PURE__ */ jsxs(
        "select",
        {
          value: categoryFilter,
          onChange: (e) => setCategoryFilter(e.target.value),
          className: "rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm",
          children: [
            /* @__PURE__ */ jsx("option", { value: "", children: "All categories" }),
            categories.map((category) => /* @__PURE__ */ jsx("option", { value: category, children: category }, category))
          ]
        }
      ),
      /* @__PURE__ */ jsxs(
        "select",
        {
          value: phaseFilter,
          onChange: (e) => setPhaseFilter(e.target.value),
          className: "rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm",
          children: [
            /* @__PURE__ */ jsx("option", { value: "", children: "Any phase" }),
            phases.map((phase) => /* @__PURE__ */ jsxs("option", { value: String(phase), children: [
              "Phase ",
              phase
            ] }, phase))
          ]
        }
      ),
      /* @__PURE__ */ jsxs(
        "select",
        {
          value: statusFilter,
          onChange: (e) => setStatusFilter(e.target.value),
          className: "rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm",
          children: [
            /* @__PURE__ */ jsx("option", { value: "all", children: "All states" }),
            /* @__PURE__ */ jsx("option", { value: "enabled", children: "Enabled" }),
            /* @__PURE__ */ jsx("option", { value: "disabled", children: "Disabled" })
          ]
        }
      ),
      /* @__PURE__ */ jsx(Button, { onClick: handleReload, disabled: loading, children: loading ? "Refreshing..." : "Reload" })
    ] }),
    /* @__PURE__ */ jsxs("div", { className: "grid grid-cols-1 gap-8 md:grid-cols-3", children: [
      /* @__PURE__ */ jsx("div", { className: "md:col-span-1", children: /* @__PURE__ */ jsx(Card, { children: /* @__PURE__ */ jsx(ModuleList, { modules: filteredModules, selectedId, onSelect: setSelectedId }) }) }),
      /* @__PURE__ */ jsxs("div", { className: "md:col-span-2", children: [
        /* @__PURE__ */ jsx(Card, { children: /* @__PURE__ */ jsx(ModuleDetails, { module: selectedModule, onToggleEnabled: handleToggleEnabled }) }),
        selectedModule && /* @__PURE__ */ jsxs("div", { className: "mt-8 space-y-8", children: [
          /* @__PURE__ */ jsx(Card, { children: /* @__PURE__ */ jsx(
            RunModule,
            {
              module: selectedModule,
              onRun: handleRunModule,
              runError,
              runMessage,
              runBusy
            }
          ) }),
          /* @__PURE__ */ jsx(Card, { children: /* @__PURE__ */ jsx(ScheduleModule, { module: selectedModule, isAdmin, token }) }),
          /* @__PURE__ */ jsx(Card, { children: /* @__PURE__ */ jsx(ModuleRuns, { module: selectedModule, token }) })
        ] })
      ] })
    ] })
  ] });
}
export {
  ModuleCatalogLocal as default
};
