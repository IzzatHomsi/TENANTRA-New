import React, { useEffect, useState, useCallback } from "react";
import { getApiBase } from "../utils/apiBase";
import Card from "../components/ui/Card.jsx";
import Button from "../components/ui/Button.jsx";
import Table from "../components/ui/Table.jsx";

const API_BASE = getApiBase();

const authHeaders = (token) => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${token}`,
});

const fetchScanData = async (token, endpoint, params = {}) => {
  const qs = new URLSearchParams(params);
  const url = `${API_BASE}${endpoint}?${qs.toString()}`;
  const res = await fetch(url, { headers: authHeaders(token) });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`);
  }
  return res.json();
};

export default function ScanOrchestration() {
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [jobDetails, setJobDetails] = useState(null);
  const [statusFilter, setStatusFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

  const loadJobs = useCallback(async (status) => {
    setLoading(true);
    setError("");
    try {
      const data = await fetchScanData(token, "/scan-orchestration/jobs", { status });
      setJobs(data || []);
      if (data?.length) {
        const jobId = data[0].id;
        setSelectedJob(jobId);
        loadJobDetails(jobId);
      }
    } catch (err) {
      setError(err.message || "Failed to load scan jobs");
    } finally {
      setLoading(false);
    }
  }, [token]);

  const loadJobDetails = async (jobId) => {
    if (!jobId) return;
    try {
      const detail = await fetchScanData(token, `/scan-orchestration/jobs/${jobId}`);
      setJobDetails(detail);
    } catch (err) {
      setError(err.message || "Failed to load job details");
    }
  };

  useEffect(() => {
    loadJobs(statusFilter);
  }, [loadJobs, statusFilter]);

  const handleJobSelection = (jobId) => {
    setSelectedJob(jobId);
    loadJobDetails(jobId);
  };

  const resultsColumns = [
    { key: "agent_id", label: "Agent" },
    { key: "asset_id", label: "Asset" },
    { key: "status", label: "Status", render: (v) => v?.toUpperCase() ?? v },
    { key: "details", label: "Details" },
  ];

  return (
    <div className="bg-facebook-gray p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Scan Orchestration</h1>
        <p className="mt-2 text-sm text-gray-600">
          Coordinate vulnerability and discovery scans across tenants. Monitor job status, priority, and agent assignment from a single view.
        </p>
      </header>

      <Card className="mb-8">
        <div className="flex items-center space-x-4">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-md border-gray-300 shadow-sm focus:border-facebook-blue focus:ring-facebook-blue sm:text-sm"
          >
            <option value="">All jobs</option>
            <option value="pending">Pending</option>
            <option value="running">Running</option>
            <option value="completed">Completed</option>
          </select>
          <Button onClick={() => loadJobs(statusFilter)} disabled={loading}>
            {loading ? "Refreshing..." : "Reload"}
          </Button>
        </div>
      </Card>

      {error && <div className="mb-4 rounded-md bg-red-100 p-4 text-red-700">{error}</div>}

      <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
        <div className="md:col-span-1">
          <Card>
            <div className="space-y-4">
              {jobs.length ? (
                jobs.map((job) => (
                  <button
                    key={job.id}
                    onClick={() => handleJobSelection(job.id)}
                    className={`w-full rounded-lg border p-4 text-left ${selectedJob === job.id ? "border-facebook-blue bg-blue-50" : "border-gray-200 bg-white"}`}>
                    <div className="font-semibold">{job.name}</div>
                    <div className="text-sm text-gray-500">{job.scan_type} • Priority {job.priority}</div>
                    <div className="text-xs text-gray-500">{job.status.toUpperCase()} • Created {job.created_at}</div>
                  </button>
                ))
              ) : (
                <div className="text-center text-gray-500">No scan jobs.</div>
              )}
            </div>
          </Card>
        </div>
        <div className="md:col-span-2">
          <Card>
            {!jobDetails ? (
              <div className="text-center text-gray-500">Select a job to view execution details.</div>
            ) : (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-bold">{jobDetails.job.name}</h2>
                  <p className="mt-1 text-sm text-gray-600">{jobDetails.job.description || "No description provided."}</p>
                  <div className="mt-4 text-sm text-gray-500">
                    Type: {jobDetails.job.scan_type} • Priority {jobDetails.job.priority} • Status {jobDetails.job.status.toUpperCase()}
                  </div>
                  <div className="text-xs text-gray-500">
                    Created {jobDetails.job.created_at} • Started {jobDetails.job.started_at || "-"} • Completed {jobDetails.job.completed_at || "-"}
                  </div>
                </div>
                <Table columns={resultsColumns} rows={jobDetails.results} empty="No results yet." />
                <Button onClick={() => loadJobDetails(selectedJob)} disabled={loading}>
                  Refresh Job
                </Button>
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}