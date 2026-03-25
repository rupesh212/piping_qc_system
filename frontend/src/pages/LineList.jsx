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

const LIMIT = 50;

const STATUS_FILTER_OPTIONS = [
  { value: "valid", label: "Valid" },
  { value: "mismatch", label: "Mismatch" },
  { value: "pending", label: "Pending" },
];

export default function LineList() {
  const { showToast } = useToast();

  const [batches, setBatches] = useState([]);
  const [selectedBatch, setSelectedBatch] = useState(null);
  const [entries, setEntries] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [tableLoading, setTableLoading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [skip, setSkip] = useState(0);

  const fetchBatches = useCallback(() => {
    api
      .get("/linelist/")
      .then((res) => setBatches(res.data))
      .catch((err) => {
        showToast(err.response?.data?.detail || "Failed to load batches", "error");
      });
  }, [showToast]);

  useEffect(() => {
    fetchBatches();
  }, [fetchBatches]);

  const fetchEntries = useCallback(
    (batchId, searchVal, statusVal, skipVal) => {
      if (!batchId) return;
      setTableLoading(true);
      const params = new URLSearchParams();
      if (searchVal) params.set("search", searchVal);
      if (statusVal) params.set("status", statusVal);
      params.set("skip", String(skipVal));
      params.set("limit", String(LIMIT));

      api
        .get(`/linelist/${batchId}?${params.toString()}`)
        .then((res) => {
          setEntries(res.data.items);
          setTotal(res.data.total ?? res.data.items.length);
        })
        .catch((err) => {
          showToast(err.response?.data?.detail || "Failed to load entries", "error");
        })
        .finally(() => setTableLoading(false));
    },
    [showToast]
  );

  const loadBatch = useCallback(
    (batchId) => {
      setSelectedBatch(batchId);
      setSearch("");
      setStatusFilter("");
      setSkip(0);
      fetchEntries(batchId, "", "", 0);
    },
    [fetchEntries]
  );

  useEffect(() => {
    if (selectedBatch) {
      fetchEntries(selectedBatch, search, statusFilter, skip);
    }
  }, [search, statusFilter, skip, selectedBatch, fetchEntries]);

  const handleSearch = useCallback((val) => {
    setSearch(val);
    setSkip(0);
  }, []);

  const handleFilter = useCallback((val) => {
    setStatusFilter(val);
    setSkip(0);
  }, []);

  const handlePageChange = useCallback((newSkip) => {
    setSkip(newSkip);
  }, []);

  const handleUpload = async (file) => {
    setLoading(true);
    setUploadError("");
    const form = new FormData();
    form.append("file", file);
    try {
      const res = await api.post("/linelist/upload", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      showToast("Line list uploaded successfully", "success");
      fetchBatches();
      loadBatch(res.data.batch_id);
    } catch (err) {
      const msg = err.response?.data?.detail || "Upload failed";
      setUploadError(msg);
      showToast(msg, "error");
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { key: "line_number", label: "Line Number" },
    { key: "pipe_size", label: "Size" },
    { key: "spec", label: "Spec" },
    { key: "from_equipment", label: "From" },
    { key: "to_equipment", label: "To" },
    { key: "fluid", label: "Fluid" },
    {
      key: "validation_status",
      label: "Status",
      render: (val) => <StatusBadge status={val} />,
    },
    {
      key: "mismatch_fields",
      label: "Mismatches",
      render: (val) =>
        val && val.length > 0 ? (
          <span className="text-red-600 text-xs">{val.join(", ")}</span>
        ) : null,
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-gray-800 mb-6">Line List</h1>

        <div className="bg-white rounded-xl shadow p-6 mb-6">
          <FileUpload
            onUpload={handleUpload}
            accept=".xlsx,.xls"
            label="Upload Line List Excel (.xlsx)"
            loading={loading}
          />
          {uploadError && <p className="mt-2 text-red-600 text-sm">{uploadError}</p>}
        </div>

        {batches.length > 0 && (
          <div className="bg-white rounded-xl shadow p-6 mb-4">
            <h2 className="font-semibold text-gray-700 mb-3">Upload Batches</h2>
            <div className="flex flex-wrap gap-2">
              {batches.map((b) => (
                <button
                  key={b.batch_id}
                  onClick={() => loadBatch(b.batch_id)}
                  className={`text-xs px-3 py-1.5 rounded-full border transition-colors ${
                    selectedBatch === b.batch_id
                      ? "bg-brand-600 text-white border-brand-600"
                      : "border-gray-300 hover:border-brand-500 text-gray-700"
                  }`}
                >
                  {b.batch_id.slice(0, 8)}…
                </button>
              ))}
            </div>
          </div>
        )}

        {selectedBatch && (
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="font-semibold text-gray-700 mb-4">
              Entries — Batch{" "}
              <span className="font-mono text-sm">{selectedBatch.slice(0, 8)}…</span>
              <span className="text-gray-400 text-sm ml-2">({total})</span>
            </h2>

            <SearchFilter
              onSearch={handleSearch}
              filterOptions={STATUS_FILTER_OPTIONS}
              onFilter={handleFilter}
              placeholder="Search by line number, spec…"
            />

            {tableLoading ? (
              <LoadingSpinner message="Loading entries…" />
            ) : (
              <>
                <DataTable columns={columns} data={entries} />
                <Pagination
                  total={total}
                  skip={skip}
                  limit={LIMIT}
                  onPageChange={handlePageChange}
                />
              </>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
