import { useEffect, useState } from "react";
import { profileApi } from "../api/endpoints";
import { useAuth } from "../context/AuthContext";
import { Field, Message, PageHeader, StatusBadge, useAction } from "../components/ui";
import { PASSWORD_RULES, normalizePhone, validateConfirm, validateFullName, validatePassword, validatePhone } from "../validation";

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

  // Errors appear after the first save attempt, then update live while typing.
  const [detailTried, setDetailTried] = useState(false);
  const [pwTried, setPwTried] = useState(false);
  const detailCheck = { full_name: validateFullName(form.full_name), phone_number: validatePhone(form.phone_number) };
  const pwCheck = {
    old_password: pw.old_password ? "" : "Enter your current password.",
    new_password: validatePassword(pw.new_password),
    confirm_new_password: validateConfirm(pw.new_password, pw.confirm_new_password),
  };
  const detailErrors = detailTried ? detailCheck : {};
  const pwErrors = pwTried ? pwCheck : {};

  const saveDetails = async (e) => {
    e.preventDefault();
    setDetailTried(true);
    if (detailCheck.full_name || detailCheck.phone_number) return;
    const res = await details.run(
      () => profileApi.update({ full_name: form.full_name.trim(), phone_number: normalizePhone(form.phone_number) }),
      "Profile updated."
    );
    if (res) refreshProfile().catch(() => {});
  };

  const savePassword = async (e) => {
    e.preventDefault();
    setPwTried(true);
    if (Object.values(pwCheck).some(Boolean)) return;
    const res = await password.run(() => profileApi.changePassword(pw), "Password changed.");
    if (res) {
      setPw({ old_password: "", new_password: "", confirm_new_password: "" });
      setPwTried(false);
    }
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

          <form onSubmit={saveDetails} noValidate>
            <Message message={details.message} onClose={() => details.setMessage(null)} />
            <Field label="Full name" hint="5–20 characters" error={detailErrors.full_name} id="pf-name">
              <input id="pf-name" autoComplete="name" aria-invalid={Boolean(detailErrors.full_name) || undefined} maxLength={20} value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
            </Field>
            <Field label="Mobile number" hint="Include your country code, e.g. +44 7911 123456" error={detailErrors.phone_number} id="pf-phone">
              <input id="pf-phone" type="tel" inputMode="tel" autoComplete="tel" aria-invalid={Boolean(detailErrors.phone_number) || undefined} value={form.phone_number} onChange={(e) => setForm({ ...form, phone_number: e.target.value })} />
            </Field>
            <button className="btn btn-primary" disabled={details.busy}>
              Save changes
            </button>
          </form>
        </section>

        <section className="card">
          <h2>Change password</h2>
          <form onSubmit={savePassword} noValidate>
            <Message message={password.message} onClose={() => password.setMessage(null)} />
            <Field label="Current password" error={pwErrors.old_password} id="pf-old">
              <input id="pf-old" type="password" autoComplete="current-password" aria-invalid={Boolean(pwErrors.old_password) || undefined} value={pw.old_password} onChange={(e) => setPw({ ...pw, old_password: e.target.value })} />
            </Field>
            <Field label="New password" error={pwErrors.new_password} id="pf-new">
              <input id="pf-new" type="password" autoComplete="new-password" aria-invalid={Boolean(pwErrors.new_password) || undefined} value={pw.new_password} onChange={(e) => setPw({ ...pw, new_password: e.target.value })} />
            </Field>
            <ul className="pw-rules" aria-label="Password requirements">
              {PASSWORD_RULES.map((r) => {
                const ok = r.test(pw.new_password);
                return (
                  <li key={r.key} className={ok ? "ok" : pw.new_password ? "missing" : ""}>
                    <span aria-hidden="true">{ok ? "✓" : "•"}</span> {r.label}
                  </li>
                );
              })}
            </ul>
            <Field label="Confirm new password" error={pwErrors.confirm_new_password} id="pf-confirm">
              <input id="pf-confirm" type="password" autoComplete="new-password" aria-invalid={Boolean(pwErrors.confirm_new_password) || undefined} value={pw.confirm_new_password} onChange={(e) => setPw({ ...pw, confirm_new_password: e.target.value })} />
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
