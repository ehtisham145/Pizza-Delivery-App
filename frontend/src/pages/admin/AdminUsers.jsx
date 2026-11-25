import { useMemo, useState } from "react";
import { adminApi } from "../../api/endpoints";
import { ROLES } from "../../constants";
import { useAuth } from "../../context/AuthContext";
import { Alert, Empty, Message, PageHeader, Spinner, StatusBadge, useAction, useLoad } from "../../components/ui";

export default function AdminUsers() {
  const { user: me } = useAuth();
  const list = useLoad(() => adminApi.users());
  const { busy, message, setMessage, run } = useAction();
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("all");

  const users = useMemo(() => {
    const q = search.trim().toLowerCase();
    return (list.data || []).filter(
      (u) =>
        (filter === "all" || (filter === "active" ? u.is_active : !u.is_active)) &&
        (!q || u.full_name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q))
    );
  }, [list.data, search, filter]);

  const toggleActive = async (u) => {
    await run(
      () => (u.is_active ? adminApi.deactivate(u.id) : adminApi.activate(u.id)),
      `${u.full_name} ${u.is_active ? "deactivated" : "activated"}.`
    );
    list.reload();
  };

  const changeRole = async (u, role) => {
    if (role === u.role) return;
    await run(() => adminApi.changeRole(u.id, role), `${u.full_name} is now ${role}.`);
    list.reload();
  };

  const pendingCount = (list.data || []).filter((u) => !u.is_active).length;

  return (
    <>
      <PageHeader title="Users" subtitle="New sign-ups start inactive. Activate them so they can log in." />
      <Message message={message} onClose={() => setMessage(null)} />
      {pendingCount > 0 && <Alert type="info">{pendingCount} user(s) waiting for activation.</Alert>}

      <div className="toolbar">
        <input className="search" placeholder="Search name or email…" value={search} onChange={(e) => setSearch(e.target.value)} />
        <div className="chips">
          {["all", "active", "inactive"].map((f) => (
            <button key={f} className={`chip${filter === f ? " active" : ""}`} onClick={() => setFilter(f)}>
              {f[0].toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {list.loading && <Spinner />}
      <Alert type="error">{list.error}</Alert>
      {!list.loading && !list.error && users.length === 0 && <Empty icon="👤" title="No users match" />}

      {users.length > 0 && (
        <div className="card table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Role</th>
                <th>Status</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {users.map((u) => {
                const isMe = u.id === me?.id;
                const isAdminUser = u.role === "admin";
                return (
                  <tr key={u.id}>
                    <td>
                      {u.full_name} {isMe && <span className="muted small">(you)</span>}
                    </td>
                    <td>{u.email}</td>
                    <td>{u.phone_number}</td>
                    <td>
                      <select
                        value={ROLES.includes(u.role) ? u.role : ""}
                        onChange={(e) => changeRole(u, e.target.value)}
                        disabled={busy || isAdminUser}
                        title={isAdminUser ? "An admin's role cannot be changed" : ""}
                        aria-label={`Role for ${u.full_name}`}
                      >
                        {!ROLES.includes(u.role) && <option value="">{u.role}</option>}
                        {ROLES.map((r) => (
                          <option key={r} value={r}>
                            {r}
                          </option>
                        ))}
                      </select>
                    </td>
                    <td>
                      <StatusBadge status={u.is_active ? "Active" : "Inactive"} />
                    </td>
                    <td className="num">
                      <button
                        className={`btn btn-sm ${u.is_active ? "btn-ghost danger" : "btn-primary"}`}
                        onClick={() => toggleActive(u)}
                        disabled={busy || (isMe && u.is_active)}
                      >
                        {u.is_active ? "Deactivate" : "Activate"}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
