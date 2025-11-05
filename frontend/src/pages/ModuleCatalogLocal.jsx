import React, { useEffect, useMemo, useState, useCallback } from "react";
import { useLocation } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getApiBase } from "../utils/apiBase";
import { useAuth } from "../context/AuthContext.jsx";
import Card from "../components/ui/Card.jsx";
import Button from "../components/ui/Button.jsx";
import ModuleList from "../components/modules/ModuleList.jsx";
import ModuleDetails from "../components/modules/ModuleDetails.jsx";
import RunModule from "../components/modules/RunModule.jsx";
import ScheduleModule from "../components/modules/ScheduleModule.jsx";
import ModuleRuns from "../components/modules/ModuleRuns.jsx";
import { fetchModules, updateModule } from "../api/modules";

const API_BASE = getApiBase();

const authHeaders = (token) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`,
});

export default function ModuleCatalogLocal() {
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
    refetch,
  } = useQuery({
    queryKey: modulesQueryKey,
    enabled: Boolean(token),
    queryFn: async ({ signal }) => {
      if (!token) {
        throw new Error("Not authenticated.");
      }
      if (signal.aborted) return [];
      try {
        const modules = await fetchModules(token);
        return modules;
      } catch (error) {
        // @ts-expect-error status is attached in apiFetch
        if (error?.status === 401) {
          signOut?.();
        }
        throw error;
      }
    },
  });

  useEffect(() => {
    try {
      const params = new URLSearchParams(location.search || "");
      const q = params.get("q");
      const cat = params.get("category");
      if (q) setSearch(q);
      if (cat) setCategoryFilter(cat);
    } catch {
      // ignore malformed query params
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
    const set = new Set(modules.map((m) => m.phase).filter((phase) => phase !== null && phase !== undefined));
    return Array.from(set).sort((a, b) => a - b);
  }, [modules]);

  const filteredModules = useMemo(() => {
    const term = search.trim().toLowerCase();
    return modules
      .filter((module) => {
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
      })
      .sort((a, b) => a.name.localeCompare(b.name));
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
        // @ts-expect-error status is attached
        if (error?.status === 401) {
          signOut?.();
        }
        throw error;
      }
    },
    onSuccess: (updated) => {
      queryClient.setQueryData(modulesQueryKey, (prev = []) =>
        prev.map((item) => (item.id === updated.id ? { ...item, ...updated } : item))
      );
      setActionError("");
    },
    onError: (err) => {
      setActionError(err?.message || "Failed to update module state.");
    },
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
        body: JSON.stringify({ parameters }),
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
      const timestamp = response?.recorded_at ? new Date(response.recorded_at).toLocaleString() : new Date().toLocaleString();
      const status = response?.status ? String(response.status).toUpperCase() : "UNKNOWN";
      setRunError("");
      setRunMessage(`Run recorded with status ${status} at ${timestamp}.`);
    },
    onError: (err) => {
      setRunMessage("");
      setRunError(err?.message || "Module execution failed.");
    },
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

  return (
    <div className="bg-neutral p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Module Catalog</h1>
        <p className="mt-2 text-sm text-gray-600">
          Browse, execute, and schedule Tenantra scanning modules. Filters honour tenant subscriptions and your assigned role.
        </p>
      </header>

      {errorMessage && <div className="mb-4 rounded-md bg-red-100 p-4 text-red-700">{errorMessage}</div>}

      <div className="mb-6 flex flex-wrap items-center gap-4">
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search modules..."
          className="w-full max-w-xs rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
        />
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
        >
          <option value="">All categories</option>
          {categories.map((category) => (
            <option key={category} value={category}>
              {category}
            </option>
          ))}
        </select>
        <select
          value={phaseFilter}
          onChange={(e) => setPhaseFilter(e.target.value)}
          className="rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
        >
          <option value="">Any phase</option>
          {phases.map((phase) => (
            <option key={phase} value={String(phase)}>
              Phase {phase}
            </option>
          ))}
        </select>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
        >
          <option value="all">All states</option>
          <option value="enabled">Enabled</option>
          <option value="disabled">Disabled</option>
        </select>
        <Button onClick={handleReload} disabled={loading}>
          {loading ? "Refreshing..." : "Reload"}
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
        <div className="md:col-span-1">
          <Card>
            <ModuleList modules={filteredModules} selectedId={selectedId} onSelect={setSelectedId} />
          </Card>
        </div>
        <div className="md:col-span-2">
          <Card>
            <ModuleDetails module={selectedModule} onToggleEnabled={handleToggleEnabled} />
          </Card>
          {selectedModule && (
            <div className="mt-8 space-y-8">
              <Card>
                <RunModule
                  module={selectedModule}
                  onRun={handleRunModule}
                  runError={runError}
                  runMessage={runMessage}
                  runBusy={runBusy}
                />
              </Card>
              <Card>
                <ScheduleModule module={selectedModule} isAdmin={isAdmin} token={token} />
              </Card>
              <Card>
                <ModuleRuns module={selectedModule} token={token} />
              </Card>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
