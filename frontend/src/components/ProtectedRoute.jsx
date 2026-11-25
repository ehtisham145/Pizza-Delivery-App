import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

// role:
//   undefined  -> any logged-in user
//   "customer" -> customers only (admins/staff are sent to the Admin Console)
//   "staff"    -> admin or staff
//   "admin"    -> admin only
export default function ProtectedRoute({ role }) {
  const { isAuthenticated, isAdmin, isStaff, home } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) return <Navigate to="/login" replace state={{ from: location.pathname + location.search }} />;
  if (role === "customer" && isStaff) return <Navigate to={home} replace />;
  if (role === "admin" && !isAdmin) return <Navigate to={home} replace />;
  if (role === "staff" && !isStaff) return <Navigate to={home} replace />;
  return <Outlet />;
}
