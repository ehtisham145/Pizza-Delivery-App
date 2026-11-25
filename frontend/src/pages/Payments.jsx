import { paymentApi } from "../api/endpoints";
import { Alert, Empty, PageHeader, Spinner, StatusBadge, dateTime, money, shortId, useLoad } from "../components/ui";

export default function Payments() {
  const list = useLoad(() => paymentApi.history());
  const payments = list.data || [];

  return (
    <>
      <PageHeader title="Payment history" subtitle="Payments you have made for your orders." />
      {list.loading && <Spinner />}
      <Alert type="error">{list.error}</Alert>
      {!list.loading && !list.error && payments.length === 0 && <Empty icon="💳" title="No payments yet" />}

      {payments.length > 0 && (
        <div className="card table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Order</th>
                <th>Method</th>
                <th>Status</th>
                <th className="num">Amount</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {payments.map((p) => (
                <tr key={p.id}>
                  <td className="mono">#{shortId(p.order_id)}</td>
                  <td>{p.method}</td>
                  <td>
                    <StatusBadge status={p.status} />
                  </td>
                  <td className="num">{money(p.amount)}</td>
                  <td>{dateTime(p.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
