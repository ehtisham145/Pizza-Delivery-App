import { motion } from "framer-motion";
import { Award, Clock, Flame, Heart, Leaf, Plus, Star } from "lucide-react";
import { ESTIMATED_DELIVERY, PIZZA_SIZES } from "../../constants";
import { useFavorites } from "../../context/FavoritesContext";
import { dietaryTags, isTopRated, priceFor } from "../../lib/menu";
import { money } from "../ui";
import PizzaImage from "../PizzaImage";

export function DietBadges({ tags, rating, className = "" }) {
  return (
    <div className={`flex flex-wrap gap-1.5 ${className}`}>
      {isTopRated(rating) && (
        <span className="inline-flex items-center gap-1 rounded-full bg-amber-400 px-2 py-0.5 text-[0.7rem] font-bold text-ink shadow-sm">
          <Award className="h-3 w-3" aria-hidden="true" /> Top rated
        </span>
      )}
      {tags.veg && (
        <span className="inline-flex items-center gap-1 rounded-full bg-emerald-600 px-2 py-0.5 text-[0.7rem] font-bold text-white shadow-sm">
          <Leaf className="h-3 w-3" aria-hidden="true" /> Veg
        </span>
      )}
      {tags.spicy && (
        <span className="inline-flex items-center gap-1 rounded-full bg-brand-600 px-2 py-0.5 text-[0.7rem] font-bold text-white shadow-sm">
          <Flame className="h-3 w-3" aria-hidden="true" /> Spicy
        </span>
      )}
    </div>
  );
}

export function RatingChip({ rating, className = "" }) {
  if (!rating) return null;
  if (!rating.count) {
    return <span className={`rounded-full bg-black/55 px-2 py-0.5 text-[0.7rem] font-semibold text-white backdrop-blur ${className}`}>New</span>;
  }
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full bg-black/55 px-2 py-0.5 text-[0.75rem] font-semibold text-white backdrop-blur ${className}`}
      aria-label={`Rated ${rating.avg.toFixed(1)} out of 5 from ${rating.count} reviews`}
    >
      <Star className="h-3 w-3 fill-amber-400 text-amber-400" aria-hidden="true" />
      {rating.avg.toFixed(1)}
      <span className="font-normal opacity-80">({rating.count})</span>
    </span>
  );
}

export const cardVariants = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.3, ease: "easeOut" } },
};

export default function PizzaCard({ pizza, categoryName, rating, onCustomize, onQuickAdd, adding }) {
  const { has, toggle } = useFavorites();
  const fav = has(pizza.id);
  const tags = dietaryTags(pizza, categoryName);
  const unavailable = !pizza.is_available;
  const fromPrice = priceFor(pizza, PIZZA_SIZES[0].id);

  return (
    <motion.article
      variants={cardVariants}
      layout="position"
      className={`group relative flex flex-col overflow-hidden rounded-2xl border border-line bg-surface shadow-soft transition duration-300 hover:-translate-y-1 hover:shadow-lift ${
        unavailable ? "opacity-70" : ""
      }`}
    >
      <button
        type="button"
        onClick={() => onCustomize(pizza)}
        className="relative block aspect-[4/3] overflow-hidden bg-surface-2"
        aria-label={`View ${pizza.name}`}
      >
        <PizzaImage pizza={pizza} className="h-full w-full transition-transform duration-500 ease-out group-hover:scale-[1.07]" />
        <span className="pointer-events-none absolute inset-0 bg-gradient-to-t from-black/45 via-transparent to-transparent" aria-hidden="true" />
        <DietBadges tags={tags} rating={rating} className="absolute left-3 top-3" />
        <RatingChip rating={rating} className="absolute bottom-3 left-3" />
        {unavailable && (
          <span className="absolute inset-0 grid place-items-center bg-black/45 text-sm font-bold uppercase tracking-wider text-white">
            Currently unavailable
          </span>
        )}
      </button>

      <motion.button
        type="button"
        whileTap={{ scale: 0.8 }}
        onClick={() => toggle(pizza.id)}
        aria-pressed={fav}
        aria-label={fav ? `Remove ${pizza.name} from favorites` : `Add ${pizza.name} to favorites`}
        className="absolute right-3 top-3 grid h-9 w-9 place-items-center rounded-full bg-white/90 shadow-soft backdrop-blur transition hover:scale-110"
      >
        <Heart className={`h-[18px] w-[18px] transition-colors ${fav ? "fill-brand-500 text-brand-500" : "text-gray-700"}`} />
      </motion.button>

      <div className="flex flex-1 flex-col p-4">
        <div className="mb-1 flex items-center gap-2 text-xs text-muted">
          <span className="truncate">{categoryName || "Pizza"}</span>
          <span aria-hidden="true">·</span>
          <span className="inline-flex shrink-0 items-center gap-1">
            <Clock className="h-3.5 w-3.5" aria-hidden="true" /> {ESTIMATED_DELIVERY}
          </span>
        </div>
        <h3 className="text-[1.05rem] leading-snug">
          <button type="button" onClick={() => onCustomize(pizza)} className="text-left hover:text-brand-ink">
            {pizza.name}
          </button>
        </h3>
        <p className="mt-1 line-clamp-2 flex-1 text-sm text-muted">{pizza.description}</p>

        <div className="mt-4 flex items-end justify-between gap-2">
          <div className="leading-tight">
            <span className="block text-[0.7rem] font-medium uppercase tracking-wide text-muted">From</span>
            <span className="font-display text-lg font-extrabold text-ink">{money(fromPrice)}</span>
          </div>
          <div className="flex items-center gap-2">
            <button type="button" className="btn btn-secondary btn-sm" onClick={() => onCustomize(pizza)} disabled={unavailable}>
              Customize
            </button>
            <motion.button
              type="button"
              whileTap={{ scale: 0.85 }}
              onClick={() => onQuickAdd(pizza)}
              disabled={unavailable || adding}
              className="grid h-9 w-9 place-items-center rounded-full bg-brand-600 text-white shadow-brand transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-50 disabled:shadow-none"
              aria-label={`Quick add a Medium ${pizza.name} to cart`}
              title="Quick add (Medium)"
            >
              {adding ? (
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" />
              ) : (
                <Plus className="h-5 w-5" strokeWidth={2.6} />
              )}
            </motion.button>
          </div>
        </div>
      </div>
    </motion.article>
  );
}

export function PizzaCardSkeleton() {
  return (
    <div className="overflow-hidden rounded-2xl border border-line bg-surface shadow-soft" aria-hidden="true">
      <div className="skeleton aspect-[4/3] rounded-none" />
      <div className="space-y-2.5 p-4">
        <div className="skeleton h-3 w-1/3" />
        <div className="skeleton h-5 w-2/3" />
        <div className="skeleton h-3 w-full" />
        <div className="skeleton h-3 w-4/5" />
        <div className="flex items-end justify-between pt-3">
          <div className="skeleton h-6 w-20" />
          <div className="skeleton h-9 w-28 rounded-full" />
        </div>
      </div>
    </div>
  );
}
