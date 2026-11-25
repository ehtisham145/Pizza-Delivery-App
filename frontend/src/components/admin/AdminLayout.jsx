import { useEffect, useState } from "react";
import { Link, Outlet, useLocation, useNavigate } from "react-router-dom";
import { AnimatePresence, LayoutGroup, motion } from "framer-motion";
import {
  ChefHat,
  ChevronRight,
  LayoutDashboard,
  LogOut,
  Menu as MenuIcon,
  MessageSquareText,
  Pizza,
  ShieldCheck,
  UserCog,
  Users,
  Wallet,
  X,
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { BRAND_NAME } from "../../constants";

// The Admin Console is its own app shell: always-dark sidebar, operations-
// focused top bar, no storefront elements (cart, search, delivery address).

const SECTIONS = [
  {
    title: "Overview",
    links: [{ to: "/admin", label: "Dashboard", icon: LayoutDashboard, admin: true, exact: true }],
  },
  {
    title: "Operations",
    links: [
      { to: "/admin/orders", label: "Orders", icon: ChefHat },
      { to: "/admin/menu", label: "Menu & pricing", icon: Pizza },
      { to: "/admin/reviews", label: "Reviews", icon: MessageSquareText },
    ],
  },
  {
    title: "People & money",
    links: [
      { to: "/admin/users", label: "Users", icon: Users, admin: true },
      { to: "/admin/payments", label: "Payments", icon: Wallet, admin: true },
    ],
  },
  {
    title: "You",
    links: [{ to: "/admin/account", label: "My account", icon: UserCog }],
  },
];

const ALL_LINKS = SECTIONS.flatMap((s) => s.links);
const isActive = (link, pathname) => (link.exact ? pathname === link.to : pathname === link.to || pathname.startsWith(`${link.to}/`));

function ConsoleNav({ onNavigate, onLogout }) {
  const { user, isAdmin } = useAuth();
  const { pathname } = useLocation();
  const [first] = BRAND_NAME.split(" ");

  return (
    <div className="flex h-full flex-col bg-[#0E1014] text-gray-400">
      <div className="flex h-16 items-center gap-3 border-b border-white/5 px-5">
        <span className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-gradient-to-br from-brand-500 to-brand-700 text-white">
          <ShieldCheck className="h-5 w-5" aria-hidden="true" />
        </span>
        <div className="min-w-0 leading-tight">
          <p className="truncate font-display text-base font-extrabold text-white" title={BRAND_NAME}>
            {first}
          </p>
          <p className="text-[0.62rem] font-bold uppercase tracking-[0.2em] text-amber-400">Admin Console</p>
        </div>
      </div>

      <nav className="no-scrollbar flex-1 overflow-y-auto px-3 py-5" aria-label="Admin">
        <LayoutGroup id="admin-nav">
          {SECTIONS.map((section) => {
            const links = section.links.filter((l) => !l.admin || isAdmin);
            if (!links.length) return null;
            return (
              <div key={section.title} className="mb-6">
                <p className="mb-2 px-3 text-[0.65rem] font-bold uppercase tracking-[0.16em] text-gray-600">{section.title}</p>
                <div className="flex flex-col gap-0.5">
                  {links.map((l) => {
                    const active = isActive(l, pathname);
                    const Icon = l.icon;
                    return (
                      <Link
                        key={l.to}
                        to={l.to}
                        onClick={onNavigate}
                        aria-current={active ? "page" : undefined}
                        className={`relative flex h-10 items-center gap-3 rounded-lg px-3 text-sm font-medium no-underline transition-colors ${
                          active ? "text-white" : "text-gray-400 hover:bg-white/5 hover:text-gray-100"
                        }`}
                      >
                        {active && (
                          <motion.span
                            layoutId="admin-active"
                            className="absolute inset-0 rounded-lg bg-white/[0.08] ring-1 ring-inset ring-white/10"
                            transition={{ type: "spring", stiffness: 500, damping: 40 }}
                          />
                        )}
                        <Icon className={`relative h-[18px] w-[18px] ${active ? "text-amber-400" : ""}`} aria-hidden="true" />
                        <span className="relative">{l.label}</span>
                        {active && <ChevronRight className="relative ml-auto h-4 w-4 text-gray-500" aria-hidden="true" />}
                      </Link>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </LayoutGroup>
      </nav>

      <div className="border-t border-white/5 p-3">
        <div className="flex items-center gap-3 rounded-lg bg-white/[0.04] p-2.5">
          <span className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-amber-400 font-display text-sm font-extrabold text-gray-900">
            {(user?.full_name || "A").charAt(0).toUpperCase()}
          </span>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-semibold text-gray-100">{user?.full_name}</p>
            <p className="truncate text-[0.7rem] font-semibold uppercase tracking-wider text-amber-400/90">{isAdmin ? "Super admin" : "Staff"}</p>
          </div>
          <button
            type="button"
            onClick={onLogout}
            className="grid h-9 w-9 place-items-center rounded-lg text-gray-400 transition hover:bg-white/10 hover:text-white"
            aria-label="Log out"
            title="Log out"
          >
            <LogOut className="h-[18px] w-[18px]" />
          </button>
        </div>
      </div>
    </div>
  );
}

export default function AdminLayout() {
  const { logout, isAdmin: isAdminRole } = useAuth();
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => setMobileOpen(false), [pathname]);

  const current = ALL_LINKS.find((l) => isActive(l, pathname));
  const today = new Date().toLocaleDateString(undefined, { weekday: "long", day: "numeric", month: "long" });

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-[#F4F5F7] dark:bg-[#0B0C0F]">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 lg:block">
        <ConsoleNav onLogout={handleLogout} />
      </aside>

      <AnimatePresence>
        {mobileOpen && (
          <div className="fixed inset-0 z-50 lg:hidden">
            <motion.div className="absolute inset-0 bg-black/60" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setMobileOpen(false)} />
            <motion.aside
              className="absolute inset-y-0 left-0 w-[82%] max-w-[280px] shadow-pop"
              initial={{ x: "-100%" }}
              animate={{ x: 0 }}
              exit={{ x: "-100%" }}
              transition={{ type: "spring", damping: 30, stiffness: 300 }}
            >
              <ConsoleNav onNavigate={() => setMobileOpen(false)} onLogout={handleLogout} />
              <button
                type="button"
                onClick={() => setMobileOpen(false)}
                className="absolute -right-12 top-3 grid h-10 w-10 place-items-center rounded-full bg-white/10 text-white"
                aria-label="Close menu"
              >
                <X className="h-5 w-5" />
              </button>
            </motion.aside>
          </div>
        )}
      </AnimatePresence>

      <div className="flex min-h-screen flex-col lg:pl-64">
        <header className="sticky top-0 z-20 flex h-16 items-center gap-3 border-b border-line bg-surface/90 px-4 backdrop-blur-xl sm:px-6 lg:px-8">
          <button type="button" className="icon-btn border-0 lg:hidden" onClick={() => setMobileOpen(true)} aria-label="Open menu">
            <MenuIcon className="h-5 w-5" />
          </button>
          <div className="min-w-0">
            <p className="hidden text-[0.7rem] font-semibold uppercase tracking-wider text-muted sm:block">Admin Console</p>
            <p className="truncate font-display text-base font-bold text-ink">{current?.label || "Admin"}</p>
          </div>
          <div className="ml-auto flex items-center gap-3">
            <span className="hidden text-sm text-muted md:block">{today}</span>
            <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-100 px-3 py-1 text-xs font-bold text-amber-700 dark:bg-amber-400/15 dark:text-amber-300">
              <ShieldCheck className="h-3.5 w-3.5" aria-hidden="true" /> {isAdminRole ? "Super admin" : "Staff"}
            </span>
          </div>
        </header>

        <main className="mx-auto w-full max-w-[1400px] flex-1 px-4 pb-16 pt-6 sm:px-6 lg:px-8">
          <motion.div key={pathname} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.18 }}>
            <Outlet />
          </motion.div>
        </main>
      </div>
    </div>
  );
}
