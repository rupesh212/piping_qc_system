export default function DataTable({ columns, data }) {
  if (!data || data.length === 0) {
    return <p className="text-gray-500 text-sm mt-4">No data available.</p>;
  }

  return (
    <div className="overflow-x-auto mt-4">
      <table className="min-w-full border border-gray-200 rounded-lg overflow-hidden text-sm">
        <thead className="bg-brand-900 text-white">
          <tr>
            {columns.map((col) => (
              <th key={col.key} className="px-4 py-2 text-left font-semibold">
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr
              key={row.id || i}
              className={i % 2 === 0 ? "bg-white" : "bg-gray-50"}
            >
              {columns.map((col) => (
                <td key={col.key} className="px-4 py-2 border-t border-gray-100">
                  {col.render ? col.render(row[col.key], row) : (row[col.key] ?? "—")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
