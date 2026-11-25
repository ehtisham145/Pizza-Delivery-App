import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowRight, ArrowUpRight, Banknote, ChefHat, Clock, PackageCheck, Pizza, Plus, ReceiptText, RefreshCw, TrendingUp, Users, XCircle } from "lucide-react";
import { adminApi, menuApi, orderApi } from "../../api/endpoints";
import { useAuth } from "../../context/AuthContext";
import { Alert, Skeleton, StatusBadge, dateTime, money, shortId, useLoad } from "../../components/ui";

const TONES = {
  red: "bg-brand-soft text-brand-600",
  amber: "bg-amber-100 text-amber-700 dark:bg-amber-400/15 dark:text-amber-300",
  green: "bg-emerald-50 text-emerald-700 dark:bg-emerald-400/15 dark:text-emerald-300",
  blue: "bg-sky-50 text-sky-700 dark:bg-sky-400/15 dark:text-sky-300",
};

function Stat({ label, value, to, icon: Icon, tone }) {
  const body = (
    <>
      <div className="flex items-start justify-between">
        <span className={`grid h-10 w-10 place-items-center rounded-lg ${tone}`}>
          <Icon className="h-5 w-5" aria-hidden="true" />
        </span>
        {to && <ArrowUpRight className="h-4 w-4 text-muted" aria-hidden="true" />}
      </div>
      <span className="stat-label mt-4">{label}</span>
      <strong className="stat-value">{value}</strong>
    </>
  );
  return to ? (
    <Link to={to} className="card stat rounded-xl">
      {body}
    </Link>
  ) : (
    <div className="card stat rounded-xl">{body}</div>
  );
}

function Panel({ title, action, children, className = "" }) {
  return (
    <section className={`card min-w-0 rounded-xl p-0 ${className}`}>
      <div className="flex items-center justify-between gap-3 border-b border-line px-5 py-4">
        <h2 className="text-base">{title}</h2>
        {action}
      </div>
      <div className="p-5">{children}</div>
    </section>
  );
}

const STATUS_META = [
  { key: "Pending", icon: Clock, bar: "bg-amber-400" },
  { key: "Delivered", icon: PackageCheck, bar: "bg-emerald-500" },
  { key: "Cancelled", icon: XCircle, bar: "bg-brand-500" },
];

function OrdersByStatus() {
  const data = useLoad(() =>
    Promise.all(STATUS_META.map((s) => adminApi.ordersByStatus(s.key).then((l) => [s.key, l.length])))
      .then(Object.fromEntries)
  );
  const counts = data.data || {};
  const total = Object.values(counts).reduce((a, b) => a + b, 0);

  if (data.loading) return <Skeleton className="h-28" />;
  if (data.error) return <Alert type="error">{data.error}</Alert>;

  return (
    <>
      <div className="mb-5 flex h-3 overflow-hidden rounded-full bg-surface-2" aria-hidden="true">
        {total > 0 &&
          STATUS_META.map((s) => (
            <motion.span
              key={s.key}
              className={s.bar}
              initial={{ width: 0 }}
              animate={{ width: `${(counts[s.key] / total) * 100}%` }}
              transition={{ duration: 0.6 }}
            />
          ))}
      </div>
      <ul className="m-0 grid list-none grid-cols-3 gap-3 p-0">
        {STATUS_META.map((s) => (
          <li key={s.key}>
            <Link to="/admin/orders" className="block rounded-lg border border-line p-3 text-ink no-underline transition hover:border-ink/20">
              <span className="flex items-center gap-1.5 text-xs text-muted">
                <span className={`h-2 w-2 rounded-full ${s.bar}`} aria-hidden="true" /> {s.key}
              </span>
              <span className="mt-1 block font-display text-2xl font-extrabold tabular-nums">{counts[s.key] ?? 0}</span>
            </Link>
          </li>
        ))}
      </ul>
      {total === 0 && <p className="mt-4 text-sm text-muted">No orders yet. They'll show up here as customers check out.</p>}
    </>
  );
}

function RecentOrders() {
  const list = useLoad(() => orderApi.all({ page: 1, page_size: 6 }));
  const orders = [...(list.data || [])].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

  if (list.loading)
    return (
      <div className="space-y-3">
        {[0, 1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-10" />
        ))}
      </div>
    );
  if (list.error) return <Alert type="error">{list.error}</Alert>;
  if (!orders.length) return <p className="py-6 text-center text-sm text-muted">No orders yet.</p>;

  return (
    <div className="-mx-5 -my-5 overflow-x-auto">
      <table className="table">
        <thead>
          <tr>
            <th>Order</th>
            <th>Placed</th>
            <th className="num">Items</th>
            <th className="num">Total</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {orders.map((o) => (
            <tr key={o.id}>
              <td className="mono">#{shortId(o.id)}</td>
              <td className="text-muted">{dateTime(o.created_at)}</td>
              <td className="num">{(o.order_item || []).reduce((n, i) => n + i.quantity, 0)}</td>
              <td className="num font-semibold">{money(o.total_price)}</td>
              <td>
                <StatusBadge status={o.status} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function MenuHealth() {
  const pizzas = useLoad(() => menuApi.pizzas());
  if (pizzas.loading) return <Skeleton className="h-24" />;
  if (pizzas.error) return <Alert type="error">{pizzas.error}</Alert>;
  const list = pizzas.data || [];
  const off = list.filter((p) => !p.is_available);

  return (
    <>
      <div className="flex items-end gap-6">
        <div>
          <p className="text-xs text-muted">On the menu</p>
          <p className="font-display text-3xl font-extrabold tabular-nums">{list.length}</p>
        </div>
        <div>
          <p className="text-xs text-muted">Available</p>
          <p className="font-display text-3xl font-extrabold tabular-nums text-emerald-600 dark:text-emerald-400">{list.length - off.length}</p>
        </div>
        <div>
          <p className="text-xs text-muted">Unavailable</p>
          <p className={`font-display text-3xl font-extrabold tabular-nums ${off.length ? "text-brand-600" : ""}`}>{off.length}</p>
        </div>
      </div>
      {off.length > 0 && <p className="mt-3 truncate text-sm text-muted">Turned off: {off.map((p) => p.name).join(", ")}</p>}
    </>
  );
}

const QUICK = [
  { to: "/admin/orders", label: "Process orders", icon: ChefHat },
  { to: "/admin/menu", label: "Add or edit pizzas", icon: Plus },
  { to: "/admin/users", label: "Manage users", icon: Users },
  { to: "/admin/payments", label: "Review payments", icon: Banknote },
];

export default function AdminDashboard() {
  const { user } = useAuth();
  const stats = useLoad(() => adminApi.stats());
  const s = stats.data;

  const tiles = s
    ? [
        { label: "Orders today", value: s.total_orders_today, to: "/admin/orders", icon: ReceiptText, tone: TONES.red },
        { label: "Revenue today", value: money(s.total_revenue_today), icon: Banknote, tone: TONES.green },
        { label: "Pending orders", value: s.total_pending_orders, to: "/admin/orders", icon: Clock, tone: TONES.amber },
        { label: "Total users", value: s.total_users, to: "/admin/users", icon: Users, tone: TONES.blue },
        { label: "Orders all time", value: s.total_orders_all_time, icon: TrendingUp, tone: TONES.red },
        { label: "Revenue all time", value: money(s.total_revenue_all_time), to: "/admin/payments", icon: Banknote, tone: TONES.green },
      ]
    : [];

  return (
    <>
      <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1>Welcome back, {(user?.full_name || "Admin").split(" ")[0]}</h1>
          <p className="muted mt-1">Here's how the shop is doing right now.</p>
        </div>
        <button className="btn btn-secondary" onClick={stats.reload} disabled={stats.loading}>
          <RefreshCw className={`h-4 w-4 ${stats.loading ? "animate-spin" : ""}`} /> Refresh
        </button>
      </div>

      <Alert type="error">{stats.error}</Alert>
      {stats.loading && !s ? (
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-3 2xl:grid-cols-6">
          {Array.from({ length: 6 }, (_, i) => (
            <Skeleton key={i} className="h-36 rounded-xl" />
          ))}
        </div>
      ) : (
        s && (
          <motion.div
            className="grid grid-cols-2 gap-4 lg:grid-cols-3 2xl:grid-cols-6"
            initial="hidden"
            animate="show"
            variants={{ show: { transition: { staggerChildren: 0.05 } } }}
          >
            {tiles.map((t) => (
              <motion.div key={t.label} variants={{ hidden: { opacity: 0, y: 12 }, show: { opacity: 1, y: 0 } }}>
                <Stat {...t} />
              </motion.div>
            ))}
          </motion.div>
        )
      )}

      <div className="mt-6 grid grid-cols-1 gap-6 xl:grid-cols-3">
        <Panel
          title="Recent orders"
          className="xl:col-span-2"
          action={
            <Link to="/admin/orders" className="inline-flex items-center gap-1 text-sm font-semibold no-underline">
              View all <ArrowRight className="h-4 w-4" />
            </Link>
          }
        >
          <RecentOrders />
        </Panel>

        <div className="min-w-0 space-y-6">
          <Panel title="Orders by status">
            <OrdersByStatus />
          </Panel>
          <Panel
            title="Menu health"
            action={
              <Link to="/admin/menu" className="inline-flex items-center gap-1 text-sm font-semibold no-underline">
                <Pizza className="h-4 w-4" /> Manage
              </Link>
            }
          >
            <MenuHealth />
          </Panel>
        </div>
      </div>

      <section className="mt-6">
        <h2 className="mb-3 text-base">Quick actions</h2>
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
          {QUICK.map(({ to, label, icon: Icon }) => (
            <Link key={to} to={to} className="card flex items-center gap-3 rounded-xl p-4 text-ink no-underline transition hover:-translate-y-0.5 hover:shadow-lift">
              <span className="grid h-9 w-9 place-items-center rounded-lg bg-surface-2">
                <Icon className="h-[18px] w-[18px]" aria-hidden="true" />
              </span>
              <span className="text-sm font-semibold">{label}</span>
            </Link>
          ))}
        </div>
      </section>
    </>
  );
}
