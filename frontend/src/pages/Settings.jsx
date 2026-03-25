import { useState } from "react";
import Navbar from "../components/Navbar";
import { useAuth } from "../contexts/AuthContext";
import { useToast } from "../contexts/ToastContext";
import api from "../services/api";

export default function Settings() {
  const { user } = useAuth();
  const { showToast } = useToast();

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState({});

  const validate = () => {
    const errs = {};
    if (!currentPassword) errs.currentPassword = "Current password is required.";
    if (!newPassword) {
      errs.newPassword = "New password is required.";
    } else if (newPassword.length < 8) {
      errs.newPassword = "New password must be at least 8 characters.";
    }
    if (!confirmPassword) {
      errs.confirmPassword = "Please confirm your new password.";
    } else if (newPassword !== confirmPassword) {
      errs.confirmPassword = "Passwords do not match.";
    }
    return errs;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const validationErrors = validate();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }
    setErrors({});
    setSaving(true);
    try {
      await api.post("/auth/change-password", {
        current_password: currentPassword,
        new_password: newPassword,
      });
      showToast("Password changed successfully", "success");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err) {
      showToast(err.response?.data?.detail || "Failed to change password", "error");
    } finally {
      setSaving(false);
    }
  };

  const ROLE_LABELS = {
    admin: "Administrator",
    qa: "QA Engineer",
    site: "Site Inspector",
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-3xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-gray-800 mb-6">Settings</h1>

        {/* Account Info */}
        <div className="bg-white rounded-xl shadow p-6 mb-6">
          <h2 className="font-semibold text-gray-700 mb-4 text-lg">Account Information</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">
                Username
              </p>
              <p className="text-sm text-gray-800 font-medium">{user?.username ?? "—"}</p>
            </div>
            <div>
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">
                Email
              </p>
              <p className="text-sm text-gray-800 font-medium">{user?.email ?? "—"}</p>
            </div>
            <div>
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">
                Role
              </p>
              <p className="text-sm text-gray-800 font-medium">
                {ROLE_LABELS[user?.role] ?? user?.role ?? "—"}
              </p>
            </div>
          </div>
        </div>

        {/* Change Password */}
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="font-semibold text-gray-700 mb-4 text-lg">Change Password</h2>
          <form onSubmit={handleSubmit} noValidate className="space-y-4 max-w-md">
            {/* Current Password */}
            <div>
              <label
                htmlFor="currentPassword"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Current Password
              </label>
              <input
                id="currentPassword"
                type="password"
                value={currentPassword}
                onChange={(e) => {
                  setCurrentPassword(e.target.value);
                  setErrors((prev) => ({ ...prev, currentPassword: undefined }));
                }}
                autoComplete="current-password"
                className={`w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 ${
                  errors.currentPassword ? "border-red-400" : "border-gray-300"
                }`}
              />
              {errors.currentPassword && (
                <p className="mt-1 text-xs text-red-600">{errors.currentPassword}</p>
              )}
            </div>

            {/* New Password */}
            <div>
              <label
                htmlFor="newPassword"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                New Password
              </label>
              <input
                id="newPassword"
                type="password"
                value={newPassword}
                onChange={(e) => {
                  setNewPassword(e.target.value);
                  setErrors((prev) => ({ ...prev, newPassword: undefined }));
                }}
                autoComplete="new-password"
                className={`w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 ${
                  errors.newPassword ? "border-red-400" : "border-gray-300"
                }`}
              />
              {errors.newPassword ? (
                <p className="mt-1 text-xs text-red-600">{errors.newPassword}</p>
              ) : (
                <p className="mt-1 text-xs text-gray-400">Minimum 8 characters.</p>
              )}
            </div>

            {/* Confirm Password */}
            <div>
              <label
                htmlFor="confirmPassword"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Confirm New Password
              </label>
              <input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => {
                  setConfirmPassword(e.target.value);
                  setErrors((prev) => ({ ...prev, confirmPassword: undefined }));
                }}
                autoComplete="new-password"
                className={`w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 ${
                  errors.confirmPassword ? "border-red-400" : "border-gray-300"
                }`}
              />
              {errors.confirmPassword && (
                <p className="mt-1 text-xs text-red-600">{errors.confirmPassword}</p>
              )}
            </div>

            <div className="pt-2">
              <button
                type="submit"
                disabled={saving}
                className="bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white text-sm font-medium px-5 py-2 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-brand-500"
              >
                {saving ? "Saving…" : "Update Password"}
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
}
