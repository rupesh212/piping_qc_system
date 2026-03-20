import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import Navbar from "../components/Navbar";
import StatusBadge from "../components/StatusBadge";
import api from "../services/api";

function StatCard({ label, value, color }) {
  return (
    <div className={`bg-white rounded-xl shadow p-5 border-l-4 ${color}`}>
      <p className="text-gray-500 text-sm">{label}</p>
      <p className="text-3xl font-bold mt-1">{value}</p>
    </div>
  );
}

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [errors, setErrors] = useState([]);
  const [lineStatus, setLineStatus] = useState([]);
  const [loading, setLoading] = useState(true);

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
      .finally(() => setLoading(false));
  }, []);

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
          <p className="text-gray-500">Loading...</p>
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
            <div className="bg-white rounded-xl shadow p-5">
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
                          <td className="py-2 pr-4"><StatusBadge status={r.iso_status} /></td>
                          <td className="py-2 pr-4"><StatusBadge status={r.validation_status} /></td>
                          <td className="py-2 text-red-600 font-semibold">{r.error_count}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </>
        )}
      </main>
    </div>
  );
}
