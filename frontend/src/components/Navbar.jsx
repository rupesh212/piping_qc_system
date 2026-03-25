import { NavLink } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

const linkClass = ({ isActive }) =>
  `px-3 py-1 rounded transition-colors text-sm ${
    isActive ? "bg-brand-600 text-white font-semibold" : "hover:bg-brand-700 text-blue-100"
  }`;

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav className="bg-brand-900 text-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <span className="font-bold text-lg tracking-wide">&#9881; Piping QA/QC</span>
          <div className="flex gap-1 text-sm">
            <NavLink to="/" end className={linkClass}>
              Dashboard
            </NavLink>
            <NavLink to="/iso" className={linkClass}>
              ISO Upload
            </NavLink>
            <NavLink to="/linelist" className={linkClass}>
              Line List
            </NavLink>
            <NavLink to="/pms" className={linkClass}>
              PMS
            </NavLink>
            {user?.role === "admin" && (
              <NavLink to="/users" className={linkClass}>
                Users
              </NavLink>
            )}
          </div>
        </div>
        <div className="flex items-center gap-3 text-sm">
          <NavLink to="/settings" className={linkClass}>
            Settings
          </NavLink>
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
