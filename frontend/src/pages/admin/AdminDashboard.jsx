import { Link } from "react-router-dom";
import { adminApi } from "../../api/endpoints";
import { Alert, PageHeader, Spinner, money, useLoad } from "../../components/ui";

function Stat({ label, value, to }) {
  const body = (
    <>
      <span className="stat-label">{label}</span>
      <strong className="stat-value">{value}</strong>
    </>
  );
  return to ? (
    <Link to={to} className="card stat">
      {body}
    </Link>
  ) : (
    <div className="card stat">{body}</div>
  );
}

export default function AdminDashboard() {
  const stats = useLoad(() => adminApi.stats());
  const s = stats.data;

  return (
    <>
      <PageHeader
        title="Admin dashboard"
        subtitle="Today's activity and all-time totals."
        actions={
          <button className="btn btn-secondary" onClick={stats.reload} disabled={stats.loading}>
            Refresh
          </button>
        }
      />
      {stats.loading && <Spinner />}
      <Alert type="error">{stats.error}</Alert>
      {s && (
        <div className="stat-grid">
          <Stat label="Orders today" value={s.total_orders_today} to="/admin/orders" />
          <Stat label="Revenue today" value={money(s.total_revenue_today)} />
          <Stat label="Pending orders" value={s.total_pending_orders} to="/admin/orders" />
          <Stat label="Total users" value={s.total_users} to="/admin/users" />
          <Stat label="Orders all time" value={s.total_orders_all_time} />
          <Stat label="Revenue all time" value={money(s.total_revenue_all_time)} to="/admin/payments" />
        </div>
      )}
    </>
  );
}
