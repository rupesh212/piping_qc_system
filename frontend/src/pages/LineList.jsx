import { useEffect, useState } from "react";
import DataTable from "../components/DataTable";
import FileUpload from "../components/FileUpload";
import Navbar from "../components/Navbar";
import StatusBadge from "../components/StatusBadge";
import api from "../services/api";

export default function LineList() {
  const [batches, setBatches] = useState([]);
  const [selectedBatch, setSelectedBatch] = useState(null);
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploadError, setUploadError] = useState("");

  const fetchBatches = () => {
    api.get("/linelist/").then((res) => setBatches(res.data));
  };

  useEffect(() => { fetchBatches(); }, []);

  const loadBatch = (batchId) => {
    setSelectedBatch(batchId);
    api.get(`/linelist/${batchId}`).then((res) => setEntries(res.data.items));
  };

  const handleUpload = async (file) => {
    setLoading(true);
    setUploadError("");
    const form = new FormData();
    form.append("file", file);
    try {
      const res = await api.post("/linelist/upload", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      fetchBatches();
      loadBatch(res.data.batch_id);
    } catch (err) {
      setUploadError(err.response?.data?.detail || "Upload failed");
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
            <h2 className="font-semibold text-gray-700 mb-2">
              Entries — Batch <span className="font-mono text-sm">{selectedBatch.slice(0, 8)}…</span>
            </h2>
            <DataTable columns={columns} data={entries} />
          </div>
        )}
      </main>
    </div>
  );
}
