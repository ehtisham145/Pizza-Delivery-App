import { useEffect, useState } from "react";
import { reviewApi } from "../api/endpoints";
import { PIZZA_SIZES } from "../constants";

// ── Pricing ─────────────────────────────────────────────────────
export const priceFor = (pizza, sizeId) => {
  const size = PIZZA_SIZES.find((s) => s.id === Number(sizeId));
  return Number(pizza?.base_price || 0) * (size?.multiplier || 1);
};

// ── Dietary tags ────────────────────────────────────────────────
// The backend has no dietary fields, so tags are derived from the category
// and the pizza's name/description.
const MEAT_RE = /chicken|beef|pepperoni|tikka|fajita|meat|sausage|bbq|peri|ham|bacon|salami|kebab|tuna|prawn/i;
const SPICY_RE = /jalape|peri|fiery|spicy|chil+i|hot|sriracha|buffalo/i;

export function dietaryTags(pizza, categoryName) {
  const text = `${pizza?.name || ""} ${pizza?.description || ""}`;
  return {
    veg: categoryName === "Garden Fresh" || !MEAT_RE.test(text),
    spicy: categoryName === "Hot & Spicy" || SPICY_RE.test(text),
  };
}

// ── Ratings (from the public reviews endpoint) ──────────────────
const ratingCache = new Map(); // pizzaId -> { avg, count } | null

async function fetchRating(id) {
  if (ratingCache.has(id)) return ratingCache.get(id);
  try {
    const reviews = await reviewApi.forPizza(id, { limit: 100 });
    const count = reviews.length;
    const value = count ? { avg: reviews.reduce((s, r) => s + Number(r.rating || 0), 0) / count, count } : { avg: 0, count: 0 };
    ratingCache.set(id, value);
    return value;
  } catch {
    return null;
  }
}

export function invalidateRating(id) {
  ratingCache.delete(id);
}

/** Returns { [pizzaId]: { avg, count } } and fills in as requests finish. */
export function useRatings(pizzas) {
  const ids = (pizzas || []).map((p) => p.id).join(",");
  const [ratings, setRatings] = useState({});

  useEffect(() => {
    if (!ids) return undefined;
    let alive = true;
    const list = ids.split(",").map(Number);
    Promise.all(list.map(async (id) => [id, await fetchRating(id)])).then((entries) => {
      if (alive) setRatings(Object.fromEntries(entries.filter(([, v]) => v)));
    });
    return () => {
      alive = false;
    };
  }, [ids]);

  return ratings;
}

export const isTopRated = (r) => Boolean(r && r.count >= 2 && r.avg >= 4.5);
