import { useState } from "react";
import { adminApi, orderApi } from "../../api/endpoints";
import { ORDER_STATUSES } from "../../constants";
import { useAuth } from "../../context/AuthContext";
import { OrderItems } from "../Orders";
import {
  Alert,
  Empty,
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
} from "../../components/ui";

const PAGE_SIZE = 20;

function OrderModal({ order, onClose, onUpdate, busy, message }) {
  return (
    <Modal title={`Order #${shortId(order.id)}`} onClose={onClose}>
      <Message message={message} />
      <dl className="details">
        <dt>Status</dt>
        <dd>
          <StatusBadge status={order.status} />
        </dd>
        <dt>Total</dt>
        <dd>{money(order.total_price)}</dd>
        <dt>Placed</dt>
        <dd>{dateTime(order.created_at)}</dd>
        {order.notes && (
          <>
            <dt>Notes</dt>
            <dd>{order.notes}</dd>
          </>
        )}
        <dt>ID</dt>
        <dd className="mono small">{order.id}</dd>
      </dl>
      <OrderItems items={order.order_item} />
      {order.status !== "Delivered" && (
        <div className="row-actions">
          {order.status !== "Cancelled" && (
            <button className="btn btn-primary" disabled={busy} onClick={() => onUpdate(order, "Delivered")}>
              Mark delivered
            </button>
          )}
          {order.status === "Pending" && (
            <button className="btn btn-danger" disabled={busy} onClick={() => onUpdate(order, "Cancelled")}>
              Cancel order
            </button>
          )}
        </div>
      )}
    </Modal>
  );
}

export default function AdminOrders() {
  const { isAdmin } = useAuth();
  const [status, setStatus] = useState("");
  const [page, setPage] = useState(1);
  const list = useLoad(
    () => (isAdmin ? (status ? adminApi.ordersByStatus(status) : orderApi.all({ page, page_size: PAGE_SIZE })) : Promise.resolve([])),
    [status, page, isAdmin]
  );
  const { busy, message, setMessage, run } = useAction();
  const [selected, setSelected] = useState(null);
  const [lookupId, setLookupId] = useState("");

  const orders = list.data || [];

  const open = async (id) => {
    const order = await run(() => orderApi.adminGet(id));
    if (order) setSelected(order);
    else if (order === null) setMessage({ type: "error", text: "Order not found." });
  };

  const update = async (order, newStatus) => {
    const res = await run(() => orderApi.updateStatus(order.id, newStatus), `Order marked ${newStatus.toLowerCase()}.`);
    if (res) {
      setSelected({ ...order, ...res, order_item: order.order_item });
      list.reload();
    }
  };

  return (
    <>
      <PageHeader title="Manage orders" subtitle="Find an order, view its items and move it through its lifecycle." />
      <Message message={selected ? null : message} onClose={() => setMessage(null)} />

      <form
        className="toolbar"
        onSubmit={(e) => {
          e.preventDefault();
          if (lookupId.trim()) open(lookupId.trim());
        }}
      >
        <input className="search" placeholder="Open order by full ID…" value={lookupId} onChange={(e) => setLookupId(e.target.value)} />
        <button className="btn btn-secondary" disabled={busy}>
          Open
        </button>
      </form>

      {!isAdmin ? (
        <Alert type="info">Staff can open orders by ID and update their status. Only admins can list all orders.</Alert>
      ) : (
        <>
          <div className="chips">
            <button className={`chip${status === "" ? " active" : ""}`} onClick={() => { setStatus(""); setPage(1); }}>
              All
            </button>
            {ORDER_STATUSES.map((s) => (
              <button key={s} className={`chip${status === s ? " active" : ""}`} onClick={() => { setStatus(s); setPage(1); }}>
                {s}
              </button>
            ))}
          </div>

          {list.loading && <Spinner />}
          <Alert type="error">{list.error}</Alert>
          {!list.loading && !list.error && orders.length === 0 && <Empty icon="📦" title="No orders here" />}

          {orders.length > 0 && (
            <div className="card table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Order</th>
                    <th>Placed</th>
                    <th className="num">Items</th>
                    <th className="num">Total</th>
                    <th>Status</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {orders.map((o) => (
                    <tr key={o.id}>
                      <td className="mono">#{shortId(o.id)}</td>
                      <td>{dateTime(o.created_at)}</td>
                      <td className="num">{(o.order_item || []).reduce((n, i) => n + i.quantity, 0)}</td>
                      <td className="num">{money(o.total_price)}</td>
                      <td>
                        <StatusBadge status={o.status} />
                      </td>
                      <td className="num">
                        <button className="btn btn-ghost btn-sm" onClick={() => setSelected(o)}>
                          Manage
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {!status && (
            <div className="pager">
              <button className="btn btn-ghost btn-sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>
                ← Previous
              </button>
              <span className="muted">Page {page}</span>
              <button className="btn btn-ghost btn-sm" disabled={orders.length < PAGE_SIZE} onClick={() => setPage(page + 1)}>
                Next →
              </button>
            </div>
          )}
        </>
      )}

      {selected && (
        <OrderModal
          order={selected}
          busy={busy}
          message={message}
          onUpdate={update}
          onClose={() => {
            setSelected(null);
            setMessage(null);
          }}
        />
      )}
    </>
  );
}
