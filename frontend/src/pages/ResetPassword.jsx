import { useRef, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { ArrowLeft, ArrowRight, Lock, ShieldAlert } from "lucide-react";
import { authApi } from "../api/endpoints";
import { Alert } from "../components/ui";
import { HERO_IMAGES } from "../lib/images";
import AuthLayout, { PasswordToggle } from "../components/auth/AuthLayout";
import FloatField from "../components/auth/FloatField";
import PasswordStrength from "../components/auth/PasswordStrength";
import { fieldErrorsFromApi, validateConfirm, validatePassword } from "../validation";

export default function ResetPassword() {
  const [params] = useSearchParams();
  const token = params.get("token") || "";
  const navigate = useNavigate();
  const [form, setForm] = useState({ password: "", confirm: "" });
  const [touched, setTouched] = useState({});
  const [show, setShow] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [linkInvalid, setLinkInvalid] = useState(token.length < 20);
  const pwRef = useRef(null);
  const confirmRef = useRef(null);

  const errors = { password: validatePassword(form.password), confirm: validateConfirm(form.password, form.confirm) };
  const shown = (k) => (touched[k] ? errors[k] : "");
  const set = (k) => (e) => {
    setForm((f) => ({ ...f, [k]: e.target.value }));
    if (error) setError("");
  };

  const submit = async (e) => {
    e.preventDefault();
    setTouched({ password: true, confirm: true });
    if (errors.password || errors.confirm) {
      (errors.password ? pwRef : confirmRef).current?.focus();
      return;
    }
    setBusy(true);
    setError("");
    try {
      await authApi.resetPassword({ token, new_password: form.password, confirm_password: form.confirm });
      navigate("/login", { replace: true, state: { passwordReset: true } });
    } catch (err) {
      if (/invalid or has expired/i.test(err.message)) setLinkInvalid(true);
      else setError(fieldErrorsFromApi(err).new_password || err.message);
    } finally {
      setBusy(false);
    }
  };

  if (linkInvalid) {
    return (
      <AuthLayout image={HERO_IMAGES.login} title="Link expired" subtitle="This password reset link is invalid or has already been used.">
        <div className="mb-6 flex items-start gap-4 rounded-2xl border border-line bg-surface-2 p-5 text-sm">
          <span className="grid h-12 w-12 shrink-0 place-items-center rounded-full bg-brand-soft text-brand-600">
            <ShieldAlert className="h-6 w-6" aria-hidden="true" />
          </span>
          <p className="text-muted">Reset links work once and expire after 30 minutes. Request a new one and use the latest email we send.</p>
        </div>
        <Link to="/forgot-password" className="btn btn-primary btn-block h-12 text-base">
          Request a new link <ArrowRight className="h-5 w-5" aria-hidden="true" />
        </Link>
        <p className="mt-8 text-center text-sm text-muted">
          <Link to="/login" className="inline-flex items-center gap-1.5 font-semibold">
            <ArrowLeft className="h-4 w-4" /> Back to log in
          </Link>
        </p>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout image={HERO_IMAGES.login} title="Set a new password" subtitle="Choose a strong password you haven't used here before.">
      <form onSubmit={submit} noValidate>
        <Alert type="error">{error}</Alert>
        <FloatField
          id="reset-password"
          ref={pwRef}
          label="New password"
          icon={Lock}
          type={show ? "text" : "password"}
          autoComplete="new-password"
          autoFocus
          className="mb-2"
          value={form.password}
          onChange={set("password")}
          onBlur={() => setTouched((t) => ({ ...t, password: true }))}
          error={shown("password")}
          trailing={<PasswordToggle shown={show} onToggle={() => setShow((s) => !s)} />}
        />
        <PasswordStrength value={form.password} />
        <FloatField
          id="reset-confirm"
          ref={confirmRef}
          label="Confirm new password"
          icon={Lock}
          type={show ? "text" : "password"}
          autoComplete="new-password"
          value={form.confirm}
          onChange={set("confirm")}
          onBlur={() => setTouched((t) => ({ ...t, confirm: true }))}
          error={shown("confirm")}
          valid={touched.confirm && !errors.confirm}
        />
        <button className="btn btn-primary btn-block mt-2 h-12 text-base" disabled={busy}>
          {busy ? (
            <>
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" /> Updating…
            </>
          ) : (
            <>
              Update password <ArrowRight className="h-5 w-5" aria-hidden="true" />
            </>
          )}
        </button>
      </form>
      <p className="mt-8 text-center text-sm text-muted">
        <Link to="/login" className="inline-flex items-center gap-1.5 font-semibold">
          <ArrowLeft className="h-4 w-4" /> Back to log in
        </Link>
      </p>
    </AuthLayout>
  );
}
