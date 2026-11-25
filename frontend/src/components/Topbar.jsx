import { useEffect, useRef, useState } from "react";
import { Link, useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { Bell, Check, ChevronDown, MapPin, Menu as MenuIcon, Plus, Search, ShoppingBag, X } from "lucide-react";
import { addressApi } from "../api/endpoints";
import { useCart } from "../context/CartContext";
import { useToast } from "../context/ToastContext";
import { money, useLoad } from "./ui";
import Logo from "./Logo";

/** Search box synced with /menu?q= so results update as you type. */
function SearchBox({ autoFocus = false, onDone }) {
  const [params] = useSearchParams();
  const location = useLocation();
  const navigate = useNavigate();
  const onMenu = location.pathname === "/menu" || location.pathname === "/favorites";
  const [value, setValue] = useState(onMenu ? params.get("q") || "" : "");

  useEffect(() => {
    if (onMenu) setValue(params.get("q") || "");
  }, [params, onMenu]);

  const push = (q, replace) => {
    const base = onMenu ? location.pathname : "/menu";
    const next = new URLSearchParams(onMenu ? params : undefined);
    if (q) next.set("q", q);
    else next.delete("q");
    const qs = next.toString();
    navigate(`${base}${qs ? `?${qs}` : ""}`, { replace });
  };

  return (
    <form
      role="search"
      className="relative w-full"
      onSubmit={(e) => {
        e.preventDefault();
        push(value.trim(), false);
        onDone?.();
      }}
    >
      <Search className="pointer-events-none absolute left-3.5 top-1/2 h-[18px] w-[18px] -translate-y-1/2 text-muted" aria-hidden="true" />
      <input
        type="search"
        value={value}
        autoFocus={autoFocus}
        onChange={(e) => {
          setValue(e.target.value);
          if (onMenu) push(e.target.value.trim(), true);
        }}
        placeholder="Search pizzas, e.g. pepperoni…"
        aria-label="Search the menu"
        className="h-11 rounded-full border-transparent bg-surface-2 pl-10 pr-9 focus:bg-surface"
      />
      {value && (
        <button
          type="button"
          onClick={() => {
            setValue("");
            if (onMenu) push("", true);
          }}
          className="absolute right-2 top-1/2 grid h-7 w-7 -translate-y-1/2 place-items-center rounded-full text-muted hover:bg-line/60"
          aria-label="Clear search"
        >
          <X className="h-4 w-4" />
        </button>
      )}
    </form>
  );
}

/** Delivery location picker backed by the saved-addresses API. */
function LocationPicker() {
  const addresses = useLoad(() => addressApi.list().catch(() => []));
  const { toast } = useToast();
  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(null);
  const ref = useRef(null);
  const location = useLocation();

  useEffect(() => {
    if (!open) return undefined;
    const onDown = (e) => ref.current && !ref.current.contains(e.target) && setOpen(false);
    const onKey = (e) => e.key === "Escape" && setOpen(false);
    document.addEventListener("mousedown", onDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  // Pick up changes made on the Addresses page (skip the first run: useLoad already fetched).
  const firstRun = useRef(true);
  useEffect(() => {
    if (firstRun.current) {
      firstRun.current = false;
      return;
    }
    addresses.reload();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.pathname]);

  const list = addresses.data || [];
  const current = list.find((a) => a.is_default) || list[0];

  const choose = async (a) => {
    if (a.is_default) return setOpen(false);
    setSaving(a.id);
    try {
      await addressApi.setDefault(a.id);
      await addresses.reload();
      toast({ title: `Delivering to ${a.label}`, description: `${a.street}, ${a.city}` });
      setOpen(false);
    } catch (err) {
      toast({ type: "error", title: "Couldn't change address", description: err.message });
    } finally {
      setSaving(null);
    }
  };

  return (
    <div className="relative" ref={ref}>
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        aria-haspopup="listbox"
        className="flex h-11 max-w-[230px] items-center gap-2.5 rounded-full px-2 text-left transition hover:bg-surface-2"
      >
        <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-brand-soft text-brand-600">
          <MapPin className="h-4 w-4" aria-hidden="true" />
        </span>
        <span className="min-w-0 leading-tight">
          <span className="block text-[0.68rem] font-semibold uppercase tracking-wider text-muted">Deliver to</span>
          <span className="block truncate text-sm font-semibold text-ink">
            {addresses.loading && !current ? "Loading…" : current ? `${current.label} · ${current.street}` : "Add an address"}
          </span>
        </span>
        <ChevronDown className={`h-4 w-4 shrink-0 text-muted transition-transform ${open ? "rotate-180" : ""}`} aria-hidden="true" />
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -6, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -6, scale: 0.98 }}
            transition={{ duration: 0.15 }}
            className="absolute left-0 top-full z-40 mt-2 w-80 origin-top-left rounded-2xl border border-line bg-surface p-2 shadow-pop"
          >
            <p className="px-3 pb-1 pt-2 text-xs font-bold uppercase tracking-wider text-muted">Saved addresses</p>
            {list.length === 0 && <p className="px-3 py-2 text-sm text-muted">No saved addresses yet.</p>}
            <ul role="listbox" aria-label="Delivery address" className="max-h-72 overflow-y-auto">
              {list.map((a) => (
                <li key={a.id}>
                  <button
                    type="button"
                    role="option"
                    aria-selected={a.id === current?.id}
                    disabled={saving !== null}
                    onClick={() => choose(a)}
                    className="flex w-full items-start gap-3 rounded-xl px-3 py-2.5 text-left transition hover:bg-surface-2"
                  >
                    <MapPin className="mt-0.5 h-4 w-4 shrink-0 text-muted" aria-hidden="true" />
                    <span className="min-w-0 flex-1">
                      <span className="block text-sm font-semibold text-ink">{a.label}</span>
                      <span className="block truncate text-xs text-muted">
                        {a.street}, {a.city}
                      </span>
                    </span>
                    {saving === a.id ? (
                      <span className="h-4 w-4 animate-spin rounded-full border-2 border-line border-t-brand-600" />
                    ) : (
                      a.id === current?.id && <Check className="h-4 w-4 text-brand-600" aria-hidden="true" />
                    )}
                  </button>
                </li>
              ))}
            </ul>
            <Link
              to="/addresses"
              onClick={() => setOpen(false)}
              className="mt-1 flex items-center gap-2 rounded-xl border-t border-line px-3 py-2.5 text-sm font-semibold no-underline hover:bg-surface-2"
            >
              <Plus className="h-4 w-4" /> Manage addresses
            </Link>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function CartButton() {
  const { count, total, openDrawer, bumpKey } = useCart();
  return (
    <button
      type="button"
      onClick={openDrawer}
      className="relative flex h-11 items-center gap-2 rounded-full bg-brand-600 pl-3 pr-3 text-white shadow-brand transition hover:bg-brand-700 active:scale-95 sm:pr-4"
      aria-label={`Open cart, ${count} item${count === 1 ? "" : "s"}`}
    >
      <span key={`bump-${bumpKey}`} className={bumpKey ? "animate-bump" : ""}>
        <ShoppingBag className="h-5 w-5" aria-hidden="true" />
      </span>
      <span className="hidden text-sm font-semibold sm:inline">{count > 0 ? money(total) : "Cart"}</span>
      {count > 0 && (
        <motion.span
          key={`count-${count}`}
          initial={{ scale: 0.4 }}
          animate={{ scale: 1 }}
          className="absolute -right-1 -top-1 grid h-5 min-w-[20px] place-items-center rounded-full bg-amber-400 px-1 text-[0.68rem] font-extrabold text-ink ring-2 ring-surface"
        >
          {count > 99 ? "99+" : count}
        </motion.span>
      )}
    </button>
  );
}

export default function Topbar({ onOpenSidebar, unread }) {
  const [mobileSearch, setMobileSearch] = useState(false);
  const location = useLocation();

  useEffect(() => setMobileSearch(false), [location.pathname]);

  return (
    <header className="sticky top-0 z-20 border-b border-line bg-surface/85 backdrop-blur-xl">
      <div className="flex h-16 items-center gap-2 px-3 sm:gap-3 sm:px-6">
        <button type="button" className="icon-btn border-0 lg:hidden" onClick={onOpenSidebar} aria-label="Open menu">
          <MenuIcon className="h-5 w-5" />
        </button>
        <Link to="/menu" className="no-underline lg:hidden" aria-label="Home">
          <Logo compact className="sm:hidden" />
          <Logo className="hidden sm:inline-flex" />
        </Link>

        <div className="hidden sm:block lg:ml-0">
          <LocationPicker />
        </div>

        <div className="mx-auto hidden w-full max-w-xl md:block">
          <SearchBox />
        </div>

        <div className="ml-auto flex items-center gap-1.5 sm:gap-2 md:ml-0">
          <button
            type="button"
            className="icon-btn border-0 md:hidden"
            onClick={() => setMobileSearch((s) => !s)}
            aria-label="Search"
            aria-expanded={mobileSearch}
          >
            <Search className="h-5 w-5" />
          </button>
          <Link to="/notifications" className="icon-btn relative border-0" aria-label={`Notifications (${unread} unread)`}>
            <Bell className="h-5 w-5" />
            {unread > 0 && (
              <span className="absolute right-1.5 top-1.5 grid h-4 min-w-[16px] place-items-center rounded-full bg-brand-600 px-1 text-[0.6rem] font-bold text-white ring-2 ring-surface">
                {unread > 9 ? "9+" : unread}
              </span>
            )}
          </Link>
          <CartButton />
        </div>
      </div>

      {/* Phones: delivery location gets its own slim row */}
      <div className="border-t border-line px-2 py-1 sm:hidden">
        <LocationPicker />
      </div>

      <AnimatePresence initial={false}>
        {mobileSearch && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden md:hidden"
          >
            <div className="px-3 pb-3">
              <SearchBox autoFocus onDone={() => setMobileSearch(false)} />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
