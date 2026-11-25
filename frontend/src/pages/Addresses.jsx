import { useState } from "react";
import { addressApi } from "../api/endpoints";
import { ADDRESS_LABELS } from "../constants";
import { Alert, Empty, Field, Message, Modal, PageHeader, Spinner, useAction, useLoad } from "../components/ui";

const blank = { label: "Home", street: "", city: "", zip_code: "", is_default: false };

function AddressForm({ initial, onSubmit, busy }) {
  const [form, setForm] = useState(initial);
  const set = (key) => (e) => setForm({ ...form, [key]: e.target.type === "checkbox" ? e.target.checked : e.target.value });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit({ ...form, street: form.street.trim(), city: form.city.trim() });
      }}
    >
      <Field label="Label">
        <select value={form.label} onChange={set("label")}>
          {ADDRESS_LABELS.map((l) => (
            <option key={l}>{l}</option>
          ))}
        </select>
      </Field>
      <Field label="Street">
        <input required minLength={3} maxLength={150} value={form.street} onChange={set("street")} placeholder="123 Pizza Street, Sector G" />
      </Field>
      <div className="grid-2">
        <Field label="City">
          <input required minLength={3} maxLength={100} value={form.city} onChange={set("city")} placeholder="Islamabad" />
        </Field>
        <Field label="ZIP code" hint="5 digits">
          <input required pattern="\d{5}" title="Enter a 5-digit ZIP code, like 44000." inputMode="numeric" maxLength={5} value={form.zip_code} onChange={set("zip_code")} placeholder="44000" />
        </Field>
      </div>
      <label className="checkbox">
        <input type="checkbox" checked={form.is_default} onChange={set("is_default")} /> Make this my default address
      </label>
      <button className="btn btn-primary btn-block" disabled={busy}>
        Save address
      </button>
    </form>
  );
}

export default function Addresses() {
  const list = useLoad(() => addressApi.list());
  const { busy, message, setMessage, run } = useAction();
  const [editing, setEditing] = useState(null); // null | "new" | address

  const save = async (data) => {
    const ok =
      editing === "new"
        ? await run(() => addressApi.add(data), "Address added.")
        : await run(() => addressApi.update(editing.id, data), "Address updated.");
    if (ok) {
      setEditing(null);
      list.reload();
    }
  };

  const makeDefault = async (a) => {
    await run(() => addressApi.setDefault(a.id), "Default address updated.");
    list.reload();
  };

  const remove = async (a) => {
    if (!window.confirm(`Delete the "${a.label}" address?`)) return;
    await run(() => addressApi.remove(a.id), "Address deleted.");
    list.reload();
  };

  const addresses = list.data || [];
  return (
    <>
      <PageHeader
        title="Delivery addresses"
        subtitle="You can save up to 5 addresses."
        actions={
          <button className="btn btn-primary" onClick={() => setEditing("new")} disabled={addresses.length >= 5}>
            + Add address
          </button>
        }
      />
      <Message message={message} onClose={() => setMessage(null)} />
      {list.loading && <Spinner />}
      <Alert type="error">{list.error}</Alert>
      {!list.loading && !list.error && addresses.length === 0 && <Empty icon="📍" title="No saved addresses yet" />}

      <div className="card-grid">
        {addresses.map((a) => (
          <article key={a.id} className={`card address${a.is_default ? " is-default" : ""}`}>
            <div className="card-head">
              <h3>{a.label}</h3>
              {a.is_default && <span className="badge badge-paid">Default</span>}
            </div>
            <p>{a.street}</p>
            <p className="muted">
              {a.city} · {a.zip_code}
            </p>
            <div className="row-actions">
              {!a.is_default && (
                <button className="btn btn-ghost btn-sm" onClick={() => makeDefault(a)} disabled={busy}>
                  Set default
                </button>
              )}
              <button className="btn btn-ghost btn-sm" onClick={() => setEditing(a)}>
                Edit
              </button>
              <button className="btn btn-ghost btn-sm danger" onClick={() => remove(a)} disabled={busy}>
                Delete
              </button>
            </div>
          </article>
        ))}
      </div>

      {editing && (
        <Modal title={editing === "new" ? "New address" : "Edit address"} onClose={() => setEditing(null)}>
          <Message message={message} />
          <AddressForm
            initial={editing === "new" ? blank : { label: editing.label, street: editing.street, city: editing.city, zip_code: editing.zip_code, is_default: editing.is_default }}
            onSubmit={save}
            busy={busy}
          />
        </Modal>
      )}
    </>
  );
}
