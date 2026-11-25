import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { cartApi, menuApi, reviewApi } from "../api/endpoints";
import { PIZZA_SIZES } from "../constants";
import { Alert, Empty, Message, Modal, PageHeader, Spinner, dateTime, money, useAction, useLoad } from "../components/ui";

function PizzaReviews({ pizza, onClose }) {
  const { data, error, loading } = useLoad(() => reviewApi.forPizza(pizza.id), [pizza.id]);
  return (
    <Modal title={`Reviews · ${pizza.name}`} onClose={onClose}>
      {loading && <Spinner />}
      <Alert type="error">{error}</Alert>
      {data && data.length === 0 && <Empty icon="⭐" title="No reviews yet" />}
      <ul className="review-list">
        {data?.map((r) => (
          <li key={r.id} className="review">
            <div className="review-head">
              <strong>{r.full_name || "Customer"}</strong>
              <span className="stars">{"★".repeat(Math.round(r.rating))}{"☆".repeat(5 - Math.round(r.rating))}</span>
            </div>
            {r.comment && <p>{r.comment}</p>}
            <span className="muted small">{dateTime(r.created_at)}</span>
          </li>
        ))}
      </ul>
    </Modal>
  );
}

function PizzaCard({ pizza, onAdd, onReviews, busy }) {
  const [sizeId, setSizeId] = useState(PIZZA_SIZES[1].id);
  const [qty, setQty] = useState(1);
  const size = PIZZA_SIZES.find((s) => s.id === Number(sizeId));
  const price = Number(pizza.base_price) * (size?.multiplier || 1);

  return (
    <article className={`pizza-card${pizza.is_available ? "" : " unavailable"}`}>
      <div className="pizza-img">
        <img src={pizza.image_url} alt={pizza.name} loading="lazy" onError={(e) => (e.currentTarget.style.display = "none")} />
        {!pizza.is_available && <span className="sold-out">Unavailable</span>}
      </div>
      <div className="pizza-body">
        <div className="pizza-title">
          <h3>{pizza.name}</h3>
          <span className="price">{money(price)}</span>
        </div>
        <p className="muted pizza-desc">{pizza.description}</p>

        <div className="pizza-controls">
          <select value={sizeId} onChange={(e) => setSizeId(e.target.value)} aria-label="Size">
            {PIZZA_SIZES.map((s) => (
              <option key={s.id} value={s.id}>
                {s.size} · {money(Number(pizza.base_price) * s.multiplier)}
              </option>
            ))}
          </select>
          <input
            type="number"
            min={1}
            max={10}
            value={qty}
            onChange={(e) => setQty(Math.max(1, Math.min(10, Number(e.target.value) || 1)))}
            aria-label="Quantity"
          />
        </div>

        <div className="pizza-actions">
          <button className="btn btn-link" onClick={() => onReviews(pizza)}>
            Reviews
          </button>
          <button
            className="btn btn-primary"
            disabled={!pizza.is_available || busy}
            onClick={() => onAdd(pizza, { size_id: Number(sizeId), quantity: qty })}
          >
            Add to cart
          </button>
        </div>
      </div>
    </article>
  );
}

export default function Menu() {
  const pizzas = useLoad(() => menuApi.pizzas());
  const categories = useLoad(() => menuApi.categories().catch(() => []));
  const { busy, message, setMessage, run } = useAction();
  const [category, setCategory] = useState("all");
  const [search, setSearch] = useState("");
  const [reviewsFor, setReviewsFor] = useState(null);

  const visible = useMemo(() => {
    const q = search.trim().toLowerCase();
    return (pizzas.data || []).filter(
      (p) =>
        (category === "all" || String(p.category_id) === category) &&
        (!q || p.name.toLowerCase().includes(q) || p.description.toLowerCase().includes(q))
    );
  }, [pizzas.data, category, search]);

  const add = (pizza, opts) =>
    run(() => cartApi.add(pizza.id, opts), `${opts.quantity} × ${pizza.name} added to your cart.`);

  return (
    <>
      <PageHeader
        title="Our menu"
        subtitle="Pick a size, choose a quantity and add it to your cart."
        actions={
          <Link to="/cart" className="btn btn-secondary">
            Go to cart →
          </Link>
        }
      />

      <Message message={message} onClose={() => setMessage(null)} />

      <div className="toolbar">
        <input className="search" placeholder="Search pizzas…" value={search} onChange={(e) => setSearch(e.target.value)} />
        <div className="chips">
          <button className={`chip${category === "all" ? " active" : ""}`} onClick={() => setCategory("all")}>
            All
          </button>
          {(categories.data || []).map((c) => (
            <button
              key={c.id}
              className={`chip${category === String(c.id) ? " active" : ""}`}
              onClick={() => setCategory(String(c.id))}
            >
              {c.name}
            </button>
          ))}
        </div>
      </div>

      {pizzas.loading && <Spinner label="Loading menu…" />}
      <Alert type="error">{pizzas.error}</Alert>
      {!pizzas.loading && !pizzas.error && visible.length === 0 && (
        <Empty title="No pizzas found">Try another category or search term.</Empty>
      )}

      <div className="pizza-grid">
        {visible.map((p) => (
          <PizzaCard key={p.id} pizza={p} busy={busy} onAdd={add} onReviews={setReviewsFor} />
        ))}
      </div>

      {reviewsFor && <PizzaReviews pizza={reviewsFor} onClose={() => setReviewsFor(null)} />}
    </>
  );
}
