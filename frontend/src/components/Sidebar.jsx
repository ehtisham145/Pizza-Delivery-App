import { Link, useLocation } from "react-router-dom";
import { AnimatePresence, LayoutGroup, motion } from "framer-motion";
import {
  Bell,
  ChevronsLeft,
  CreditCard,
  Heart,
  LogOut,
  MapPin,
  Pizza,
  ReceiptText,
  Settings,
  Star,
  Truck,
  X,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import Logo from "./Logo";

// `match` decides the active state (query-aware, so "Track order" and
// "My orders" can share the /orders route).
const ORDER_LINKS = [
  { to: "/menu", label: "Menu", icon: Pizza },
  { to: "/favorites", label: "Favorites", icon: Heart },
  { to: "/orders", label: "My orders", icon: ReceiptText, match: (l) => l.pathname === "/orders" && !l.search.includes("filter=active") },
  { to: "/orders?filter=active", label: "Track order", icon: Truck, match: (l) => l.pathname === "/orders" && l.search.includes("filter=active") },
];

const ACCOUNT_LINKS = [
  { to: "/notifications", label: "Notifications", icon: Bell, badge: "unread" },
  { to: "/addresses", label: "Addresses", icon: MapPin },
  { to: "/payments", label: "Payments", icon: CreditCard },
  { to: "/reviews", label: "My reviews", icon: Star },
  { to: "/profile", label: "Profile & settings", icon: Settings },
];


function NavItem({ link, collapsed, unread, onNavigate }) {
  const location = useLocation();
  const active = link.match ? link.match(location) : location.pathname === link.to || location.pathname.startsWith(`${link.to}/`);
  const Icon = link.icon;
  const count = link.badge === "unread" ? unread : 0;

  return (
    <Link
      to={link.to}
      onClick={onNavigate}
      title={collapsed ? link.label : undefined}
      aria-current={active ? "page" : undefined}
      className={`group relative flex h-11 items-center gap-3 rounded-xl px-3 text-[0.92rem] font-medium no-underline transition-colors
        ${active ? "bg-brand-soft text-brand-ink" : "text-muted hover:bg-surface-2 hover:text-ink"}
        ${collapsed ? "justify-center px-0" : ""}`}
    >
      {active && (
        <motion.span
          layoutId="sidebar-active"
          className="absolute left-0 top-2 bottom-2 w-1 rounded-r-full bg-brand-600"
          transition={{ type: "spring", stiffness: 500, damping: 40 }}
        />
      )}
      <Icon className={`h-5 w-5 shrink-0 ${active ? "text-brand-600" : ""}`} strokeWidth={active ? 2.4 : 2} aria-hidden="true" />
      {!collapsed && <span className="truncate">{link.label}</span>}
      {count > 0 && (
        <span
          className={`grid min-w-[20px] place-items-center rounded-full bg-brand-600 px-1.5 text-[0.68rem] font-bold leading-5 text-white
            ${collapsed ? "absolute right-1.5 top-1" : "ml-auto"}`}
        >
          {count > 99 ? "99+" : count}
        </span>
      )}
    </Link>
  );
}

function Section({ title, collapsed, children }) {
  return (
    <div className="mb-5">
      {collapsed ? (
        <div className="mx-auto mb-2 h-px w-8 bg-line" aria-hidden="true" />
      ) : (
        <p className="mb-1.5 px-3 text-[0.7rem] font-bold uppercase tracking-[0.12em] text-muted/80">{title}</p>
      )}
      <nav className="flex flex-col gap-0.5" aria-label={title}>
        {children}
      </nav>
    </div>
  );
}

function SidebarBody({ collapsed, unread, onNavigate, onLogout, onToggleCollapse, onClose }) {
  const { user } = useAuth();
  const initial = (user?.full_name || "?").charAt(0).toUpperCase();

  return (
    <div className="flex h-full flex-col">
      <div className={`flex h-16 items-center border-b border-line ${collapsed ? "justify-center px-2" : "justify-between px-5"}`}>
        <Link to="/menu" onClick={onNavigate} className="no-underline" aria-label="Home">
          <Logo compact={collapsed} />
        </Link>
        {onClose && (
          <button type="button" className="icon-btn border-0 bg-surface-2" onClick={onClose} aria-label="Close menu">
            <X className="h-5 w-5" />
          </button>
        )}
      </div>

      <div className={`no-scrollbar flex-1 overflow-y-auto py-5 ${collapsed ? "px-2" : "px-3"}`}>
        <Section title="Order" collapsed={collapsed}>
          {ORDER_LINKS.map((l) => (
            <NavItem key={l.to} link={l} collapsed={collapsed} onNavigate={onNavigate} />
          ))}
        </Section>
        <Section title="Account" collapsed={collapsed}>
          {ACCOUNT_LINKS.map((l) => (
            <NavItem key={l.to} link={l} collapsed={collapsed} unread={unread} onNavigate={onNavigate} />
          ))}
        </Section>
      </div>

      <div className={`border-t border-line p-3 ${collapsed ? "flex flex-col items-center gap-2" : ""}`}>
        <div className={`flex items-center gap-3 rounded-xl ${collapsed ? "" : "bg-surface-2 p-2.5"}`}>
          <Link
            to="/profile"
            onClick={onNavigate}
            title={user?.full_name}
            className="grid h-10 w-10 shrink-0 place-items-center rounded-full bg-gradient-to-br from-amber-400 to-brand-500 font-display font-bold text-white no-underline"
          >
            {initial}
          </Link>
          {!collapsed && (
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-semibold text-ink">{user?.full_name || "Guest"}</p>
              <p className="truncate text-xs text-muted">{user?.email}</p>
            </div>
          )}
          {!collapsed && (
            <button type="button" onClick={onLogout} className="icon-btn h-9 w-9 border-0 bg-transparent" aria-label="Log out" title="Log out">
              <LogOut className="h-[18px] w-[18px]" />
            </button>
          )}
        </div>
        {collapsed && (
          <button type="button" onClick={onLogout} className="icon-btn border-0" aria-label="Log out" title="Log out">
            <LogOut className="h-[18px] w-[18px]" />
          </button>
        )}
        {onToggleCollapse && (
          <button
            type="button"
            onClick={onToggleCollapse}
            className={`mt-2 hidden h-9 items-center gap-2 rounded-lg px-3 text-xs font-semibold text-muted transition hover:bg-surface-2 hover:text-ink lg:flex ${collapsed ? "w-10 justify-center px-0" : "w-full"}`}
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
            aria-expanded={!collapsed}
          >
            <ChevronsLeft className={`h-4 w-4 transition-transform ${collapsed ? "rotate-180" : ""}`} />
            {!collapsed && "Collapse"}
          </button>
        )}
      </div>
    </div>
  );
}

/** Desktop: fixed, collapsible rail. Mobile: slide-out drawer. */
export default function Sidebar({ collapsed, onToggleCollapse, mobileOpen, onCloseMobile, unread, onLogout }) {
  return (
    <>
      <aside
        className={`fixed inset-y-0 left-0 z-30 hidden border-r border-line bg-surface transition-[width] duration-300 ease-out lg:block ${
          collapsed ? "w-20" : "w-[264px]"
        }`}
      >
        <LayoutGroup id="sidebar-desktop">
          <SidebarBody collapsed={collapsed} unread={unread} onLogout={onLogout} onToggleCollapse={onToggleCollapse} />
        </LayoutGroup>
      </aside>

      <AnimatePresence>
        {mobileOpen && (
          <div className="fixed inset-0 z-50 lg:hidden">
            <motion.div
              className="absolute inset-0 bg-black/50 backdrop-blur-sm"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={onCloseMobile}
            />
            <motion.aside
              className="absolute inset-y-0 left-0 w-[86%] max-w-[300px] bg-surface shadow-pop"
              initial={{ x: "-100%" }}
              animate={{ x: 0 }}
              exit={{ x: "-100%" }}
              transition={{ type: "spring", damping: 30, stiffness: 300 }}
              aria-label="Navigation"
            >
              <LayoutGroup id="sidebar-mobile">
                <SidebarBody collapsed={false} unread={unread} onNavigate={onCloseMobile} onLogout={onLogout} onClose={onCloseMobile} />
              </LayoutGroup>
            </motion.aside>
          </div>
        )}
      </AnimatePresence>
    </>
  );
}
