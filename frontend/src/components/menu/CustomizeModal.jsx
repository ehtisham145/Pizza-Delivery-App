import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Check, ChevronDown, Clock, Heart, MessageSquareText, Star } from "lucide-react";
import { reviewApi } from "../../api/endpoints";
import { ESTIMATED_DELIVERY, PIZZA_SIZES } from "../../constants";
import { useFavorites } from "../../context/FavoritesContext";
import { dietaryTags, priceFor } from "../../lib/menu";
import { Modal, QtyStepper, Skeleton, dateTime, money, useLoad } from "../ui";
import PizzaImage from "../PizzaImage";
import { DietBadges } from "./PizzaCard";

function Stars({ value }) {
  const r = Math.round(Number(value) || 0);
  return (
    <span className="inline-flex" aria-label={`${r} out of 5`}>
      {[1, 2, 3, 4, 5].map((n) => (
        <Star key={n} className={`h-3.5 w-3.5 ${n <= r ? "fill-amber-400 text-amber-400" : "text-line"}`} aria-hidden="true" />
      ))}
    </span>
  );
}

function Reviews({ pizzaId }) {
  const { data, error, loading } = useLoad(() => reviewApi.forPizza(pizzaId, { limit: 20 }), [pizzaId]);
  if (loading)
    return (
      <div className="space-y-3 pt-3">
        <Skeleton className="h-14" />
        <Skeleton className="h-14" />
      </div>
    );
  if (error) return <p className="pt-3 text-sm text-brand-600">{error}</p>;
  if (!data?.length) return <p className="pt-3 text-sm text-muted">No reviews yet. Be the first after your order is delivered.</p>;
  return (
    <ul className="m-0 list-none space-y-3 p-0 pt-3">
      {data.map((r) => (
        <li key={r.id} className="rounded-xl bg-surface-2 p-3">
          <div className="flex items-center justify-between gap-2">
            <span className="text-sm font-semibold text-ink">{r.full_name || "Customer"}</span>
            <Stars value={r.rating} />
          </div>
          {r.comment && <p className="mt-1 text-sm text-ink/90">{r.comment}</p>}
          <p className="mt-1 text-xs text-muted">{dateTime(r.created_at)}</p>
        </li>
      ))}
    </ul>
  );
}

export default function CustomizeModal({ pizza, categoryName, rating, onClose, onAdd }) {
  const [sizeId, setSizeId] = useState(PIZZA_SIZES[1].id);
  const [qty, setQty] = useState(1);
  const [busy, setBusy] = useState(false);
  const [showReviews, setShowReviews] = useState(false);
  const { has, toggle } = useFavorites();
  const fav = has(pizza.id);
  const tags = dietaryTags(pizza, categoryName);
  const total = priceFor(pizza, sizeId) * qty;

  const submit = async () => {
    setBusy(true);
    const ok = await onAdd(pizza, { size_id: sizeId, quantity: qty });
    setBusy(false);
    if (ok) onClose();
  };

  return (
    <Modal title={pizza.name} onClose={onClose} size="lg" bare>
      <div className="grid md:grid-cols-[1fr_1.1fr]">
        <div className="relative h-56 overflow-hidden bg-surface-2 sm:h-72 md:h-auto md:min-h-[520px] md:rounded-l-3xl">
          <PizzaImage pizza={pizza} width={1200} sizes="(min-width: 768px) 45vw, 100vw" className="absolute inset-0 h-full w-full" />
          <DietBadges tags={tags} rating={rating} className="absolute bottom-4 left-4" />
        </div>

        <div className="flex flex-col">
          <div className="flex-1 p-5 sm:p-7 md:pt-16">
            <p className="text-xs font-bold uppercase tracking-widest text-brand-ink">{categoryName || "Pizza"}</p>
            <div className="mt-1 flex items-start justify-between gap-3">
              <h2 className="text-2xl font-extrabold sm:text-[1.7rem]">{pizza.name}</h2>
              <button
                type="button"
                onClick={() => toggle(pizza.id)}
                aria-pressed={fav}
                aria-label={fav ? "Remove from favorites" : "Add to favorites"}
                className="icon-btn shrink-0"
              >
                <Heart className={`h-5 w-5 ${fav ? "fill-brand-500 text-brand-500" : ""}`} />
              </button>
            </div>

            <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-muted">
              {rating?.count ? (
                <span className="inline-flex items-center gap-1.5">
                  <Star className="h-4 w-4 fill-amber-400 text-amber-400" aria-hidden="true" />
                  <strong className="text-ink">{rating.avg.toFixed(1)}</strong> ({rating.count} review{rating.count === 1 ? "" : "s"})
                </span>
              ) : (
                <span>No ratings yet</span>
              )}
              <span className="inline-flex items-center gap-1.5">
                <Clock className="h-4 w-4" aria-hidden="true" /> {ESTIMATED_DELIVERY}
              </span>
            </div>

            <p className="mt-4 text-[0.95rem] leading-relaxed text-ink/85">{pizza.description}</p>

            <fieldset className="mt-6">
              <legend className="mb-3 flex w-full items-center justify-between text-sm font-bold text-ink">
                Choose your size <span className="rounded-full bg-surface-2 px-2 py-0.5 text-[0.7rem] font-semibold text-muted">Required</span>
              </legend>
              <div className="grid grid-cols-2 gap-2.5" role="radiogroup">
                {PIZZA_SIZES.map((s) => {
                  const active = s.id === sizeId;
                  return (
                    <button
                      key={s.id}
                      type="button"
                      role="radio"
                      aria-checked={active}
                      onClick={() => setSizeId(s.id)}
                      className={`relative flex flex-col items-start rounded-xl border-2 px-3.5 py-3 text-left transition active:scale-[0.98] ${
                        active ? "border-brand-600 bg-brand-soft" : "border-line hover:border-brand-500/40"
                      }`}
                    >
                      <span className={`text-sm font-bold ${active ? "text-brand-ink" : "text-ink"}`}>{s.size}</span>
                      <span className="text-sm text-muted">{money(priceFor(pizza, s.id))}</span>
                      <AnimatePresence>
                        {active && (
                          <motion.span
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            exit={{ scale: 0 }}
                            className="absolute right-2.5 top-2.5 grid h-5 w-5 place-items-center rounded-full bg-brand-600 text-white"
                          >
                            <Check className="h-3 w-3" strokeWidth={3} />
                          </motion.span>
                        )}
                      </AnimatePresence>
                    </button>
                  );
                })}
              </div>
            </fieldset>

            <div className="mt-6 border-t border-line pt-4">
              <button
                type="button"
                onClick={() => setShowReviews((s) => !s)}
                aria-expanded={showReviews}
                className="flex w-full items-center justify-between text-sm font-bold text-ink"
              >
                <span className="inline-flex items-center gap-2">
                  <MessageSquareText className="h-4 w-4 text-muted" aria-hidden="true" /> Customer reviews
                </span>
                <ChevronDown className={`h-4 w-4 text-muted transition-transform ${showReviews ? "rotate-180" : ""}`} />
              </button>
              {showReviews && <Reviews pizzaId={pizza.id} />}
            </div>
          </div>

          <div className="sticky bottom-0 flex items-center gap-3 border-t border-line bg-surface p-4 pb-safe sm:px-7 md:rounded-br-3xl">
            <QtyStepper value={qty} onChange={setQty} min={1} max={10} />
            <button type="button" onClick={submit} disabled={busy || !pizza.is_available} className="btn btn-primary h-12 flex-1 justify-between text-base">
              <span>{!pizza.is_available ? "Unavailable" : busy ? "Adding…" : "Add to cart"}</span>
              <span className="tabular-nums">{money(total)}</span>
            </button>
          </div>
        </div>
      </div>
    </Modal>
  );
}
