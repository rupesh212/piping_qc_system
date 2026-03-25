import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center px-4">
      <p className="text-9xl font-extrabold text-gray-200 select-none">404</p>
      <h1 className="text-2xl font-bold text-gray-700 mt-4 mb-2">Page Not Found</h1>
      <p className="text-gray-500 text-sm mb-8 text-center">
        The page you are looking for does not exist or has been moved.
      </p>
      <Link
        to="/"
        className="bg-brand-600 hover:bg-brand-700 text-white text-sm font-medium px-6 py-2.5 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-brand-500"
      >
        Back to Dashboard
      </Link>
    </div>
  );
}
