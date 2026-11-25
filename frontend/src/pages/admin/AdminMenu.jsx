import { useState } from "react";
import { menuApi } from "../../api/endpoints";
import { PIZZA_CATEGORIES } from "../../constants";
import { useAuth } from "../../context/AuthContext";
import { Alert, Empty, Field, Message, Modal, PageHeader, Spinner, StatusBadge, money, useAction, useLoad } from "../../components/ui";

// ── Pizzas ──────────────────────────────────────────────────────
function PizzaForm({ initial, categories, onSubmit, busy }) {
  const [f, setF] = useState(initial);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.type === "checkbox" ? e.target.checked : e.target.value });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit({
          name: f.name.trim(),
          description: f.description.trim(),
          base_price: Number(f.base_price).toFixed(2),
          image_url: f.image_url.trim(),
          is_available: f.is_available,
          category_id: Number(f.category_id),
        });
      }}
    >
      <Field label="Name" hint="5–50 characters">
        <input required minLength={5} maxLength={50} value={f.name} onChange={set("name")} />
      </Field>
      <Field label="Description">
        <textarea required rows={3} maxLength={500} value={f.description} onChange={set("description")} />
      </Field>
      <div className="grid-2">
        <Field label="Base price (Rs)" hint="Small size price; other sizes multiply it">
          <input required type="number" min="0.01" step="0.01" value={f.base_price} onChange={set("base_price")} />
        </Field>
        <Field label="Category">
          <select required value={f.category_id} onChange={set("category_id")}>
            <option value="">Select…</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </Field>
      </div>
      <Field label="Image URL">
        <input required type="url" value={f.image_url} onChange={set("image_url")} placeholder="https://…" />
      </Field>
      <label className="checkbox">
        <input type="checkbox" checked={f.is_available} onChange={set("is_available")} /> Available to order
      </label>
      <button className="btn btn-primary btn-block" disabled={busy}>
        Save pizza
      </button>
    </form>
  );
}

function PizzasTab({ isAdmin }) {
  const pizzas = useLoad(() => menuApi.pizzas());
  const categories = useLoad(() => menuApi.categories());
  const { busy, message, setMessage, run } = useAction();
  const [editing, setEditing] = useState(null); // null | "new" | pizza

  const catName = (id) => categories.data?.find((c) => c.id === id)?.name || `#${id}`;

  const save = async (data) => {
    const ok =
      editing === "new"
        ? await run(() => menuApi.createPizza(data), "Pizza created.")
        : await run(() => menuApi.updatePizza(editing.id, data), "Pizza updated.");
    if (ok) {
      setEditing(null);
      pizzas.reload();
    }
  };

  const toggle = async (p) => {
    await run(() => menuApi.setPizzaAvailability(p.id, !p.is_available), `${p.name} is now ${p.is_available ? "unavailable" : "available"}.`);
    pizzas.reload();
  };

  const remove = async (p) => {
    if (!window.confirm(`Delete "${p.name}"? This cannot be undone.`)) return;
    await run(() => menuApi.deletePizza(p.id), "Pizza deleted.");
    pizzas.reload();
  };

  const list = pizzas.data || [];
  return (
    <>
      <div className="tab-head">
        <Message message={editing ? null : message} onClose={() => setMessage(null)} />
        {isAdmin && (
          <button className="btn btn-primary" onClick={() => setEditing("new")} disabled={!categories.data?.length}>
            + New pizza
          </button>
        )}
      </div>
      {isAdmin && categories.data?.length === 0 && <Alert type="info">Create a category first.</Alert>}
      {pizzas.loading && <Spinner />}
      <Alert type="error">{pizzas.error}</Alert>
      {!pizzas.loading && !pizzas.error && list.length === 0 && <Empty title="No pizzas yet" />}

      {list.length > 0 && (
        <div className="card table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Pizza</th>
                <th>Category</th>
                <th className="num">Base price</th>
                <th>Status</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {list.map((p) => (
                <tr key={p.id}>
                  <td>
                    <div className="inline">
                      <img className="thumb" src={p.image_url} alt="" onError={(e) => (e.currentTarget.style.visibility = "hidden")} />
                      {p.name}
                    </div>
                  </td>
                  <td>{catName(p.category_id)}</td>
                  <td className="num">{money(p.base_price)}</td>
                  <td>
                    <StatusBadge status={p.is_available ? "Available" : "Unavailable"} />
                  </td>
                  <td className="num">
                    <div className="row-actions end">
                      <button className="btn btn-ghost btn-sm" onClick={() => toggle(p)} disabled={busy}>
                        {p.is_available ? "Disable" : "Enable"}
                      </button>
                      {isAdmin && (
                        <button className="btn btn-ghost btn-sm" onClick={() => setEditing(p)}>
                          Edit
                        </button>
                      )}
                      <button className="btn btn-ghost btn-sm danger" onClick={() => remove(p)} disabled={busy}>
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {editing && (
        <Modal title={editing === "new" ? "New pizza" : `Edit ${editing.name}`} onClose={() => setEditing(null)}>
          <Message message={message} />
          <PizzaForm
            categories={categories.data || []}
            busy={busy}
            onSubmit={save}
            initial={
              editing === "new"
                ? { name: "", description: "", base_price: "", image_url: "", is_available: true, category_id: "" }
                : { ...editing, base_price: editing.base_price, category_id: String(editing.category_id) }
            }
          />
        </Modal>
      )}
    </>
  );
}

// ── Categories ──────────────────────────────────────────────────
function CategoriesTab({ isAdmin }) {
  const list = useLoad(() => menuApi.categories());
  const { busy, message, setMessage, run } = useAction();
  const existing = new Set((list.data || []).map((c) => c.name));
  const remaining = PIZZA_CATEGORIES.filter((c) => !existing.has(c));
  const [form, setForm] = useState({ name: "", description: "" });

  const create = async (e) => {
    e.preventDefault();
    const ok = await run(() => menuApi.createCategory(form.name || remaining[0], form.description.trim()), "Category created.");
    if (ok) {
      setForm({ name: "", description: "" });
      list.reload();
    }
  };

  return (
    <div className="grid-2 align-start">
      <section className="card">
        <h2>Categories</h2>
        {list.loading && <Spinner />}
        <Alert type="error">{list.error}</Alert>
        {!list.loading && (list.data || []).length === 0 && <Empty icon="🏷" title="No categories yet" />}
        <ul className="plain-list">
          {(list.data || []).map((c) => (
            <li key={c.id}>
              <strong>{c.name}</strong>
              {c.description && <p className="muted small">{c.description}</p>}
            </li>
          ))}
        </ul>
      </section>

      {isAdmin && (
        <section className="card">
          <h2>Add category</h2>
          <Message message={message} onClose={() => setMessage(null)} />
          {remaining.length === 0 ? (
            <Alert type="info">All supported categories already exist.</Alert>
          ) : (
            <form onSubmit={create}>
              <Field label="Category" hint="The backend only accepts these fixed categories">
                <select value={form.name || remaining[0]} onChange={(e) => setForm({ ...form, name: e.target.value })}>
                  {remaining.map((c) => (
                    <option key={c}>{c}</option>
                  ))}
                </select>
              </Field>
              <Field label="Description">
                <textarea required rows={3} maxLength={500} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
              </Field>
              <button className="btn btn-primary" disabled={busy}>
                Create category
              </button>
            </form>
          )}
        </section>
      )}
    </div>
  );
}

// ── Toppings ────────────────────────────────────────────────────
function ToppingForm({ initial, onSubmit, busy, label }) {
  const [f, setF] = useState(initial);
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit({ name: f.name.trim(), extra_price: Number(f.extra_price).toFixed(2), is_available: f.is_available });
      }}
    >
      <Field label="Name">
        <input required minLength={2} maxLength={100} value={f.name} onChange={(e) => setF({ ...f, name: e.target.value })} />
      </Field>
      <Field label="Extra price (Rs)">
        <input required type="number" min="0.01" step="0.01" value={f.extra_price} onChange={(e) => setF({ ...f, extra_price: e.target.value })} />
      </Field>
      <label className="checkbox">
        <input type="checkbox" checked={f.is_available} onChange={(e) => setF({ ...f, is_available: e.target.checked })} /> Available
      </label>
      <button className="btn btn-primary" disabled={busy}>
        {label}
      </button>
    </form>
  );
}

function ToppingsTab({ isAdmin }) {
  const list = useLoad(() => menuApi.toppings());
  const { busy, message, setMessage, run } = useAction();
  const [editing, setEditing] = useState(null);
  const [formKey, setFormKey] = useState(0);

  const create = async (data) => {
    if (await run(() => menuApi.createTopping(data), "Topping created.")) {
      setFormKey((k) => k + 1);
      list.reload();
    }
  };

  const update = async (data) => {
    if (await run(() => menuApi.updateTopping(editing.id, data), "Topping updated.")) {
      setEditing(null);
      list.reload();
    }
  };

  return (
    <div className="grid-2 align-start">
      <section className="card">
        <h2>Toppings</h2>
        {!editing && <Message message={message} onClose={() => setMessage(null)} />}
        {list.loading && <Spinner />}
        <Alert type="error">{list.error}</Alert>
        {!list.loading && (list.data || []).length === 0 && <Empty icon="🧀" title="No toppings yet" />}
        <ul className="plain-list">
          {(list.data || []).map((t) => (
            <li key={t.id} className="inline spread">
              <span>
                <strong>{t.name}</strong> <span className="muted">+{money(t.extra_price)}</span>
              </span>
              <span className="inline">
                <StatusBadge status={t.is_available ? "Available" : "Unavailable"} />
                <button className="btn btn-ghost btn-sm" onClick={() => setEditing(t)}>
                  Edit
                </button>
              </span>
            </li>
          ))}
        </ul>
      </section>

      {isAdmin && (
        <section className="card">
          <h2>Add topping</h2>
          <ToppingForm key={formKey} label="Create topping" busy={busy} onSubmit={create} initial={{ name: "", extra_price: "", is_available: true }} />
        </section>
      )}

      {editing && (
        <Modal title={`Edit ${editing.name}`} onClose={() => setEditing(null)}>
          <Message message={message} />
          <ToppingForm label="Save topping" busy={busy} onSubmit={update} initial={{ name: editing.name, extra_price: editing.extra_price, is_available: editing.is_available }} />
        </Modal>
      )}
    </div>
  );
}

// ── Page ────────────────────────────────────────────────────────
const TABS = [
  { key: "pizzas", label: "Pizzas", Comp: PizzasTab },
  { key: "categories", label: "Categories", Comp: CategoriesTab },
  { key: "toppings", label: "Toppings", Comp: ToppingsTab },
];

export default function AdminMenu() {
  const { isAdmin } = useAuth();
  const [tab, setTab] = useState("pizzas");
  const Active = TABS.find((t) => t.key === tab).Comp;

  return (
    <>
      <PageHeader title="Manage menu" subtitle={isAdmin ? "Pizzas, categories and toppings." : "Staff can change availability, edit toppings and remove pizzas."} />
      <div className="tabs" role="tablist">
        {TABS.map((t) => (
          <button key={t.key} role="tab" aria-selected={tab === t.key} className={`tab${tab === t.key ? " active" : ""}`} onClick={() => setTab(t.key)}>
            {t.label}
          </button>
        ))}
      </div>
      <Active isAdmin={isAdmin} />
    </>
  );
}
