import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { orderApi, paymentApi, reviewApi } from "../api/endpoints";
import { PAYMENT_METHODS } from "../constants";
import {
  Alert,
  Empty,
  Field,
  Message,
  Modal,
  PageHeader,
  Spinner,
  StatusBadge,
  dateTime,
  money,
  shortId,
  useAction,
  useLoad,
} from "../components/ui";

export function OrderItems({ items }) {
  return (
    <table className="table compact">
      <thead>
        <tr>
          <th>Pizza</th>
          <th>Size</th>
          <th className="num">Qty</th>
          <th className="num">Unit</th>
          <th className="num">Total</th>
        </tr>
      </thead>
      <tbody>
        {(items || []).map((i, idx) => (
          <tr key={idx}>
            <td>{i.pizza_name}</td>
            <td>{i.size_name}</td>
            <td className="num">{i.quantity}</td>
            <td className="num">{money(i.unit_price)}</td>
            <td className="num">{money(i.sub_total)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function PaymentModal({ order, onClose, onDone }) {
  const existing = useLoad(() => paymentApi.forOrder(order.id).catch((e) => (e.status === 404 ? null : Promise.reject(e))), [order.id]);
  const [method, setMethod] = useState(PAYMENT_METHODS[1]);
  const { busy, message, run } = useAction();

  const pay = async () => {
    await run(() => paymentApi.create(order.id, method), "Payment created.");
    existing.reload();
    onDone?.();
  };

  const p = existing.data;
  return (
    <Modal title={`Payment · Order ${shortId(order.id)}`} onClose={onClose}>
      {existing.loading && <Spinner />}
      <Alert type="error">{existing.error}</Alert>
      <Message message={message} />
      {p ? (
        <dl className="details">
          <dt>Amount</dt>
          <dd>{money(p.amount)}</dd>
          <dt>Method</dt>
          <dd>{p.method}</dd>
          <dt>Status</dt>
          <dd>
            <StatusBadge status={p.status} />
          </dd>
          <dt>Created</dt>
          <dd>{dateTime(p.created_at)}</dd>
          {p.paid_at && (
            <>
              <dt>Paid at</dt>
              <dd>{dateTime(p.paid_at)}</dd>
            </>
          )}
        </dl>
      ) : (
        !existing.loading && (
          <>
            <p>
              Amount due: <strong>{money(order.total_price)}</strong>
            </p>
            <Field label="Payment method">
              <select value={method} onChange={(e) => setMethod(e.target.value)}>
                {PAYMENT_METHODS.map((m) => (
                  <option key={m}>{m}</option>
                ))}
              </select>
            </Field>
            <button className="btn btn-primary btn-block" onClick={pay} disabled={busy}>
              {busy ? "Processing…" : "Confirm payment"}
            </button>
          </>
        )
      )}
    </Modal>
  );
}

function ReviewModal({ order, onClose }) {
  const items = order.order_item || [];
  const [form, setForm] = useState({ pizza_id: items[0]?.pizza_id || "", rating: 5, comment: "" });
  const { busy, message, run } = useAction();

  const submit = async (e) => {
    e.preventDefault();
    const res = await run(
      () =>
        reviewApi.submit({
          order_id: order.id,
          pizza_id: Number(form.pizza_id),
          rating: Number(form.rating),
          comment: form.comment.trim() || null,
        }),
      "Thanks for your review!"
    );
    if (res) setTimeout(onClose, 900);
  };

  return (
    <Modal title="Rate your order" onClose={onClose}>
      <form onSubmit={submit}>
        <Message message={message} />
        <Field label="Pizza">
          <select value={form.pizza_id} onChange={(e) => setForm({ ...form, pizza_id: e.target.value })}>
            {items.map((i) => (
              <option key={`${i.pizza_id}-${i.size_name}`} value={i.pizza_id}>
                {i.pizza_name} ({i.size_name})
              </option>
            ))}
          </select>
        </Field>
        <Field label="Rating">
          <div className="star-input" role="radiogroup" aria-label="Rating">
            {[1, 2, 3, 4, 5].map((n) => (
              <button
                type="button"
                key={n}
                className={n <= form.rating ? "on" : ""}
                onClick={() => setForm({ ...form, rating: n })}
                aria-label={`${n} star${n > 1 ? "s" : ""}`}
                aria-checked={form.rating === n}
                role="radio"
              >
                ★
              </button>
            ))}
          </div>
        </Field>
        <Field label="Comment (optional)">
          <textarea rows={3} maxLength={1000} value={form.comment} onChange={(e) => setForm({ ...form, comment: e.target.value })} />
        </Field>
        <button className="btn btn-primary btn-block" disabled={busy || !form.pizza_id}>
          Submit review
        </button>
      </form>
    </Modal>
  );
}

function OrderCard({ order, onCancel, onPay, onReview, busy }) {
  const [open, setOpen] = useState(false);
  const count = (order.order_item || []).reduce((n, i) => n + i.quantity, 0);

  return (
    <article className="card order-card">
      <button className="order-summary" onClick={() => setOpen((o) => !o)} aria-expanded={open}>
        <div>
          <strong>Order #{shortId(order.id)}</strong>
          <span className="muted small">
            {dateTime(order.created_at)} · {count} item{count === 1 ? "" : "s"}
          </span>
        </div>
        <div className="order-summary-right">
          <StatusBadge status={order.status} />
          <strong>{money(order.total_price)}</strong>
          <span className="chevron">{open ? "▴" : "▾"}</span>
        </div>
      </button>

      {open && (
        <div className="order-detail">
          <OrderItems items={order.order_item} />
          {order.notes && <p className="muted">Notes: {order.notes}</p>}
          <p className="muted small">Full order ID: {order.id}</p>
          <div className="row-actions">
            {order.status === "Pending" && (
              <button className="btn btn-danger btn-sm" onClick={() => onCancel(order)} disabled={busy}>
                Cancel order
              </button>
            )}
            {order.status !== "Cancelled" && (
              <button className="btn btn-secondary btn-sm" onClick={() => onPay(order)}>
                Payment
              </button>
            )}
            {order.status === "Delivered" && (
              <button className="btn btn-secondary btn-sm" onClick={() => onReview(order)}>
                Write a review
              </button>
            )}
          </div>
        </div>
      )}
    </article>
  );
}

export default function Orders() {
  const location = useLocation();
  const history = useLoad(() => orderApi.history());
  const { busy, message, setMessage, run } = useAction();
  const [payFor, setPayFor] = useState(null);
  const [reviewFor, setReviewFor] = useState(null);
  const [lookupId, setLookupId] = useState("");
  const [lookup, setLookup] = useState(null);

  const orders = [...(history.data?.order || [])].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

  const cancel = async (order) => {
    if (!window.confirm("Cancel this order?")) return;
    await run(() => orderApi.cancel(order.id), "Order cancelled.");
    history.reload();
  };

  const find = async (e) => {
    e.preventDefault();
    if (!lookupId.trim()) return;
    const res = await run(() => orderApi.mine(lookupId.trim()));
    setLookup(res || null);
  };

  return (
    <>
      <PageHeader title="My orders" subtitle="Track, pay for and review your orders." />

      {location.state?.placed && (
        <Alert type="success">Order #{shortId(location.state.placed)} placed! Open it below to pay.</Alert>
      )}
      <Message message={message} onClose={() => setMessage(null)} />

      <form className="toolbar" onSubmit={find}>
        <input className="search" placeholder="Find an order by its full ID…" value={lookupId} onChange={(e) => setLookupId(e.target.value)} />
        <button className="btn btn-secondary" disabled={busy}>
          Find order
        </button>
      </form>
      {lookup && (
        <div className="stack">
          <h3>Search result</h3>
          <OrderCard order={lookup} busy={busy} onCancel={cancel} onPay={setPayFor} onReview={setReviewFor} />
        </div>
      )}

      {history.loading && <Spinner />}
      <Alert type="error">{history.error}</Alert>
      {!history.loading && !history.error && orders.length === 0 && (
        <Empty icon="📦" title="No orders yet">
          <Link to="/menu">Order your first pizza</Link>.
        </Empty>
      )}

      <div className="stack">
        {orders.map((o) => (
          <OrderCard key={o.id} order={o} busy={busy} onCancel={cancel} onPay={setPayFor} onReview={setReviewFor} />
        ))}
      </div>

      {payFor && <PaymentModal order={payFor} onClose={() => setPayFor(null)} />}
      {reviewFor && <ReviewModal order={reviewFor} onClose={() => setReviewFor(null)} />}
    </>
  );
}
