import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import { ArrowLeft, Check, CreditCard, MapPin, Plus, ShieldCheck, ShoppingBag, Trash2 } from "lucide-react";
import { addressApi, orderApi } from "../api/endpoints";
import { useCart } from "../context/CartContext";
import { useToast } from "../context/ToastContext";
import { CartLine } from "../components/CartDrawer";
import { Alert, Empty, Message, PageHeader, Skeleton, money, useAction, useLoad } from "../components/ui";

function Section({ step, title, children, action }) {
  return (
    <section className="card">
      <div className="mb-4 flex items-center justify-between gap-3">
        <h2 className="flex items-center gap-3 text-lg">
          <span className="grid h-7 w-7 place-items-center rounded-full bg-brand-600 text-sm font-bold text-white">{step}</span>
          {title}
        </h2>
        {action}
      </div>
      {children}
    </section>
  );
}

export default function Cart() {
  const cart = useCart();
  const { toast } = useToast();
  const addresses = useLoad(() => addressApi.list());
  const { busy, message, setMessage, run } = useAction();
  const [addressId, setAddressId] = useState("");
  const [notes, setNotes] = useState("");
  const navigate = useNavigate();

  const { items, count, total } = cart;

  useEffect(() => {
    if (!addressId && addresses.data?.length) {
      const def = addresses.data.find((a) => a.is_default) || addresses.data[0];
      setAddressId(String(def.id));
    }
  }, [addresses.data, addressId]);

  const clear = async () => {
    if (!window.confirm("Remove everything from your cart?")) return;
    try {
      await cart.clear();
      toast({ title: "Cart cleared" });
    } catch (err) {
      setMessage({ type: "error", text: err.message });
    }
  };

  const placeOrder = async () => {
    const res = await run(() => orderApi.placeFromCart(Number(addressId), notes.trim()));
    if (res) {
      await cart.reload();
      navigate("/orders", { state: { placed: res.order_details?.order_id } });
    }
  };

  if (cart.loading && items.length === 0) {
    return (
      <>
        <PageHeader eyebrow="Checkout" title="Review your order" />
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">
          <div className="card space-y-4">
            {[0, 1, 2].map((i) => (
              <div key={i} className="flex gap-4">
                <Skeleton className="h-20 w-20 rounded-xl" />
                <div className="flex-1 space-y-2 pt-1">
                  <Skeleton className="h-4 w-1/2" />
                  <Skeleton className="h-3 w-1/4" />
                </div>
              </div>
            ))}
          </div>
          <Skeleton className="h-72 rounded-2xl" />
        </div>
      </>
    );
  }

  return (
    <>
      <PageHeader
        eyebrow="Checkout"
        title="Review your order"
        subtitle="Check your items, choose where to deliver, and place your order."
        actions={
          <Link to="/menu" className="btn btn-ghost btn-sm">
            <ArrowLeft className="h-4 w-4" /> Keep shopping
          </Link>
        }
      />
      <Message message={message} onClose={() => setMessage(null)} />
      <Alert type="error">{cart.error}</Alert>

      {!cart.error && items.length === 0 ? (
        <Empty
          icon={ShoppingBag}
          title="Your cart is empty"
          action={
            <Link to="/menu" className="btn btn-primary">
              Browse the menu
            </Link>
          }
        >
          Add a pizza or two and come back here to check out.
        </Empty>
      ) : (
        items.length > 0 && (
          <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">
            <div className="space-y-6">
              <Section
                step={1}
                title={`Your items (${count})`}
                action={
                  <button type="button" className="btn btn-ghost btn-sm text-muted" onClick={clear} disabled={cart.busy || busy}>
                    <Trash2 className="h-4 w-4" /> Clear
                  </button>
                }
              >
                <ul className="m-0 -my-4 list-none p-0">
                  <AnimatePresence initial={false}>
                    {items.map((item) => (
                      <CartLine key={item.id} item={item} />
                    ))}
                  </AnimatePresence>
                </ul>
                <Link to="/menu" className="mt-4 inline-flex items-center gap-1.5 text-sm font-semibold no-underline">
                  <Plus className="h-4 w-4" /> Add more items
                </Link>
              </Section>

              <Section
                step={2}
                title="Delivery address"
                action={
                  <Link to="/addresses" className="btn btn-ghost btn-sm">
                    Manage
                  </Link>
                }
              >
                {addresses.loading ? (
                  <div className="grid gap-3 sm:grid-cols-2">
                    <Skeleton className="h-20 rounded-xl" />
                    <Skeleton className="h-20 rounded-xl" />
                  </div>
                ) : addresses.data?.length === 0 ? (
                  <Alert type="info">
                    You need a delivery address first. <Link to="/addresses">Add one</Link>.
                  </Alert>
                ) : (
                  <div className="grid gap-3 sm:grid-cols-2" role="radiogroup" aria-label="Delivery address">
                    {addresses.data?.map((a) => {
                      const active = String(a.id) === addressId;
                      return (
                        <button
                          key={a.id}
                          type="button"
                          role="radio"
                          aria-checked={active}
                          onClick={() => setAddressId(String(a.id))}
                          className={`relative flex items-start gap-3 rounded-xl border-2 p-3.5 text-left transition active:scale-[0.99] ${
                            active ? "border-brand-600 bg-brand-soft" : "border-line hover:border-brand-500/40"
                          }`}
                        >
                          <span className={`grid h-9 w-9 shrink-0 place-items-center rounded-full ${active ? "bg-brand-600 text-white" : "bg-surface-2 text-muted"}`}>
                            <MapPin className="h-4 w-4" aria-hidden="true" />
                          </span>
                          <span className="min-w-0">
                            <span className="flex items-center gap-2 text-sm font-bold text-ink">
                              {a.label}
                              {a.is_default && <span className="rounded bg-surface-2 px-1.5 text-[0.65rem] font-semibold uppercase text-muted">Default</span>}
                            </span>
                            <span className="block text-sm text-muted">
                              {a.street}, {a.city} {a.zip_code}
                            </span>
                          </span>
                          {active && (
                            <span className="absolute right-3 top-3 grid h-5 w-5 place-items-center rounded-full bg-brand-600 text-white">
                              <Check className="h-3 w-3" strokeWidth={3} />
                            </span>
                          )}
                        </button>
                      );
                    })}
                  </div>
                )}
                <label className="field mb-0 mt-5" htmlFor="rider-notes">
                  <span className="field-label">Notes for the rider (optional)</span>
                  <textarea id="rider-notes" rows={2} value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Ring the bell twice, gate code 1234…" />
                </label>
              </Section>
            </div>

            <aside className="card space-y-4 lg:sticky lg:top-24">
              <h2 className="text-lg">Order summary</h2>
              <dl className="space-y-2 text-sm">
                {items.map((i) => (
                  <div key={i.id} className="flex justify-between gap-3">
                    <dt className="truncate text-muted">
                      {i.quantity} × {i.pizza?.name || `Pizza #${i.pizza_id}`} <span className="text-xs">({i.size})</span>
                    </dt>
                    <dd className="m-0 shrink-0 tabular-nums">{money(i.sub_total)}</dd>
                  </div>
                ))}
              </dl>
              <div className="flex items-baseline justify-between border-t border-line pt-4">
                <span className="font-semibold">Total</span>
                <span className="font-display text-2xl font-extrabold tabular-nums">{money(total)}</span>
              </div>
              <button type="button" className="btn btn-primary btn-block h-12 text-base" onClick={placeOrder} disabled={busy || cart.busy || !addressId}>
                {busy ? (
                  <>
                    <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" /> Placing order…
                  </>
                ) : (
                  `Place order · ${money(total)}`
                )}
              </button>
              <ul className="space-y-2 text-xs text-muted">
                <li className="flex items-center gap-2">
                  <CreditCard className="h-4 w-4 shrink-0" aria-hidden="true" /> Pay by card or cash on delivery after placing the order.
                </li>
                <li className="flex items-center gap-2">
                  <ShieldCheck className="h-4 w-4 shrink-0" aria-hidden="true" /> You can cancel while the order is pending.
                </li>
              </ul>
            </aside>
          </div>
        )
      )}
    </>
  );
}
