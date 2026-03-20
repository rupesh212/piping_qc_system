import { useEffect, useState } from "react";
import DataTable from "../components/DataTable";
import FileUpload from "../components/FileUpload";
import Navbar from "../components/Navbar";
import StatusBadge from "../components/StatusBadge";
import api from "../services/api";

export default function ISOUpload() {
  const [isos, setIsos] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [projectName, setProjectName] = useState("");
  const [validating, setValidating] = useState({});
  const [validationResults, setValidationResults] = useState({});

  const fetchIsos = () => {
    api.get("/iso/").then((res) => {
      setIsos(res.data.items);
      setTotal(res.data.total);
    });
  };

  useEffect(() => { fetchIsos(); }, []);

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
      fetchIsos();
    } catch (err) {
      setUploadError(err.response?.data?.detail || "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  const handleValidate = async (isoId) => {
    setValidating((v) => ({ ...v, [isoId]: true }));
    try {
      const res = await api.post(`/iso/${isoId}/validate`);
      setValidationResults((r) => ({ ...r, [isoId]: res.data }));
      fetchIsos();
    } catch (err) {
      alert(err.response?.data?.detail || "Validation failed");
    } finally {
      setValidating((v) => ({ ...v, [isoId]: false }));
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
            {validating[id] ? "..." : "Validate"}
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
                  ISO {isoId.slice(0, 8)}… — Passed: {res.passed} | Failed: {res.failed} | Warnings: {res.warnings}
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
          <h2 className="font-semibold text-gray-700 mb-2">
            All ISO Drawings <span className="text-gray-400 text-sm">({total})</span>
          </h2>
          <DataTable columns={columns} data={isos} />
        </div>
      </main>
    </div>
  );
}
