import { useEffect, useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { notificationApi } from "../api/endpoints";

const customerLinks = [
  { to: "/menu", label: "Menu" },
  { to: "/cart", label: "Cart" },
  { to: "/orders", label: "Orders" },
  { to: "/addresses", label: "Addresses" },
  { to: "/payments", label: "Payments" },
  { to: "/reviews", label: "My reviews" },
];

const staffLinks = [
  { to: "/admin/orders", label: "Manage orders" },
  { to: "/admin/menu", label: "Manage menu" },
  { to: "/admin/reviews", label: "Reviews" },
];

const adminLinks = [
  { to: "/admin", label: "Dashboard", end: true },
  { to: "/admin/users", label: "Users" },
  { to: "/admin/payments", label: "Payments" },
];

export default function Layout() {
  const { user, isAdmin, isStaff, logout } = useAuth();
  const [unread, setUnread] = useState(0);
  const [menuOpen, setMenuOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => setMenuOpen(false), [location.pathname]);

  useEffect(() => {
    let alive = true;
    const poll = () =>
      notificationApi
        .unreadCount()
        .then((n) => alive && setUnread(n))
        .catch(() => {});
    poll();
    const timer = setInterval(poll, 60000);
    return () => {
      alive = false;
      clearInterval(timer);
    };
  }, [location.pathname]);

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  const link = (l) => (
    <NavLink key={l.to} to={l.to} end={l.end} className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>
      {l.label}
    </NavLink>
  );

  return (
    <div className="app-shell">
      <header className="topbar">
        <NavLink to="/menu" className="brand">
          <span className="brand-icon">🍕</span> Pizza Delivery
        </NavLink>

        <button className="icon-btn nav-toggle" onClick={() => setMenuOpen((o) => !o)} aria-label="Toggle menu">
          ☰
        </button>

        <nav className={`nav ${menuOpen ? "open" : ""}`}>
          <div className="nav-group">{customerLinks.map(link)}</div>
          {isStaff && (
            <div className="nav-group nav-admin">
              {isAdmin && adminLinks.map(link)}
              {staffLinks.map(link)}
            </div>
          )}
        </nav>

        <div className="topbar-right">
          <NavLink to="/notifications" className="bell" aria-label={`Notifications (${unread} unread)`}>
            🔔{unread > 0 && <span className="bell-count">{unread > 99 ? "99+" : unread}</span>}
          </NavLink>
          <NavLink to="/profile" className="user-chip">
            <span className="avatar">{(user?.full_name || "?").charAt(0).toUpperCase()}</span>
            <span className="user-name">{user?.full_name}</span>
            {isStaff && <span className="role-tag">{user?.role}</span>}
          </NavLink>
          <button className="btn btn-ghost btn-sm" onClick={handleLogout}>
            Log out
          </button>
        </div>
      </header>

      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
