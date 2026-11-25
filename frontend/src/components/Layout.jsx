import { useEffect, useState } from "react";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { useAuth } from "../context/AuthContext";
import { notificationApi } from "../api/endpoints";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import CartDrawer from "./CartDrawer";

const COLLAPSE_KEY = "pizza_sidebar_collapsed";

export default function Layout() {
  const { logout } = useAuth();
  const [unread, setUnread] = useState(0);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(() => localStorage.getItem(COLLAPSE_KEY) === "1");
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => setMobileOpen(false), [location.pathname, location.search]);

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

  const toggleCollapse = () =>
    setCollapsed((c) => {
      localStorage.setItem(COLLAPSE_KEY, c ? "0" : "1");
      return !c;
    });

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-canvas">
      <Sidebar
        collapsed={collapsed}
        onToggleCollapse={toggleCollapse}
        mobileOpen={mobileOpen}
        onCloseMobile={() => setMobileOpen(false)}
        unread={unread}
        onLogout={handleLogout}
      />

      <div className={`flex min-h-screen flex-col transition-[padding] duration-300 ease-out ${collapsed ? "lg:pl-20" : "lg:pl-[264px]"}`}>
        <Topbar onOpenSidebar={() => setMobileOpen(true)} unread={unread} />
        <main className="mx-auto w-full max-w-7xl flex-1 px-4 pb-16 pt-6 sm:px-6 lg:px-8">
          <motion.div key={location.pathname} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.2, ease: "easeOut" }}>
            <Outlet />
          </motion.div>
        </main>
      </div>

      <CartDrawer />
    </div>
  );
}
