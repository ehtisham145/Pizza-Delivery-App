import { useState } from "react";
import { Link, useLocation, useSearchParams } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { Bike, Check, ChefHat, ChevronDown, CreditCard, PackageCheck, ReceiptText, Search, Star, XCircle } from "lucide-react";
import { orderApi, paymentApi, reviewApi } from "../api/endpoints";
import { PAYMENT_METHODS } from "../constants";
import PizzaImage from "../components/PizzaImage";
import {
  Alert,
  Empty,
  Field,
  ListSkeleton,
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
    <div className="overflow-x-auto rounded-xl border border-line">
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
              <td className="font-medium">{i.pizza_name}</td>
              <td>{i.size_name}</td>
              <td className="num">{i.quantity}</td>
              <td className="num">{money(i.unit_price)}</td>
              <td className="num">{money(i.sub_total)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// The backend only knows Pending → Delivered (or Cancelled), so the middle
// step covers everything between placing and delivery.
const STEPS = [
  { key: "placed", label: "Order placed", icon: ReceiptText },
  { key: "on-the-way", label: "Preparing & on the way", icon: ChefHat },
  { key: "delivered", label: "Delivered", icon: PackageCheck },
];

export function OrderTracker({ order }) {
  if (order.status === "Cancelled") {
    return (
      <div className="flex items-center gap-3 rounded-xl bg-brand-soft p-4 text-sm text-brand-ink">
        <XCircle className="h-5 w-5 shrink-0" aria-hidden="true" />
        This order was cancelled.
      </div>
    );
  }
  const current = order.status === "Delivered" ? 3 : 1; // index of the step in progress (3 = all done)

  return (
    <ol className="relative grid grid-cols-3 gap-2" aria-label="Order progress">
      {STEPS.map((s, i) => {
        const done = i < current;
        const active = i === current;
        const Icon = active ? Bike : done ? Check : s.icon;
        return (
          <li key={s.key} className="relative flex flex-col items-center text-center">
            {i > 0 && (
              <span className="absolute right-1/2 top-5 -z-0 h-1 w-full -translate-y-1/2 overflow-hidden rounded-full bg-line" aria-hidden="true">
                <motion.span
                  className="block h-full bg-brand-600"
                  initial={{ width: 0 }}
                  animate={{ width: i <= current ? (i < current ? "100%" : "50%") : 0 }}
                  transition={{ duration: 0.6, delay: 0.15 * i }}
                />
              </span>
            )}
            <span
              className={`relative z-10 grid h-10 w-10 place-items-center rounded-full border-2 transition-colors ${
                done ? "border-brand-600 bg-brand-600 text-white" : active ? "border-brand-600 bg-surface text-brand-600" : "border-line bg-surface text-muted"
              }`}
            >
              {active && <span className="absolute inset-0 animate-ping rounded-full bg-brand-500/25" aria-hidden="true" />}
              <Icon className="h-[18px] w-[18px]" aria-hidden="true" />
            </span>
            <span className={`mt-2 text-xs font-semibold ${done || active ? "text-ink" : "text-muted"}`}>{s.label}</span>
            {i === 0 && <span className="text-[0.7rem] text-muted">{new Date(order.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>}
            <span className="sr-only">{done ? "(done)" : active ? "(in progress)" : "(upcoming)"}</span>
          </li>
        );
      })}
    </ol>
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
    <Modal title={`Payment · Order #${shortId(order.id)}`} onClose={onClose}>
      {existing.loading && <Spinner />}
      <Alert type="error">{existing.error}</Alert>
      <Message message={message} />
      {p ? (
        <dl className="details">
          <dt>Amount</dt>
          <dd className="font-semibold">{money(p.amount)}</dd>
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
            <div className="mb-5 flex items-baseline justify-between rounded-xl bg-surface-2 p-4">
              <span className="text-sm text-muted">Amount due</span>
              <span className="font-display text-2xl font-extrabold">{money(order.total_price)}</span>
            </div>
            <p className="field-label mb-2">Payment method</p>
            <div className="mb-5 grid grid-cols-2 gap-3" role="radiogroup" aria-label="Payment method">
              {PAYMENT_METHODS.map((m) => {
                const active = m === method;
                return (
                  <button
                    key={m}
                    type="button"
                    role="radio"
                    aria-checked={active}
                    onClick={() => setMethod(m)}
                    className={`flex flex-col items-start gap-2 rounded-xl border-2 p-3.5 text-left text-sm font-semibold transition ${
                      active ? "border-brand-600 bg-brand-soft text-brand-ink" : "border-line text-ink hover:border-brand-500/40"
                    }`}
                  >
                    {m === "Card" ? <CreditCard className="h-5 w-5" /> : <Bike className="h-5 w-5" />}
                    {m}
                  </button>
                );
              })}
            </div>
            <button className="btn btn-primary btn-block h-12" onClick={pay} disabled={busy}>
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
                <Star className={`h-8 w-8 ${n <= form.rating ? "fill-current" : ""}`} />
              </button>
            ))}
          </div>
        </Field>
        <Field label="Comment (optional)">
          <textarea rows={3} maxLength={1000} value={form.comment} onChange={(e) => setForm({ ...form, comment: e.target.value })} placeholder="What did you love?" />
        </Field>
        <button className="btn btn-primary btn-block h-12" disabled={busy || !form.pizza_id}>
          Submit review
        </button>
      </form>
    </Modal>
  );
}

function OrderCard({ order, onCancel, onPay, onReview, busy, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen);
  const items = order.order_item || [];
  const count = items.reduce((n, i) => n + i.quantity, 0);
  const thumbs = items.slice(0, 3);
  const isActive = order.status === "Pending";

  return (
    <article className={`card overflow-hidden p-0 transition hover:shadow-lift ${isActive ? "border-brand-500/40" : ""}`}>
      <button
        type="button"
        className="flex w-full items-center gap-4 p-4 text-left transition-colors hover:bg-surface-2/50 sm:p-5"
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
      >
        <div className="flex shrink-0 -space-x-3">
          {thumbs.map((i, idx) => (
            <div key={idx} className="h-12 w-12 overflow-hidden rounded-full bg-surface-2 ring-2 ring-surface">
              <PizzaImage pizza={{ id: i.pizza_id, name: i.pizza_name }} width={120} sizes="48px" className="h-full w-full" alt="" />
            </div>
          ))}
        </div>
        <div className="min-w-0 flex-1">
          <p className="truncate font-display font-bold text-ink">
            {thumbs.map((i) => i.pizza_name).join(", ") || `Order #${shortId(order.id)}`}
          </p>
          <p className="text-xs text-muted">
            #{shortId(order.id)} · {dateTime(order.created_at)} · {count} item{count === 1 ? "" : "s"}
          </p>
          <div className="mt-1.5 flex items-center gap-2 sm:hidden">
            <StatusBadge status={order.status} />
            <span className="text-sm font-bold tabular-nums">{money(order.total_price)}</span>
          </div>
        </div>
        <div className="hidden shrink-0 flex-col items-end gap-1 sm:flex">
          <span className="font-display font-extrabold tabular-nums">{money(order.total_price)}</span>
          <StatusBadge status={order.status} />
        </div>
        <ChevronDown className={`h-5 w-5 shrink-0 text-muted transition-transform ${open ? "rotate-180" : ""}`} aria-hidden="true" />
      </button>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.25 }}>
            <div className="space-y-5 border-t border-line p-4 sm:p-5">
              <OrderTracker order={order} />
              <OrderItems items={items} />
              {order.notes && (
                <p className="rounded-xl bg-surface-2 p-3 text-sm">
                  <span className="font-semibold">Rider notes:</span> {order.notes}
                </p>
              )}
              <p className="text-xs text-muted">
                Full order ID: <span className="mono select-all">{order.id}</span>
              </p>
              <div className="flex flex-wrap gap-2">
                {order.status !== "Cancelled" && (
                  <button className="btn btn-primary btn-sm" onClick={() => onPay(order)}>
                    <CreditCard className="h-4 w-4" /> Payment
                  </button>
                )}
                {order.status === "Delivered" && (
                  <button className="btn btn-secondary btn-sm" onClick={() => onReview(order)}>
                    <Star className="h-4 w-4" /> Write a review
                  </button>
                )}
                {order.status === "Pending" && (
                  <button className="btn btn-ghost btn-sm danger" onClick={() => onCancel(order)} disabled={busy}>
                    <XCircle className="h-4 w-4" /> Cancel order
                  </button>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </article>
  );
}

const FILTERS = [
  { key: "all", label: "All" },
  { key: "active", label: "Active", status: "Pending" },
  { key: "delivered", label: "Delivered", status: "Delivered" },
  { key: "cancelled", label: "Cancelled", status: "Cancelled" },
];

export default function Orders() {
  const location = useLocation();
  const [params, setParams] = useSearchParams();
  const history = useLoad(() => orderApi.history());
  const { busy, message, setMessage, run } = useAction();
  const [payFor, setPayFor] = useState(null);
  const [reviewFor, setReviewFor] = useState(null);
  const [lookupId, setLookupId] = useState("");
  const [lookup, setLookup] = useState(null);

  const filter = FILTERS.find((f) => f.key === params.get("filter")) || FILTERS[0];
  const all = [...(history.data?.order || [])].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  const orders = filter.status ? all.filter((o) => o.status === filter.status) : all;
  const countFor = (f) => (f.status ? all.filter((o) => o.status === f.status).length : all.length);

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
      <PageHeader
        eyebrow={filter.key === "active" ? "Track order" : "Orders"}
        title={filter.key === "active" ? "Track your order" : "My orders"}
        subtitle="Track, pay for and review your orders."
      />

      {location.state?.placed && (
        <Alert type="success">Order #{shortId(location.state.placed)} placed! Open it below to pay.</Alert>
      )}
      <Message message={message} onClose={() => setMessage(null)} />

      <div className="mb-5 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div className="no-scrollbar -mx-1 flex gap-2 overflow-x-auto px-1" role="tablist" aria-label="Filter orders">
          {FILTERS.map((f) => (
            <button
              key={f.key}
              role="tab"
              aria-selected={filter.key === f.key}
              className={`chip shrink-0 ${filter.key === f.key ? "active" : ""}`}
              onClick={() => setParams(f.key === "all" ? {} : { filter: f.key }, { replace: true })}
            >
              {f.label}
              {!history.loading && <span className="ml-1.5 text-xs opacity-75">{countFor(f)}</span>}
            </button>
          ))}
        </div>
        <form className="flex w-full gap-2 lg:w-auto" onSubmit={find}>
          <div className="relative flex-1 lg:w-80">
            <Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" aria-hidden="true" />
            <input className="pl-10" placeholder="Find an order by its full ID…" value={lookupId} onChange={(e) => setLookupId(e.target.value)} aria-label="Order ID" />
          </div>
          <button className="btn btn-secondary" disabled={busy}>
            Find
          </button>
        </form>
      </div>

      {lookup && (
        <div className="stack">
          <h3>Search result</h3>
          <OrderCard order={lookup} busy={busy} onCancel={cancel} onPay={setPayFor} onReview={setReviewFor} defaultOpen />
        </div>
      )}

      {history.loading && <ListSkeleton rows={4} />}
      <Alert type="error">{history.error}</Alert>
      {!history.loading && !history.error && orders.length === 0 && (
        <Empty
          icon={filter.key === "active" ? Bike : ReceiptText}
          title={filter.key === "active" ? "No active orders" : all.length ? `No ${filter.label.toLowerCase()} orders` : "No orders yet"}
          action={
            <Link to="/menu" className="btn btn-primary">
              Order a pizza
            </Link>
          }
        >
          {filter.key === "active" ? "When you place an order you can follow it here." : "Your order history will appear here."}
        </Empty>
      )}

      <div className="stack">
        {orders.map((o, i) => (
          <motion.div key={o.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: Math.min(i, 8) * 0.04 }}>
            <OrderCard
              order={o}
              busy={busy}
              onCancel={cancel}
              onPay={setPayFor}
              onReview={setReviewFor}
              defaultOpen={o.status === "Pending" && (filter.key === "active" || o.id === location.state?.placed)}
            />
          </motion.div>
        ))}
      </div>

      {payFor && <PaymentModal order={payFor} onClose={() => setPayFor(null)} />}
      {reviewFor && <ReviewModal order={reviewFor} onClose={() => setReviewFor(null)} />}
    </>
  );
}
