import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { useAuth } from "./AuthContext";

// The backend has no favourites table, so favourites are stored per user in
// this browser's localStorage.
const FavoritesContext = createContext(null);

const keyFor = (user) => `pizza_favorites:${user?.email || user?.id || "guest"}`;

function read(key) {
  try {
    const v = JSON.parse(localStorage.getItem(key));
    return Array.isArray(v) ? v : [];
  } catch {
    return [];
  }
}

export function FavoritesProvider({ children }) {
  const { user } = useAuth();
  const key = keyFor(user);
  const [ids, setIds] = useState(() => read(key));

  useEffect(() => setIds(read(key)), [key]);

  const toggle = useCallback(
    (id) => {
      setIds((prev) => {
        const next = prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id];
        localStorage.setItem(key, JSON.stringify(next));
        return next;
      });
    },
    [key]
  );

  const value = useMemo(() => ({ ids, has: (id) => ids.includes(id), toggle }), [ids, toggle]);
  return <FavoritesContext.Provider value={value}>{children}</FavoritesContext.Provider>;
}

export const useFavorites = () => useContext(FavoritesContext);
