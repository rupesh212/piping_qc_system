import { Navigate, Route, BrowserRouter as Router, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import Dashboard from "./pages/Dashboard";
import ISOUpload from "./pages/ISOUpload";
import LineList from "./pages/LineList";
import Login from "./pages/Login";
import PMSValidation from "./pages/PMSValidation";

function PrivateRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="flex items-center justify-center h-screen">Loading...</div>;
  return user ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <AuthProvider>
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
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}
