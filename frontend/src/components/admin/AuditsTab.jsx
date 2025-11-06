import React, { useCallback, useEffect, useMemo, useState, memo } from "react";
import CollapsibleSection from "./CollapsibleSection.jsx";
import Button from "../ui/Button.jsx";
import { fetchAuditLogs } from "../../api/auditLogs.ts";

function AuditsTab({ headers }) {
  const [items, setItems] = useState([]);
  const [q, setQ] = useState("");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  const [total, setTotal] = useState(0);
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const totalPages = useMemo(() => Math.max(1, Math.ceil(total / pageSize)), [total, pageSize]);

  const refresh = useCallback(async () => {
    const params = new URLSearchParams();
    if (dateFrom) params.set("start_date", dateFrom);
    if (dateTo) params.set("end_date", dateTo);
    if (result) params.set("result", result);
    params.set("page", String(page));
    params.set("page_size", String(pageSize));

    setLoading(true);
    setError("");
    try {
      const payload = await fetchAuditLogs(headers, {
        start_date: dateFrom || undefined,
        end_date: dateTo || undefined,
        result: result || undefined,
        q: q || undefined,
        page,
        page_size: pageSize,
      });
      setItems(payload.items || []);
      setTotal(payload.total || 0);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Network error";
      setError(`Unable to reach audit API • ${message}`);
      setItems([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [headers, dateFrom, dateTo, result, page, pageSize]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const filtered = useMemo(
    () => items.filter((it) => !q || JSON.stringify(it).toLowerCase().includes(q.toLowerCase())),
    [items, q]
  );

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <h3 className="text-lg font-semibold text-primary-text">Audit logs</h3>
        <Button onClick={refresh} disabled={loading} className="w-full sm:w-auto">
          {loading ? "Refreshing..." : "Apply filters"}
        </Button>
      </div>

      <CollapsibleSection
        id="audit-filters"
        title="Filters"
        helper="Narrow results by window, result, or keyword before exporting."
      >
        <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
          <div>
            <label className="text-sm font-medium text-primary-text" htmlFor="audit-search">
              Search
            </label>
            <p className="text-xs text-secondary-text">Matches event payload, actor, and metadata.</p>
            <input
              id="audit-search"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              className="mt-2 block w-full rounded-lg border border-border-color px-3 py-2 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40"
              placeholder="Find events..."
            />
          </div>
          <div>
            <label className="text-sm font-medium text-primary-text" htmlFor="audit-start">
              Start date
            </label>
            <p className="text-xs text-secondary-text">UTC date; leave blank for oldest data.</p>
            <input
              id="audit-start"
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              className="mt-2 block w-full rounded-lg border border-border-color px-3 py-2 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40"
            />
          </div>
          <div>
            <label className="text-sm font-medium text-primary-text" htmlFor="audit-end">
              End date
            </label>
            <p className="text-xs text-secondary-text">Inclusive. Combine with start date for bounded range.</p>
            <input
              id="audit-end"
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              className="mt-2 block w-full rounded-lg border border-border-color px-3 py-2 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40"
            />
          </div>
          <div>
            <label className="text-sm font-medium text-primary-text" htmlFor="audit-result">
              Result
            </label>
            <p className="text-xs text-secondary-text">Surface failures quickly when triaging incidents.</p>
            <select
              id="audit-result"
              value={result}
              onChange={(e) => setResult(e.target.value)}
              className="mt-2 block w-full rounded-lg border border-border-color px-3 py-2 shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40"
            >
              <option value="">Any</option>
              <option value="success">Success</option>
              <option value="failure">Failure</option>
              <option value="denied">Denied</option>
            </select>
          </div>
        </div>
      </CollapsibleSection>

      {error && (
        <div className="rounded-lg border border-amber-300 bg-amber-50 p-4 text-sm text-amber-700">
          {error}
        </div>
      )}

      {!error && (
        <div className="overflow-hidden rounded-lg border border-border-color shadow">
          <table className="min-w-full divide-y divide-border-color">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-secondary-text">Time</th>
                <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-secondary-text">User</th>
                <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-secondary-text">Action</th>
                <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wide text-secondary-text">Result</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border-color bg-surface">
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-6 py-6 text-center text-sm text-secondary-text">
                    {loading ? "Loading audit activity…" : "No audit entries match your filters yet."}
                  </td>
                </tr>
              ) : (
                filtered.map((row, index) => (
                  <tr key={index} className="hover:bg-gray-50/60">
                    <td className="whitespace-nowrap px-6 py-3 text-sm text-primary-text">
                      {row.timestamp || row.created_at || ""}
                    </td>
                    <td className="whitespace-nowrap px-6 py-3 text-sm text-primary-text">{row.user_id || "—"}</td>
                    <td className="whitespace-nowrap px-6 py-3 text-sm text-primary-text">{row.action || ""}</td>
                    <td className="whitespace-nowrap px-6 py-3 text-sm text-primary-text capitalize">{row.result || ""}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="text-sm text-secondary-text">Total events: {total}</div>
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
          <div className="flex items-center justify-between gap-2">
            <Button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page <= 1 || loading} variant="ghost">
              Prev
            </Button>
            <div className="text-sm text-primary-text">
              Page {page} / {totalPages}
            </div>
            <Button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages || loading}
              variant="ghost"
            >
              Next
            </Button>
          </div>
          <select
            value={pageSize}
            onChange={(e) => {
              setPageSize(Number(e.target.value) || 50);
              setPage(1);
            }}
            className="rounded-lg border border-border-color px-3 py-2 text-sm text-primary-text focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/40"
          >
            {[25, 50, 100, 200, 500].map((n) => (
              <option key={n} value={n}>
                {n} / page
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}

export default memo(AuditsTab);
