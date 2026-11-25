import { useState } from "react";
import { paymentApi } from "../../api/endpoints";
import { PAYMENT_STATUSES } from "../../constants";
import { Alert, Empty, Message, PageHeader, Spinner, StatusBadge, dateTime, money, shortId, useAction, useLoad } from "../../components/ui";

const PAGE_SIZE = 50;

export default function AdminPayments() {
  const [page, setPage] = useState(0);
  const list = useLoad(() => paymentApi.all({ skip: page * PAGE_SIZE, limit: PAGE_SIZE }), [page]);
  const { busy, message, setMessage, run } = useAction();
  const payments = list.data || [];

  const setStatus = async (p, status) => {
    if (status === p.status) return;
    await run(() => paymentApi.updateStatus(p.id, status), `Payment #${shortId(p.id)} set to ${status}.`);
    list.reload();
  };

  return (
    <>
      <PageHeader title="Payments" subtitle="All payments across the platform." />
      <Message message={message} onClose={() => setMessage(null)} />
      {list.loading && <Spinner />}
      <Alert type="error">{list.error}</Alert>
      {!list.loading && !list.error && payments.length === 0 && <Empty icon="💳" title="No payments yet" />}

      {payments.length > 0 && (
        <div className="card table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Payment</th>
                <th>Order</th>
                <th>Method</th>
                <th className="num">Amount</th>
                <th>Created</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {payments.map((p) => (
                <tr key={p.id}>
                  <td className="mono">#{shortId(p.id)}</td>
                  <td className="mono">#{shortId(p.order_id)}</td>
                  <td>{p.method}</td>
                  <td className="num">{money(p.amount)}</td>
                  <td>{dateTime(p.created_at)}</td>
                  <td>
                    <div className="inline">
                      <StatusBadge status={p.status} />
                      <select
                        value=""
                        onChange={(e) => setStatus(p, e.target.value)}
                        disabled={busy}
                        aria-label={`Change status of payment ${shortId(p.id)}`}
                      >
                        <option value="">Change…</option>
                        {/* Backend refuses reverting to Pending */}
                        {PAYMENT_STATUSES.filter((s) => s !== "Pending" && s !== p.status).map((s) => (
                          <option key={s}>{s}</option>
                        ))}
                      </select>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="pager">
        <button className="btn btn-ghost btn-sm" disabled={page === 0} onClick={() => setPage(page - 1)}>
          ← Previous
        </button>
        <span className="muted">Page {page + 1}</span>
        <button className="btn btn-ghost btn-sm" disabled={payments.length < PAGE_SIZE} onClick={() => setPage(page + 1)}>
          Next →
        </button>
      </div>
    </>
  );
}
