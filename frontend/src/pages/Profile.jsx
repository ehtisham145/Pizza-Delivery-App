import { useEffect, useState } from "react";
import { profileApi } from "../api/endpoints";
import { useAuth } from "../context/AuthContext";
import { Field, Message, PageHeader, StatusBadge, useAction } from "../components/ui";

export default function Profile() {
  const { user, refreshProfile } = useAuth();
  const details = useAction();
  const password = useAction();
  const [form, setForm] = useState({ full_name: "", phone_number: "" });
  const [pw, setPw] = useState({ old_password: "", new_password: "", confirm_new_password: "" });

  useEffect(() => {
    refreshProfile().catch(() => {});
  }, [refreshProfile]);

  useEffect(() => {
    if (user) setForm({ full_name: user.full_name || "", phone_number: user.phone_number || "" });
  }, [user]);

  const saveDetails = async (e) => {
    e.preventDefault();
    const res = await details.run(
      () => profileApi.update({ full_name: form.full_name.trim(), phone_number: form.phone_number.trim() }),
      "Profile updated."
    );
    if (res) refreshProfile().catch(() => {});
  };

  const savePassword = async (e) => {
    e.preventDefault();
    if (pw.new_password !== pw.confirm_new_password) {
      password.setMessage({ type: "error", text: "New passwords do not match." });
      return;
    }
    const res = await password.run(() => profileApi.changePassword(pw), "Password changed.");
    if (res) setPw({ old_password: "", new_password: "", confirm_new_password: "" });
  };

  return (
    <>
      <PageHeader title="My profile" />
      <div className="grid-2 align-start">
        <section className="card">
          <h2>Account</h2>
          <dl className="details">
            <dt>Email</dt>
            <dd>{user?.email}</dd>
            <dt>Role</dt>
            <dd>{user?.role}</dd>
            <dt>Status</dt>
            <dd>
              <StatusBadge status={user?.is_active === false ? "Inactive" : "Active"} />
            </dd>
          </dl>

          <form onSubmit={saveDetails}>
            <Message message={details.message} onClose={() => details.setMessage(null)} />
            <Field label="Full name" hint="5–20 characters">
              <input required minLength={5} maxLength={20} value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
            </Field>
            <Field label="Phone number">
              <input required value={form.phone_number} onChange={(e) => setForm({ ...form, phone_number: e.target.value })} />
            </Field>
            <button className="btn btn-primary" disabled={details.busy}>
              Save changes
            </button>
          </form>
        </section>

        <section className="card">
          <h2>Change password</h2>
          <form onSubmit={savePassword}>
            <Message message={password.message} onClose={() => password.setMessage(null)} />
            <Field label="Current password">
              <input type="password" required autoComplete="current-password" value={pw.old_password} onChange={(e) => setPw({ ...pw, old_password: e.target.value })} />
            </Field>
            <Field label="New password" hint="8+ chars with upper, lower, number and one of @$!%*?&">
              <input type="password" required minLength={8} autoComplete="new-password" value={pw.new_password} onChange={(e) => setPw({ ...pw, new_password: e.target.value })} />
            </Field>
            <Field label="Confirm new password">
              <input type="password" required autoComplete="new-password" value={pw.confirm_new_password} onChange={(e) => setPw({ ...pw, confirm_new_password: e.target.value })} />
            </Field>
            <button className="btn btn-primary" disabled={password.busy}>
              Update password
            </button>
          </form>
        </section>
      </div>
    </>
  );
}
