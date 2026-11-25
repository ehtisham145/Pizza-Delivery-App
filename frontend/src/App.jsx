import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import AdminLayout from "./components/admin/AdminLayout";
import ProtectedRoute from "./components/ProtectedRoute";
import { useAuth } from "./context/AuthContext";

import Login from "./pages/Login";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import Menu from "./pages/Menu";
import Cart from "./pages/Cart";
import Orders from "./pages/Orders";
import Addresses from "./pages/Addresses";
import Payments from "./pages/Payments";
import MyReviews from "./pages/MyReviews";
import Notifications from "./pages/Notifications";
import Profile from "./pages/Profile";

import AdminDashboard from "./pages/admin/AdminDashboard";
import AdminUsers from "./pages/admin/AdminUsers";
import AdminOrders from "./pages/admin/AdminOrders";
import AdminPayments from "./pages/admin/AdminPayments";
import AdminReviews from "./pages/admin/AdminReviews";
import AdminMenu from "./pages/admin/AdminMenu";

export default function App() {
  const { isAuthenticated, home } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={isAuthenticated ? <Navigate to={home} replace /> : <Login />} />
      <Route path="/register" element={isAuthenticated ? <Navigate to={home} replace /> : <Register />} />
      <Route path="/forgot-password" element={isAuthenticated ? <Navigate to={home} replace /> : <ForgotPassword />} />
      {/* Reachable while logged in too: the e-mailed link must always work. */}
      <Route path="/reset-password" element={<ResetPassword />} />

      {/* Customer storefront */}
      <Route element={<ProtectedRoute role="customer" />}>
        <Route element={<Layout />}>
          <Route path="/menu" element={<Menu />} />
          <Route path="/favorites" element={<Menu key="favorites" favoritesOnly />} />
          <Route path="/cart" element={<Cart />} />
          <Route path="/orders" element={<Orders />} />
          <Route path="/addresses" element={<Addresses />} />
          <Route path="/payments" element={<Payments />} />
          <Route path="/reviews" element={<MyReviews />} />
          <Route path="/notifications" element={<Notifications />} />
          <Route path="/profile" element={<Profile />} />
        </Route>
      </Route>

      {/* Admin Console: a separate app shell for admins and staff */}
      <Route element={<ProtectedRoute role="staff" />}>
        <Route element={<AdminLayout />}>
          <Route path="/admin/orders" element={<AdminOrders />} />
          <Route path="/admin/menu" element={<AdminMenu />} />
          <Route path="/admin/reviews" element={<AdminReviews />} />
          <Route path="/admin/account" element={<Profile />} />

          <Route element={<ProtectedRoute role="admin" />}>
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/admin/users" element={<AdminUsers />} />
            <Route path="/admin/payments" element={<AdminPayments />} />
          </Route>
        </Route>
      </Route>

      <Route path="*" element={<Navigate to={isAuthenticated ? home : "/login"} replace />} />
    </Routes>
  );
}
