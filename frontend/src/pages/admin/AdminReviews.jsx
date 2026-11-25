import { useState } from "react";
import { menuApi, reviewApi } from "../../api/endpoints";
import { useAuth } from "../../context/AuthContext";
import { Stars } from "../MyReviews";
import { Alert, Empty, Message, PageHeader, Spinner, dateTime, shortId, useAction, useLoad } from "../../components/ui";

export default function AdminReviews() {
  const { isAdmin } = useAuth();
  const pizzas = useLoad(() => menuApi.pizzas().catch(() => []));
  // "" = all reviews (admin only), otherwise a pizza id (public endpoint)
  const [pizzaId, setPizzaId] = useState(isAdmin ? "" : null);
  const list = useLoad(
    () => (pizzaId ? reviewApi.forPizza(pizzaId, { limit: 100 }) : isAdmin && pizzaId === "" ? reviewApi.all({ limit: 100 }) : Promise.resolve([])),
    [pizzaId, isAdmin]
  );
  const { busy, message, setMessage, run } = useAction();
  const reviews = list.data || [];

  const remove = async (r) => {
    if (!window.confirm("Delete this review?")) return;
    await run(() => reviewApi.remove(r.id), "Review deleted.");
    list.reload();
  };

  return (
    <>
      <PageHeader title="Reviews" subtitle="Moderate customer reviews." />
      <Message message={message} onClose={() => setMessage(null)} />

      <div className="toolbar">
        <select value={pizzaId ?? ""} onChange={(e) => setPizzaId(e.target.value)} aria-label="Filter by pizza">
          {isAdmin ? <option value="">All reviews</option> : <option value="">Choose a pizza…</option>}
          {(pizzas.data || []).map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
      </div>

      {list.loading && <Spinner />}
      <Alert type="error">{list.error}</Alert>
      {!list.loading && !list.error && reviews.length === 0 && <Empty icon="⭐" title="No reviews found" />}

      <ul className="review-list">
        {reviews.map((r) => (
          <li key={r.id} className="card review">
            <div className="review-head">
              <strong>
                {r.full_name || "Customer"} · Order #{shortId(r.order_id)}
              </strong>
              <Stars rating={r.rating} />
            </div>
            {r.comment && <p>{r.comment}</p>}
            <div className="review-foot">
              <span className="muted small">{dateTime(r.created_at)}</span>
              <button className="btn btn-ghost btn-sm danger" onClick={() => remove(r)} disabled={busy}>
                Delete
              </button>
            </div>
          </li>
        ))}
      </ul>
    </>
  );
}
