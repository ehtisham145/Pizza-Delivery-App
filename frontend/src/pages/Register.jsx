import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { authApi } from "../api/endpoints";
import { Alert, Field } from "../components/ui";

export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ full_name: "", email: "", phone_number: "", password: "", confirm: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    if (form.password !== form.confirm) {
      setError("Passwords do not match.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      const { confirm, ...data } = form;
      await authApi.register({ ...data, full_name: data.full_name.trim(), email: data.email.trim() });
      navigate("/login", { state: { registered: true } });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={submit}>
        <div className="auth-brand">🍕</div>
        <h1>Create account</h1>
        <p className="muted">Sign up to start ordering.</p>

        <Alert type="error">{error}</Alert>

        <Field label="Full name" hint="5–20 characters">
          <input required minLength={5} maxLength={20} value={form.full_name} onChange={set("full_name")} />
        </Field>
        <Field label="Email">
          <input type="email" required autoComplete="email" value={form.email} onChange={set("email")} />
        </Field>
        <Field label="Phone number" hint="Pakistani mobile, e.g. 03001234567">
          <input required inputMode="tel" placeholder="03001234567" value={form.phone_number} onChange={set("phone_number")} />
        </Field>
        <Field label="Password" hint="8+ chars with upper, lower, number and one of @$!%*?&">
          <input type="password" required minLength={8} autoComplete="new-password" value={form.password} onChange={set("password")} />
        </Field>
        <Field label="Confirm password">
          <input type="password" required autoComplete="new-password" value={form.confirm} onChange={set("confirm")} />
        </Field>

        <button className="btn btn-primary btn-block" disabled={busy}>
          {busy ? "Creating account…" : "Create account"}
        </button>
        <p className="auth-switch">
          Already registered? <Link to="/login">Log in</Link>
        </p>
      </form>
    </div>
  );
}
