import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

const BASE_NAV_LINKS = [
  { to: "/", label: "Dashboard" },
  { to: "/iso", label: "ISO Upload" },
  { to: "/linelist", label: "Line List" },
  { to: "/pms", label: "PMS" },
];

export default function Navbar() {
  const { user, logout } = useAuth();
  const location = useLocation();

  const navLinks = [
    ...BASE_NAV_LINKS,
    ...(user?.role === "admin" ? [{ to: "/users", label: "Users" }] : []),
    { to: "/settings", label: "Settings" },
  ];

  return (
    <nav className="bg-brand-900 text-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <span className="font-bold text-lg tracking-wide">&#9881; Piping QA/QC</span>
          <div className="flex gap-1 text-sm">
            {navLinks.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className={`px-3 py-1 rounded transition-colors ${
                  location.pathname === link.to
                    ? "bg-brand-600 text-white font-semibold"
                    : "hover:bg-brand-700 text-blue-100"
                }`}
              >
                {link.label}
              </Link>
            ))}
          </div>
        </div>
        <div className="flex items-center gap-3 text-sm">
          <span className="text-blue-200">
            {user?.username}{" "}
            <span className="text-blue-400 text-xs uppercase tracking-wide">
              ({user?.role})
            </span>
          </span>
          <button
            onClick={logout}
            className="bg-red-600 hover:bg-red-700 px-3 py-1 rounded text-white transition-colors"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}
