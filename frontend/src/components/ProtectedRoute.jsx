import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

// role: undefined (any logged-in user) | "staff" (admin or staff) | "admin"
export default function ProtectedRoute({ role }) {
  const { isAuthenticated, isAdmin, isStaff } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  if (role === "admin" && !isAdmin) return <Navigate to="/menu" replace />;
  if (role === "staff" && !isStaff) return <Navigate to="/menu" replace />;
  return <Outlet />;
}
