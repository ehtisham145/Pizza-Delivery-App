import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { cartApi } from "../api/endpoints";
import { useAuth } from "./AuthContext";

// One place that owns the cart so the top-bar badge, the slide-over drawer,
// the menu and the checkout page always agree. Uses the same cartApi calls
// the old Cart page made.
const CartContext = createContext(null);

export function CartProvider({ children }) {
  const { isAuthenticated, isStaff } = useAuth();
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [pending, setPending] = useState(0); // in-flight mutations
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [bumpKey, setBumpKey] = useState(0);

  const reload = useCallback(async () => {
    if (!isAuthenticated || isStaff) {
      setCart(null);
      setLoading(false);
      return;
    }
    setError("");
    try {
      const list = await cartApi.get(); // backend returns a list; a user has at most one cart
      setCart(list?.[0] || null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, isStaff]);

  useEffect(() => {
    setLoading(true);
    reload();
  }, [reload]);

  const mutate = useCallback(
    async (fn) => {
      setPending((n) => n + 1);
      try {
        return await fn();
      } finally {
        await reload();
        setPending((n) => n - 1);
      }
    },
    [reload]
  );

  const add = useCallback(
    async (pizza, { size_id, quantity }) => {
      const res = await mutate(() => cartApi.add(pizza.id, { size_id, quantity }));
      setBumpKey((k) => k + 1);
      return res;
    },
    [mutate]
  );

  const setQuantity = useCallback(
    async (item, qty) => {
      if (qty < 1) return undefined;
      // Optimistic: show the new quantity immediately.
      setCart((c) =>
        c
          ? {
              ...c,
              items: c.items.map((i) =>
                i.id === item.id ? { ...i, quantity: qty, sub_total: Number(i.unit_price) * qty } : i
              ),
            }
          : c
      );
      return mutate(() => cartApi.updateQuantity(item.id, qty));
    },
    [mutate]
  );

  const remove = useCallback(
    async (item) => {
      setCart((c) => (c ? { ...c, items: c.items.filter((i) => i.id !== item.id) } : c));
      return mutate(() => cartApi.removeItem(item.id));
    },
    [mutate]
  );

  const clear = useCallback(() => mutate(() => cartApi.clear()), [mutate]);

  const value = useMemo(() => {
    const items = cart?.items || [];
    const count = items.reduce((n, i) => n + Number(i.quantity || 0), 0);
    const localTotal = items.reduce((s, i) => s + Number(i.sub_total || 0), 0);
    return {
      cart,
      items,
      count,
      // While an optimistic change is in flight the server total is stale.
      total: pending ? localTotal : Number(cart?.total_price ?? localTotal),
      loading,
      error,
      busy: pending > 0,
      bumpKey,
      reload,
      add,
      setQuantity,
      remove,
      clear,
      drawerOpen,
      openDrawer: () => setDrawerOpen(true),
      closeDrawer: () => setDrawerOpen(false),
    };
  }, [cart, pending, loading, error, bumpKey, reload, add, setQuantity, remove, clear, drawerOpen]);

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export const useCart = () => useContext(CartContext);
