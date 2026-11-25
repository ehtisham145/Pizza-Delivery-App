import { useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { motion } from "framer-motion";
import { Clock, Flame, Heart, Leaf, SearchX, SlidersHorizontal } from "lucide-react";
import { menuApi } from "../api/endpoints";
import { ESTIMATED_DELIVERY, PIZZA_SIZES } from "../constants";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";
import { useFavorites } from "../context/FavoritesContext";
import { useToast } from "../context/ToastContext";
import { HERO_IMAGES, categoryImage } from "../lib/images";
import { dietaryTags, priceFor, useRatings } from "../lib/menu";
import { Alert, Empty, PageHeader, money, useLoad } from "../components/ui";
import PizzaCard, { PizzaCardSkeleton } from "../components/menu/PizzaCard";
import CustomizeModal from "../components/menu/CustomizeModal";

const SORTS = [
  { key: "recommended", label: "Recommended" },
  { key: "price-asc", label: "Price: low to high" },
  { key: "price-desc", label: "Price: high to low" },
  { key: "rating", label: "Top rated" },
];

const gridVariants = { hidden: {}, show: { transition: { staggerChildren: 0.045 } } };

function greeting() {
  const h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 17) return "Good afternoon";
  return "Good evening";
}

function Hero({ name }) {
  return (
    <section className="relative mb-8 overflow-hidden rounded-3xl bg-gray-900 text-white shadow-lift">
      <img src={HERO_IMAGES.menuBanner} alt="" className="absolute inset-0 h-full w-full object-cover opacity-70" />
      <div className="absolute inset-0 bg-gradient-to-r from-black/85 via-black/55 to-transparent" aria-hidden="true" />
      <div className="relative max-w-xl px-6 py-9 sm:px-10 sm:py-12">
        <p className="text-sm font-semibold text-amber-300">
          {greeting()}
          {name ? `, ${name}` : ""} 👋
        </p>
        <h1 className="mt-2 text-3xl font-extrabold leading-tight text-white sm:text-4xl">What are you craving today?</h1>
        <p className="mt-3 max-w-md text-[0.95rem] text-white/80">Stone-baked to order with real mozzarella, and at your door while it's still bubbling.</p>
        <span className="mt-5 inline-flex items-center gap-2 rounded-full bg-white/15 px-3.5 py-1.5 text-sm font-semibold backdrop-blur">
          <Clock className="h-4 w-4 text-amber-300" aria-hidden="true" /> Delivery in {ESTIMATED_DELIVERY}
        </span>
      </div>
    </section>
  );
}

function CategoryPill({ active, onClick, image, label, count }) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={active}
      className={`relative flex shrink-0 items-center gap-2.5 rounded-full py-1.5 pl-1.5 pr-4 text-sm font-semibold transition active:scale-95 ${
        active ? "text-white" : "border border-line bg-surface text-ink hover:border-brand-500/40"
      }`}
    >
      {active && (
        <motion.span
          layoutId="category-pill"
          className="absolute inset-0 rounded-full bg-brand-600 shadow-brand"
          transition={{ type: "spring", stiffness: 420, damping: 34 }}
        />
      )}
      <img src={image} alt="" loading="lazy" className="relative h-9 w-9 rounded-full object-cover ring-2 ring-white/70" />
      <span className="relative whitespace-nowrap">{label}</span>
      <span className={`relative rounded-full px-1.5 text-xs ${active ? "bg-white/20" : "bg-surface-2 text-muted"}`}>{count}</span>
    </button>
  );
}

function FilterToggle({ active, onClick, icon: Icon, children }) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={active}
      className={`inline-flex h-9 items-center gap-1.5 rounded-full border px-3 text-sm font-medium transition active:scale-95 ${
        active ? "border-ink bg-ink text-surface" : "border-line bg-surface text-ink hover:border-ink/30"
      }`}
    >
      <Icon className="h-4 w-4" aria-hidden="true" /> {children}
    </button>
  );
}

export default function Menu({ favoritesOnly = false }) {
  const { user } = useAuth();
  const cart = useCart();
  const { toast } = useToast();
  const favorites = useFavorites();
  const pizzas = useLoad(() => menuApi.pizzas());
  const categories = useLoad(() => menuApi.categories().catch(() => []));
  const ratings = useRatings(pizzas.data);
  const [params, setParams] = useSearchParams();
  const [customizing, setCustomizing] = useState(null);
  const [quickAdding, setQuickAdding] = useState(null);

  const q = params.get("q") || "";
  const category = params.get("category") || "all";
  const sort = params.get("sort") || "recommended";
  const vegOnly = params.get("veg") === "1";
  const spicyOnly = params.get("spicy") === "1";

  const setParam = (key, value) => {
    const next = new URLSearchParams(params);
    if (value) next.set(key, value);
    else next.delete(key);
    setParams(next, { replace: true });
  };

  const catName = useMemo(() => {
    const map = new Map((categories.data || []).map((c) => [c.id, c.name]));
    return (id) => map.get(id);
  }, [categories.data]);

  // Everything except the category filter — used for the pill counts.
  const base = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return (pizzas.data || []).filter((p) => {
      if (favoritesOnly && !favorites.has(p.id)) return false;
      if (needle && !`${p.name} ${p.description}`.toLowerCase().includes(needle)) return false;
      const tags = dietaryTags(p, catName(p.category_id));
      if (vegOnly && !tags.veg) return false;
      if (spicyOnly && !tags.spicy) return false;
      return true;
    });
  }, [pizzas.data, q, vegOnly, spicyOnly, favoritesOnly, favorites, catName]);

  const visible = useMemo(() => {
    const list = base.filter((p) => category === "all" || String(p.category_id) === category);
    const byPrice = (p) => Number(p.base_price);
    const byRating = (p) => ratings[p.id]?.avg || 0;
    const sorted = [...list];
    if (sort === "price-asc") sorted.sort((a, b) => byPrice(a) - byPrice(b));
    if (sort === "price-desc") sorted.sort((a, b) => byPrice(b) - byPrice(a));
    if (sort === "rating") sorted.sort((a, b) => byRating(b) - byRating(a));
    // Available pizzas first in every sort.
    return sorted.sort((a, b) => Number(b.is_available) - Number(a.is_available));
  }, [base, category, sort, ratings]);

  const add = async (pizza, opts) => {
    try {
      await cart.add(pizza, opts);
      const size = PIZZA_SIZES.find((s) => s.id === opts.size_id)?.size;
      toast({
        title: `${opts.quantity} × ${pizza.name} added`,
        description: `${size} · ${money(priceFor(pizza, opts.size_id) * opts.quantity)}`,
        action: { label: "View cart", onClick: cart.openDrawer },
      });
      return true;
    } catch (err) {
      toast({ type: "error", title: "Couldn't add to cart", description: err.message });
      return false;
    }
  };

  const quickAdd = async (pizza) => {
    setQuickAdding(pizza.id);
    await add(pizza, { size_id: PIZZA_SIZES[1].id, quantity: 1 });
    setQuickAdding(null);
  };

  const filterKey = `${category}|${sort}|${vegOnly}|${spicyOnly}|${q}`;
  const firstName = (user?.full_name || "").split(" ")[0];
  const showHero = !favoritesOnly && !q;
  const loading = pizzas.loading;

  return (
    <>
      {favoritesOnly ? (
        <PageHeader eyebrow="Saved for later" title="Your favorites" subtitle="Tap the heart on any pizza to keep it here." />
      ) : (
        showHero && <Hero name={firstName} />
      )}

      {q && !favoritesOnly && (
        <PageHeader
          eyebrow="Search"
          title={`Results for “${q}”`}
          subtitle={`${visible.length} pizza${visible.length === 1 ? "" : "s"} found`}
          actions={
            <button type="button" className="btn btn-secondary btn-sm" onClick={() => setParam("q", "")}>
              Clear search
            </button>
          }
        />
      )}

      {/* Category rail */}
      <div className="-mx-4 mb-4 sm:-mx-6 lg:-mx-8">
        <div className="no-scrollbar flex gap-2.5 overflow-x-auto px-4 pb-2 sm:px-6 lg:px-8" role="toolbar" aria-label="Categories">
          {loading && !categories.data
            ? Array.from({ length: 6 }, (_, i) => <div key={i} className="skeleton h-12 w-40 shrink-0 rounded-full" />)
            : (
              <>
                <CategoryPill active={category === "all"} onClick={() => setParam("category", "")} image={HERO_IMAGES.allCategory} label="All pizzas" count={base.length} />
                {(categories.data || [])
                  .map((c) => ({ ...c, count: base.filter((p) => p.category_id === c.id).length }))
                  // Hide empty categories so they never lead to a dead end (unless already selected).
                  .filter((c) => c.count > 0 || category === String(c.id))
                  .map((c) => (
                    <CategoryPill
                      key={c.id}
                      active={category === String(c.id)}
                      onClick={() => setParam("category", String(c.id))}
                      image={categoryImage(c.name)}
                      label={c.name}
                      count={c.count}
                    />
                  ))}
              </>
            )}
        </div>
      </div>

      {/* Filters & sort */}
      <div className="mb-6 flex flex-wrap items-center gap-2">
        <FilterToggle active={vegOnly} onClick={() => setParam("veg", vegOnly ? "" : "1")} icon={Leaf}>
          Veg
        </FilterToggle>
        <FilterToggle active={spicyOnly} onClick={() => setParam("spicy", spicyOnly ? "" : "1")} icon={Flame}>
          Spicy
        </FilterToggle>
        <div className="ml-auto flex items-center gap-2">
          <SlidersHorizontal className="hidden h-4 w-4 text-muted sm:block" aria-hidden="true" />
          <select
            value={sort}
            onChange={(e) => setParam("sort", e.target.value === "recommended" ? "" : e.target.value)}
            aria-label="Sort pizzas"
            className="h-9 min-h-0 w-auto rounded-full py-0 pl-3.5 text-sm font-medium"
          >
            {SORTS.map((s) => (
              <option key={s.key} value={s.key}>
                {s.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <Alert type="error">{pizzas.error}</Alert>

      {loading ? (
        <div className="grid grid-cols-[repeat(auto-fill,minmax(250px,1fr))] gap-5" role="status" aria-label="Loading menu">
          {Array.from({ length: 8 }, (_, i) => (
            <PizzaCardSkeleton key={i} />
          ))}
        </div>
      ) : (
        !pizzas.error &&
        (visible.length === 0 ? (
          favoritesOnly && favorites.ids.length === 0 ? (
            <Empty
              icon={Heart}
              title="No favorites yet"
              action={
                <Link to="/menu" className="btn btn-primary">
                  Explore the menu
                </Link>
              }
            >
              Tap the heart on any pizza and it will be saved here for quick reordering.
            </Empty>
          ) : (
            <Empty
              icon={SearchX}
              title="No pizzas match"
              action={
                <button type="button" className="btn btn-secondary" onClick={() => setParams({}, { replace: true })}>
                  Reset filters
                </button>
              }
            >
              Try another category, remove a filter, or search for something else.
            </Empty>
          )
        ) : (
          <motion.div
            key={filterKey}
            variants={gridVariants}
            initial="hidden"
            animate="show"
            className="grid grid-cols-[repeat(auto-fill,minmax(250px,1fr))] gap-5"
          >
            {visible.map((p) => (
              <PizzaCard
                key={p.id}
                pizza={p}
                categoryName={catName(p.category_id)}
                rating={ratings[p.id]}
                onCustomize={setCustomizing}
                onQuickAdd={quickAdd}
                adding={quickAdding === p.id}
              />
            ))}
          </motion.div>
        ))
      )}

      {customizing && (
        <CustomizeModal
          pizza={customizing}
          categoryName={catName(customizing.category_id)}
          rating={ratings[customizing.id]}
          onClose={() => setCustomizing(null)}
          onAdd={add}
        />
      )}
    </>
  );
}
