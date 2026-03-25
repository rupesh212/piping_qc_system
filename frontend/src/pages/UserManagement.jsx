import { useCallback, useEffect, useState } from "react";
import DataTable from "../components/DataTable";
import LoadingSpinner from "../components/LoadingSpinner";
import Navbar from "../components/Navbar";
import Pagination from "../components/Pagination";
import { useAuth } from "../contexts/AuthContext";
import { useToast } from "../contexts/ToastContext";
import api from "../services/api";

const LIMIT = 20;

const ROLE_OPTIONS = ["admin", "qa", "site"];

function RoleSelect({ userId, currentRole, onRoleChange }) {
  const [role, setRole] = useState(currentRole);
  const [saving, setSaving] = useState(false);
  const { showToast } = useToast();

  const handleChange = async (e) => {
    const newRole = e.target.value;
    setSaving(true);
    try {
      await api.patch(`/users/${userId}`, { role: newRole });
      setRole(newRole);
      onRoleChange(userId, newRole);
      showToast(`Role updated to "${newRole}"`, "success");
    } catch (err) {
      showToast(err.response?.data?.detail || "Failed to update role", "error");
    } finally {
      setSaving(false);
    }
  };

  return (
    <select
      value={role}
      onChange={handleChange}
      disabled={saving}
      className="text-sm border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-brand-500 bg-white disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {ROLE_OPTIONS.map((r) => (
        <option key={r} value={r}>
          {r}
        </option>
      ))}
    </select>
  );
}

function ActiveToggle({ userId, isActive, isCurrentUser, onToggle }) {
  const [active, setActive] = useState(isActive);
  const [saving, setSaving] = useState(false);
  const { showToast } = useToast();

  const handleToggle = async () => {
    if (isCurrentUser) return;
    setSaving(true);
    const newActive = !active;
    try {
      await api.patch(`/users/${userId}`, { is_active: newActive });
      setActive(newActive);
      onToggle(userId, newActive);
      showToast(
        newActive ? "User activated successfully" : "User deactivated successfully",
        "success"
      );
    } catch (err) {
      showToast(err.response?.data?.detail || "Failed to update user status", "error");
    } finally {
      setSaving(false);
    }
  };

  if (isCurrentUser) {
    return (
      <button
        disabled
        className="text-xs px-3 py-1 rounded-full bg-gray-100 text-gray-400 cursor-not-allowed border border-gray-200"
        title="Cannot deactivate your own account"
      >
        {active ? "Active" : "Inactive"}
      </button>
    );
  }

  return (
    <button
      onClick={handleToggle}
      disabled={saving}
      className={`text-xs px-3 py-1 rounded-full border transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
        active
          ? "bg-green-100 text-green-700 border-green-300 hover:bg-green-200"
          : "bg-red-100 text-red-700 border-red-300 hover:bg-red-200"
      }`}
    >
      {saving ? "…" : active ? "Active" : "Inactive"}
    </button>
  );
}

export default function UserManagement() {
  const { user: currentUser } = useAuth();
  const { showToast } = useToast();

  const [users, setUsers] = useState([]);
  const [total, setTotal] = useState(0);
  const [skip, setSkip] = useState(0);
  const [loading, setLoading] = useState(false);

  const fetchUsers = useCallback(
    (skipVal) => {
      setLoading(true);
      const params = new URLSearchParams();
      params.set("skip", String(skipVal));
      params.set("limit", String(LIMIT));

      api
        .get(`/users/?${params.toString()}`)
        .then((res) => {
          if (Array.isArray(res.data)) {
            setUsers(res.data);
            setTotal(res.data.length);
          } else {
            setUsers(res.data.items ?? res.data);
            setTotal(res.data.total ?? res.data.length);
          }
        })
        .catch((err) => {
          showToast(err.response?.data?.detail || "Failed to load users", "error");
        })
        .finally(() => setLoading(false));
    },
    [showToast]
  );

  useEffect(() => {
    fetchUsers(skip);
  }, [skip, fetchUsers]);

  const handlePageChange = useCallback((newSkip) => {
    setSkip(newSkip);
  }, []);

  const handleRoleChange = useCallback((userId, newRole) => {
    setUsers((prev) =>
      prev.map((u) => (u.id === userId ? { ...u, role: newRole } : u))
    );
  }, []);

  const handleActiveToggle = useCallback((userId, newActive) => {
    setUsers((prev) =>
      prev.map((u) => (u.id === userId ? { ...u, is_active: newActive } : u))
    );
  }, []);

  const columns = [
    { key: "username", label: "Username" },
    { key: "email", label: "Email" },
    {
      key: "role",
      label: "Role",
      render: (val, row) => (
        <RoleSelect
          userId={row.id}
          currentRole={val}
          onRoleChange={handleRoleChange}
        />
      ),
    },
    {
      key: "is_active",
      label: "Status",
      render: (val, row) => (
        <ActiveToggle
          userId={row.id}
          isActive={val}
          isCurrentUser={row.id === currentUser?.id}
          onToggle={handleActiveToggle}
        />
      ),
    },
    {
      key: "created_at",
      label: "Created",
      render: (val) =>
        val
          ? new Date(val).toLocaleDateString("en-GB", {
              day: "2-digit",
              month: "short",
              year: "numeric",
            })
          : "—",
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-gray-800 mb-6">User Management</h1>

        <div className="bg-white rounded-xl shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-gray-700">
              All Users{" "}
              <span className="text-gray-400 text-sm">({total})</span>
            </h2>
          </div>

          {loading ? (
            <LoadingSpinner message="Loading users…" />
          ) : (
            <>
              <DataTable columns={columns} data={users} />
              <Pagination
                total={total}
                skip={skip}
                limit={LIMIT}
                onPageChange={handlePageChange}
              />
            </>
          )}
        </div>
      </main>
    </div>
  );
}
