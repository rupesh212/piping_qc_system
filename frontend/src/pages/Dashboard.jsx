import { useCallback, useEffect, useState } from "react";
import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import LoadingSpinner from "../components/LoadingSpinner";
import Navbar from "../components/Navbar";
import StatusBadge from "../components/StatusBadge";
import { useToast } from "../contexts/ToastContext";
import api from "../services/api";

function StatCard({ label, value, color }) {
  return (
    <div className={`bg-white rounded-xl shadow p-5 border-l-4 ${color}`}>
      <p className="text-gray-500 text-sm">{label}</p>
      <p className="text-3xl font-bold mt-1">{value}</p>
    </div>
  );
}

function RiskBadge({ score }) {
  let colorClass;
  let label;
  if (score <= 33) {
    colorClass = "bg-green-100 text-green-800 border-green-300";
    label = "Low";
  } else if (score <= 66) {
    colorClass = "bg-yellow-100 text-yellow-800 border-yellow-300";
    label = "Medium";
  } else {
    colorClass = "bg-red-100 text-red-800 border-red-300";
    label = "High";
  }
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-semibold border ${colorClass}`}
    >
      Risk Score: {score} — {label}
    </span>
  );
}

const SEVERITY_COLORS = {
  critical: "bg-red-100 text-red-800",
  high: "bg-orange-100 text-orange-800",
  medium: "bg-yellow-100 text-yellow-800",
  low: "bg-blue-100 text-blue-800",
};

function SeverityBadge({ severity }) {
  const colorClass = SEVERITY_COLORS[severity?.toLowerCase()] || "bg-gray-100 text-gray-700";
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-semibold ${colorClass}`}>
      {severity}
    </span>
  );
}

export default function Dashboard() {
  const { showToast } = useToast();

  const [summary, setSummary] = useState(null);
  const [errors, setErrors] = useState([]);
  const [lineStatus, setLineStatus] = useState([]);
  const [loading, setLoading] = useState(true);

  const [anomalyReport, setAnomalyReport] = useState(null);
  const [anomalyLoading, setAnomalyLoading] = useState(false);

  useEffect(() => {
    Promise.all([
      api.get("/dashboard/summary"),
      api.get("/dashboard/errors"),
      api.get("/dashboard/line-status"),
    ])
      .then(([s, e, l]) => {
        setSummary(s.data);
        setErrors(e.data);
        setLineStatus(l.data);
      })
      .catch((err) => {
        showToast(err.response?.data?.detail || "Failed to load dashboard data", "error");
      })
      .finally(() => setLoading(false));
  }, [showToast]);

  const fetchAnomalyReport = useCallback(() => {
    setAnomalyLoading(true);
    api
      .get("/dashboard/anomaly-report")
      .then((res) => {
        setAnomalyReport(res.data);
      })
      .catch((err) => {
        showToast(err.response?.data?.detail || "Failed to load anomaly report", "error");
      })
      .finally(() => setAnomalyLoading(false));
  }, [showToast]);

  const chartData = summary
    ? [
        { name: "Pass", count: summary.total_validations - summary.total_errors, fill: "#22c55e" },
        { name: "Fail", count: summary.total_errors, fill: "#ef4444" },
      ]
    : [];

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-gray-800 mb-6">Dashboard</h1>

        {loading ? (
          <LoadingSpinner message="Loading dashboard…" />
        ) : (
          <>
            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <StatCard label="Total ISOs" value={summary?.total_isos ?? 0} color="border-blue-500" />
              <StatCard label="Line List Entries" value={summary?.total_lines ?? 0} color="border-purple-500" />
              <StatCard label="Validations Run" value={summary?.total_validations ?? 0} color="border-green-500" />
              <StatCard label="Errors Found" value={summary?.total_errors ?? 0} color="border-red-500" />
            </div>

            {/* Pass Rate + Chart */}
            <div className="grid md:grid-cols-2 gap-6 mb-8">
              <div className="bg-white rounded-xl shadow p-5">
                <h2 className="font-semibold text-gray-700 mb-4">Validation Results</h2>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={chartData}>
                    <XAxis dataKey="name" />
                    <YAxis allowDecimals={false} />
                    <Tooltip />
                    <Bar dataKey="count">
                      {chartData.map((entry, i) => (
                        <Cell key={i} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="bg-white rounded-xl shadow p-5 flex flex-col items-center justify-center">
                <p className="text-gray-500 text-sm mb-2">Overall Pass Rate</p>
                <p className="text-6xl font-bold text-green-600">{summary?.pass_rate ?? 0}%</p>
              </div>
            </div>

            {/* Recent Errors */}
            <div className="bg-white rounded-xl shadow p-5 mb-8">
              <h2 className="font-semibold text-gray-700 mb-3">Recent Errors</h2>
              {errors.length === 0 ? (
                <p className="text-gray-400 text-sm">No errors found.</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full text-sm">
                    <thead>
                      <tr className="text-left text-gray-500 border-b">
                        <th className="py-2 pr-4">Line No</th>
                        <th className="py-2 pr-4">Rule</th>
                        <th className="py-2">Message</th>
                      </tr>
                    </thead>
                    <tbody>
                      {errors.map((e) => (
                        <tr key={e.id} className="border-b last:border-0">
                          <td className="py-2 pr-4 font-mono text-xs">{e.line_number || "—"}</td>
                          <td className="py-2 pr-4 text-red-600 font-medium">{e.rule_name}</td>
                          <td className="py-2 text-gray-600">{e.message}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {/* Line Status */}
            <div className="bg-white rounded-xl shadow p-5 mb-8">
              <h2 className="font-semibold text-gray-700 mb-3">Line Status</h2>
              {lineStatus.length === 0 ? (
                <p className="text-gray-400 text-sm">No ISOs uploaded yet.</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full text-sm">
                    <thead>
                      <tr className="text-left text-gray-500 border-b">
                        <th className="py-2 pr-4">Line Number</th>
                        <th className="py-2 pr-4">ISO Status</th>
                        <th className="py-2 pr-4">Validation</th>
                        <th className="py-2">Errors</th>
                      </tr>
                    </thead>
                    <tbody>
                      {lineStatus.map((r, i) => (
                        <tr key={i} className="border-b last:border-0">
                          <td className="py-2 pr-4 font-mono text-xs">{r.line_number || "—"}</td>
                          <td className="py-2 pr-4">
                            <StatusBadge status={r.iso_status} />
                          </td>
                          <td className="py-2 pr-4">
                            <StatusBadge status={r.validation_status} />
                          </td>
                          <td className="py-2 text-red-600 font-semibold">{r.error_count}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {/* AI Anomaly Report */}
            <div className="bg-white rounded-xl shadow p-5">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-semibold text-gray-700">AI Anomaly Report</h2>
                <button
                  onClick={fetchAnomalyReport}
                  disabled={anomalyLoading}
                  className="flex items-center gap-2 text-sm bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg transition-colors"
                >
                  <svg
                    className={`w-4 h-4 ${anomalyLoading ? "animate-spin" : ""}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                    />
                  </svg>
                  {anomalyLoading ? "Analyzing…" : "Refresh Report"}
                </button>
              </div>

              {anomalyLoading ? (
                <LoadingSpinner message="Running AI analysis…" />
              ) : anomalyReport ? (
                <div>
                  {/* Risk Score */}
                  <div className="mb-4">
                    <RiskBadge score={anomalyReport.risk_score ?? 0} />
                  </div>

                  {/* Recommendation */}
                  {anomalyReport.recommendation && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                      <p className="text-sm font-medium text-blue-800 mb-1">Recommendation</p>
                      <p className="text-sm text-blue-700">{anomalyReport.recommendation}</p>
                    </div>
                  )}

                  {/* Anomaly list */}
                  {anomalyReport.anomalies && anomalyReport.anomalies.length > 0 ? (
                    <div className="space-y-3">
                      <p className="text-sm font-medium text-gray-600">
                        {anomalyReport.anomalies.length} anomal
                        {anomalyReport.anomalies.length === 1 ? "y" : "ies"} detected
                      </p>
                      {anomalyReport.anomalies.map((anomaly, i) => (
                        <div
                          key={i}
                          className="border border-gray-200 rounded-lg p-4 flex flex-col gap-2"
                        >
                          <div className="flex items-center gap-3">
                            <span className="text-sm font-semibold text-gray-700">
                              {anomaly.type || "Unknown Type"}
                            </span>
                            <SeverityBadge severity={anomaly.severity} />
                          </div>
                          <p className="text-sm text-gray-600">{anomaly.message}</p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-400 text-sm">No anomalies detected.</p>
                  )}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-12 text-center">
                  <svg
                    className="w-12 h-12 text-gray-300 mb-3"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1.5}
                      d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                    />
                  </svg>
                  <p className="text-gray-400 text-sm">
                    Click "Refresh Report" to run AI anomaly analysis on your piping data.
                  </p>
                </div>
              )}
            </div>
          </>
        )}
      </main>
    </div>
  );
}
