import { useState } from "react";
import { notificationApi } from "../api/endpoints";
import { Alert, Empty, Message, PageHeader, Spinner, dateTime, useAction, useLoad } from "../components/ui";

const PAGE_SIZE = 20;

export default function Notifications() {
  const [page, setPage] = useState(1);
  const list = useLoad(() => notificationApi.list({ page, size: PAGE_SIZE }), [page]);
  const { busy, message, setMessage, run } = useAction();

  const items = list.data?.notifications || list.data?.Notifications || [];
  const total = list.data?.total ?? items.length;
  const pages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const markOne = async (n) => {
    if (n.is_read) return;
    await run(() => notificationApi.markRead(n.id));
    list.reload();
  };

  const markAll = async () => {
    await run(() => notificationApi.markAllRead(), "All notifications marked as read.");
    list.reload();
  };

  return (
    <>
      <PageHeader
        title="Notifications"
        subtitle="Updates about your orders."
        actions={
          <button className="btn btn-secondary" onClick={markAll} disabled={busy || items.every((n) => n.is_read)}>
            Mark all as read
          </button>
        }
      />
      <Message message={message} onClose={() => setMessage(null)} />
      {list.loading && <Spinner />}
      <Alert type="error">{list.error}</Alert>
      {!list.loading && !list.error && items.length === 0 && <Empty icon="🔔" title="You're all caught up" />}

      <ul className="notif-list">
        {items.map((n) => (
          <li key={n.id}>
            <button className={`card notif${n.is_read ? "" : " unread"}`} onClick={() => markOne(n)} disabled={busy}>
              {!n.is_read && <span className="dot" aria-label="Unread" />}
              <div>
                <strong>{n.title}</strong>
                <p>{n.message}</p>
                <span className="muted small">{dateTime(n.created_at)}</span>
              </div>
            </button>
          </li>
        ))}
      </ul>

      {pages > 1 && (
        <div className="pager">
          <button className="btn btn-ghost btn-sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>
            ← Previous
          </button>
          <span className="muted">
            Page {page} of {pages}
          </span>
          <button className="btn btn-ghost btn-sm" disabled={page >= pages} onClick={() => setPage(page + 1)}>
            Next →
          </button>
        </div>
      )}
    </>
  );
}
