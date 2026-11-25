import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { addressApi, cartApi, orderApi } from "../api/endpoints";
import { Alert, Empty, Field, Message, PageHeader, Spinner, money, useAction, useLoad } from "../components/ui";

export default function Cart() {
  const cart = useLoad(() => cartApi.get());
  const addresses = useLoad(() => addressApi.list());
  const { busy, message, setMessage, run } = useAction();
  const [addressId, setAddressId] = useState("");
  const [notes, setNotes] = useState("");
  const navigate = useNavigate();

  // Backend returns a list; a user has at most one cart.
  const current = cart.data?.[0];
  const items = current?.items || [];
  const total = items.reduce((sum, i) => sum + Number(i.sub_total), 0);

  useEffect(() => {
    if (!addressId && addresses.data?.length) {
      const def = addresses.data.find((a) => a.is_default) || addresses.data[0];
      setAddressId(String(def.id));
    }
  }, [addresses.data, addressId]);

  const changeQty = async (item, qty) => {
    if (qty < 1) return;
    await run(() => cartApi.updateQuantity(item.id, qty));
    cart.reload();
  };

  const remove = async (item) => {
    await run(() => cartApi.removeItem(item.id), "Item removed.");
    cart.reload();
  };

  const clear = async () => {
    if (!window.confirm("Remove everything from your cart?")) return;
    await run(() => cartApi.clear(), "Cart cleared.");
    cart.reload();
  };

  const placeOrder = async () => {
    const res = await run(() => orderApi.placeFromCart(Number(addressId), notes.trim()));
    if (res) navigate("/orders", { state: { placed: res.order_details?.order_id } });
  };

  return (
    <>
      <PageHeader title="Your cart" subtitle="Review your items and place your order." />
      <Message message={message} onClose={() => setMessage(null)} />

      {cart.loading && <Spinner />}
      <Alert type="error">{cart.error}</Alert>

      {!cart.loading && !cart.error && items.length === 0 && (
        <Empty icon="🛒" title="Your cart is empty">
          <Link to="/menu">Browse the menu</Link> to add some pizza.
        </Empty>
      )}

      {items.length > 0 && (
        <div className="cart-layout">
          <section className="card">
            <div className="card-head">
              <h2>Items ({items.length})</h2>
              <button className="btn btn-ghost btn-sm" onClick={clear} disabled={busy}>
                Clear cart
              </button>
            </div>
            <ul className="cart-items">
              {items.map((item) => (
                <li key={item.id} className="cart-item">
                  {item.pizza?.image_url && <img src={item.pizza.image_url} alt="" />}
                  <div className="cart-item-info">
                    <strong>{item.pizza?.name || `Pizza #${item.pizza_id}`}</strong>
                    <span className="muted small">
                      {item.size} · {money(item.unit_price)} each
                    </span>
                  </div>
                  <div className="qty">
                    <button className="icon-btn" onClick={() => changeQty(item, item.quantity - 1)} disabled={busy || item.quantity <= 1} aria-label="Decrease">
                      −
                    </button>
                    <span>{item.quantity}</span>
                    <button className="icon-btn" onClick={() => changeQty(item, item.quantity + 1)} disabled={busy} aria-label="Increase">
                      +
                    </button>
                  </div>
                  <strong className="line-total">{money(item.sub_total)}</strong>
                  <button className="icon-btn danger" onClick={() => remove(item)} disabled={busy} aria-label="Remove">
                    🗑
                  </button>
                </li>
              ))}
            </ul>
          </section>

          <aside className="card checkout">
            <h2>Checkout</h2>
            {addresses.data?.length === 0 ? (
              <Alert type="info">
                You need a delivery address first. <Link to="/addresses">Add one</Link>.
              </Alert>
            ) : (
              <Field label="Deliver to">
                <select value={addressId} onChange={(e) => setAddressId(e.target.value)}>
                  {addresses.data?.map((a) => (
                    <option key={a.id} value={a.id}>
                      {a.label} — {a.street}, {a.city}
                    </option>
                  ))}
                </select>
              </Field>
            )}
            <Field label="Notes for the rider (optional)">
              <textarea rows={3} value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Ring the bell twice…" />
            </Field>
            <div className="total-row">
              <span>Total</span>
              <strong>{money(current?.total_price ?? total)}</strong>
            </div>
            <button className="btn btn-primary btn-block" onClick={placeOrder} disabled={busy || !addressId}>
              {busy ? "Placing order…" : "Place order"}
            </button>
          </aside>
        </div>
      )}
    </>
  );
}
