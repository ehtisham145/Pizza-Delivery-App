import { useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { ArrowRight, ShoppingBag, Trash2, X } from "lucide-react";
import { useCart } from "../context/CartContext";
import { useToast } from "../context/ToastContext";
import { Empty, QtyStepper, Skeleton, money, useLockBodyScroll } from "./ui";
import PizzaImage from "./PizzaImage";

export function CartLine({ item, compact = false }) {
  const { setQuantity, remove, busy } = useCart();
  const { toast } = useToast();
  const name = item.pizza?.name || `Pizza #${item.pizza_id}`;

  const safe = (fn) => fn().catch((err) => toast({ type: "error", title: "Cart not updated", description: err.message }));

  return (
    <motion.li
      layout
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, x: 40, height: 0, marginBottom: 0, paddingTop: 0, paddingBottom: 0 }}
      transition={{ duration: 0.2 }}
      className="flex gap-3.5 border-b border-line py-4 last:border-b-0"
    >
      <div className={`${compact ? "h-16 w-16" : "h-20 w-20"} shrink-0 overflow-hidden rounded-xl bg-surface-2`}>
        <PizzaImage pizza={item.pizza || { id: item.pizza_id }} width={200} sizes="80px" className="h-full w-full" alt="" />
      </div>
      <div className="flex min-w-0 flex-1 flex-col">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <p className="truncate font-display font-bold text-ink">{name}</p>
            <p className="text-xs text-muted">
              {item.size} · {money(item.unit_price)} each
            </p>
          </div>
          <button
            type="button"
            onClick={() => safe(() => remove(item))}
            disabled={busy}
            className="-mr-1 -mt-1 grid h-8 w-8 shrink-0 place-items-center rounded-lg text-muted transition hover:bg-brand-soft hover:text-brand-600"
            aria-label={`Remove ${name}`}
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
        <div className="mt-auto flex items-center justify-between gap-2 pt-2">
          <QtyStepper size="sm" value={item.quantity} max={20} onChange={(q) => safe(() => setQuantity(item, q))} label={`Quantity of ${name}`} />
          <span className="font-semibold tabular-nums text-ink">{money(item.sub_total)}</span>
        </div>
      </div>
    </motion.li>
  );
}

export default function CartDrawer() {
  const { drawerOpen, closeDrawer, items, count, total, loading, error, busy } = useCart();
  const navigate = useNavigate();
  const location = useLocation();
  useLockBodyScroll(drawerOpen);

  useEffect(() => {
    closeDrawer();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.pathname]);

  useEffect(() => {
    if (!drawerOpen) return undefined;
    const onKey = (e) => e.key === "Escape" && closeDrawer();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [drawerOpen, closeDrawer]);

  return (
    <AnimatePresence>
      {drawerOpen && (
        <div className="fixed inset-0 z-50">
          <motion.div
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={closeDrawer}
          />
          <motion.aside
            role="dialog"
            aria-modal="true"
            aria-label="Your cart"
            className="absolute inset-y-0 right-0 flex w-full max-w-md flex-col bg-surface shadow-pop"
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 32, stiffness: 320 }}
          >
            <header className="flex h-16 items-center justify-between border-b border-line px-5">
              <h2 className="flex items-center gap-2 text-lg">
                <ShoppingBag className="h-5 w-5 text-brand-600" aria-hidden="true" />
                Your cart
                {count > 0 && <span className="rounded-full bg-surface-2 px-2 py-0.5 text-xs font-bold text-muted">{count}</span>}
              </h2>
              <button type="button" className="icon-btn border-0 bg-surface-2" onClick={closeDrawer} aria-label="Close cart">
                <X className="h-5 w-5" />
              </button>
            </header>

            <div className="flex-1 overflow-y-auto px-5">
              {loading && items.length === 0 ? (
                <div className="space-y-5 py-5" role="status" aria-label="Loading cart">
                  {[0, 1, 2].map((i) => (
                    <div key={i} className="flex gap-3.5">
                      <Skeleton className="h-20 w-20 rounded-xl" />
                      <div className="flex-1 space-y-2 pt-1">
                        <Skeleton className="h-4 w-2/3" />
                        <Skeleton className="h-3 w-1/3" />
                        <Skeleton className="mt-4 h-8 w-28 rounded-full" />
                      </div>
                    </div>
                  ))}
                </div>
              ) : error ? (
                <p className="alert alert-error mt-5">{error}</p>
              ) : items.length === 0 ? (
                <Empty
                  icon={ShoppingBag}
                  title="Your cart is empty"
                  action={
                    <button type="button" className="btn btn-primary" onClick={() => (location.pathname === "/menu" ? closeDrawer() : navigate("/menu"))}>
                      Browse the menu
                    </button>
                  }
                >
                  Hungry? Add a pizza or two and they'll show up here.
                </Empty>
              ) : (
                <ul className="m-0 list-none p-0">
                  <AnimatePresence initial={false}>
                    {items.map((item) => (
                      <CartLine key={item.id} item={item} />
                    ))}
                  </AnimatePresence>
                </ul>
              )}
            </div>

            {items.length > 0 && (
              <footer className="border-t border-line bg-surface px-5 pt-4 pb-safe">
                <div className="mb-4 flex items-baseline justify-between">
                  <span className="text-sm text-muted">Subtotal</span>
                  <span className="font-display text-2xl font-extrabold tabular-nums text-ink">{money(total)}</span>
                </div>
                <button type="button" className="btn btn-primary btn-block h-12 text-base" disabled={busy} onClick={() => {
                    closeDrawer();
                    navigate("/cart");
                  }}>
                  Go to checkout <ArrowRight className="h-5 w-5" aria-hidden="true" />
                </button>
              </footer>
            )}
          </motion.aside>
        </div>
      )}
    </AnimatePresence>
  );
}
