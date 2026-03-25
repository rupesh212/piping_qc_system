export default function LoadingSpinner({ message = "Loading…" }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-3">
      <div
        className="w-10 h-10 rounded-full border-4 border-gray-200 border-t-brand-600 animate-spin"
        role="status"
        aria-label="Loading"
      />
      {message && <p className="text-gray-500 text-sm">{message}</p>}
    </div>
  );
}
