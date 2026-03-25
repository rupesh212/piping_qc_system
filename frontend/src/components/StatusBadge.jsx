const STATUS_STYLES = {
  pending: "bg-yellow-100 text-yellow-800",
  processed: "bg-green-100 text-green-800",
  error: "bg-red-100 text-red-800",
  valid: "bg-green-100 text-green-800",
  mismatch: "bg-red-100 text-red-800",
  pass: "bg-green-100 text-green-800",
  fail: "bg-red-100 text-red-800",
  warning: "bg-orange-100 text-orange-800",
};

export default function StatusBadge({ status }) {
  const style = STATUS_STYLES[status] || "bg-gray-100 text-gray-700";
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-semibold ${style}`}>
      {status}
    </span>
  );
}
