import { Navigate, Route, BrowserRouter as Router, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import { ToastProvider } from "./contexts/ToastContext";
import Dashboard from "./pages/Dashboard";
import ISOUpload from "./pages/ISOUpload";
import LineList from "./pages/LineList";
import Login from "./pages/Login";
import NotFound from "./pages/NotFound";
import PMSValidation from "./pages/PMSValidation";
import Settings from "./pages/Settings";
import UserManagement from "./pages/UserManagement";

function PrivateRoute({ children, adminOnly = false }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="flex items-center justify-center h-screen">Loading...</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (adminOnly && user.role !== "admin") return <Navigate to="/" replace />;
  return children;
}

export default function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <Router>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route
              path="/"
              element={
                <PrivateRoute>
                  <Dashboard />
                </PrivateRoute>
              }
            />
            <Route
              path="/iso"
              element={
                <PrivateRoute>
                  <ISOUpload />
                </PrivateRoute>
              }
            />
            <Route
              path="/linelist"
              element={
                <PrivateRoute>
                  <LineList />
                </PrivateRoute>
              }
            />
            <Route
              path="/pms"
              element={
                <PrivateRoute>
                  <PMSValidation />
                </PrivateRoute>
              }
            />
            <Route
              path="/users"
              element={
                <PrivateRoute adminOnly>
                  <UserManagement />
                </PrivateRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <PrivateRoute>
                  <Settings />
                </PrivateRoute>
              }
            />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Router>
      </ToastProvider>
    </AuthProvider>
  );
}
