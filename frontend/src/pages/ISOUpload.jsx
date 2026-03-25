import { useCallback, useEffect, useState } from "react";
import DataTable from "../components/DataTable";
import FileUpload from "../components/FileUpload";
import LoadingSpinner from "../components/LoadingSpinner";
import Navbar from "../components/Navbar";
import Pagination from "../components/Pagination";
import SearchFilter from "../components/SearchFilter";
import StatusBadge from "../components/StatusBadge";
import { useToast } from "../contexts/ToastContext";
import api from "../services/api";

const LIMIT = 20;

const STATUS_FILTER_OPTIONS = [
  { value: "pending", label: "Pending" },
  { value: "processed", label: "Processed" },
  { value: "error", label: "Error" },
];

export default function ISOUpload() {
  const { showToast } = useToast();

  const [isos, setIsos] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [tableLoading, setTableLoading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [projectName, setProjectName] = useState("");
  const [validating, setValidating] = useState({});
  const [validationResults, setValidationResults] = useState({});
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [skip, setSkip] = useState(0);
  const [exporting, setExporting] = useState(false);

  const fetchIsos = useCallback(
    (searchVal, statusVal, skipVal) => {
      setTableLoading(true);
      const params = new URLSearchParams();
      if (searchVal) params.set("search", searchVal);
      if (statusVal) params.set("status", statusVal);
      params.set("skip", String(skipVal));
      params.set("limit", String(LIMIT));

      api
        .get(`/iso/?${params.toString()}`)
        .then((res) => {
          setIsos(res.data.items);
          setTotal(res.data.total);
        })
        .catch((err) => {
          showToast(err.response?.data?.detail || "Failed to load ISO list", "error");
        })
        .finally(() => setTableLoading(false));
    },
    [showToast]
  );

  useEffect(() => {
    fetchIsos(search, statusFilter, skip);
  }, [search, statusFilter, skip, fetchIsos]);

  const handleSearch = useCallback(
    (val) => {
      setSearch(val);
      setSkip(0);
    },
    []
  );

  const handleFilter = useCallback(
    (val) => {
      setStatusFilter(val);
      setSkip(0);
    },
    []
  );

  const handlePageChange = useCallback((newSkip) => {
    setSkip(newSkip);
  }, []);

  const handleUpload = async (file) => {
    setLoading(true);
    setUploadError("");
    const form = new FormData();
    form.append("file", file);
    form.append("project_name", projectName);
    try {
      await api.post("/iso/upload", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      showToast("ISO uploaded successfully", "success");
      setSkip(0);
      fetchIsos(search, statusFilter, 0);
    } catch (err) {
      const msg = err.response?.data?.detail || "Upload failed";
      setUploadError(msg);
      showToast(msg, "error");
    } finally {
      setLoading(false);
    }
  };

  const handleValidate = async (isoId) => {
    setValidating((v) => ({ ...v, [isoId]: true }));
    try {
      const res = await api.post(`/iso/${isoId}/validate`);
      setValidationResults((r) => ({ ...r, [isoId]: res.data }));
      showToast("Validation complete", "success");
      fetchIsos(search, statusFilter, skip);
    } catch (err) {
      showToast(err.response?.data?.detail || "Validation failed", "error");
    } finally {
      setValidating((v) => ({ ...v, [isoId]: false }));
    }
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      const res = await api.get("/reports/validation-summary", {
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      const disposition = res.headers["content-disposition"];
      let filename = "validation-summary.csv";
      if (disposition) {
        const match = disposition.match(/filename="?([^"]+)"?/);
        if (match) filename = match[1];
      }
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      showToast("Export downloaded successfully", "success");
    } catch (err) {
      showToast(err.response?.data?.detail || "Export failed", "error");
    } finally {
      setExporting(false);
    }
  };

  const columns = [
    { key: "file_name", label: "File" },
    { key: "project_name", label: "Project" },
    { key: "line_number", label: "Line No." },
    { key: "pipe_size", label: "Size" },
    { key: "spec", label: "Spec" },
    { key: "weld_count", label: "Welds" },
    {
      key: "status",
      label: "Status",
      render: (val) => <StatusBadge status={val} />,
    },
    {
      key: "id",
      label: "Actions",
      render: (id, row) =>
        row.status === "processed" ? (
          <button
            onClick={() => handleValidate(id)}
            disabled={validating[id]}
            className="text-xs bg-brand-600 hover:bg-brand-700 text-white px-2 py-1 rounded disabled:opacity-50"
          >
            {validating[id] ? "…" : "Validate"}
          </button>
        ) : null,
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-gray-800 mb-6">ISO Upload</h1>

        <div className="bg-white rounded-xl shadow p-6 mb-6">
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">Project Name</label>
            <input
              type="text"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              placeholder="e.g. Plant-A Unit-2"
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-64 focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
          </div>
          <FileUpload
            onUpload={handleUpload}
            accept=".pdf,.jpg,.jpeg,.png,.tiff"
            label="Upload ISO Drawing (PDF or Image)"
            loading={loading}
          />
          {uploadError && <p className="mt-2 text-red-600 text-sm">{uploadError}</p>}
        </div>

        {/* Validation result panel */}
        {Object.keys(validationResults).length > 0 && (
          <div className="bg-white rounded-xl shadow p-6 mb-6">
            <h2 className="font-semibold text-gray-700 mb-3">Validation Results</h2>
            {Object.entries(validationResults).map(([isoId, res]) => (
              <div key={isoId} className="mb-4 border rounded-lg p-4">
                <p className="text-sm font-medium mb-2">
                  ISO {isoId.slice(0, 8)}… — Passed: {res.passed} | Failed: {res.failed} | Warnings:{" "}
                  {res.warnings}
                </p>
                <div className="space-y-1">
                  {res.results.map((r, i) => (
                    <div key={i} className="flex gap-3 text-sm">
                      <StatusBadge status={r.result === "pass" ? "pass" : r.result} />
                      <span className="font-mono text-gray-500">{r.rule_name}</span>
                      <span className="text-gray-700">{r.message}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="bg-white rounded-xl shadow p-6">
          <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
            <h2 className="font-semibold text-gray-700">
              All ISO Drawings <span className="text-gray-400 text-sm">({total})</span>
            </h2>
            <button
              onClick={handleExport}
              disabled={exporting}
              className="flex items-center gap-2 text-sm bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              {exporting ? "Exporting…" : "Export Report"}
            </button>
          </div>

          <SearchFilter
            onSearch={handleSearch}
            filterOptions={STATUS_FILTER_OPTIONS}
            onFilter={handleFilter}
            placeholder="Search by file, project, line no…"
          />

          {tableLoading ? (
            <LoadingSpinner message="Loading ISO drawings…" />
          ) : (
            <>
              <DataTable columns={columns} data={isos} />
              <Pagination total={total} skip={skip} limit={LIMIT} onPageChange={handlePageChange} />
            </>
          )}
        </div>
      </main>
    </div>
  );
}
