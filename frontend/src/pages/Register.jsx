import { useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowRight, Lock, Mail, Phone, User } from "lucide-react";
import { authApi } from "../api/endpoints";
import { useAuth } from "../context/AuthContext";
import { Alert } from "../components/ui";
import { HERO_IMAGES } from "../lib/images";
import AuthLayout, { PasswordToggle } from "../components/auth/AuthLayout";
import FloatField from "../components/auth/FloatField";
import PasswordStrength from "../components/auth/PasswordStrength";
import {
  fieldErrorsFromApi,
  normalizePhone,
  validateConfirm,
  validateEmail,
  validateFullName,
  validatePassword,
  validatePhone,
} from "../validation";

const FIELDS = ["full_name", "email", "phone_number", "password", "confirm"];
function validate(form) {
  return {
    full_name: validateFullName(form.full_name),
    email: validateEmail(form.email),
    phone_number: validatePhone(form.phone_number),
    password: validatePassword(form.password),
    confirm: validateConfirm(form.password, form.confirm),
  };
}

export default function Register() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [form, setForm] = useState({ full_name: "", email: "", phone_number: "", password: "", confirm: "" });
  const [touched, setTouched] = useState({});
  const [serverErrors, setServerErrors] = useState({});
  const [formError, setFormError] = useState("");
  const [busy, setBusy] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const refs = useRef({});

  const clientErrors = validate(form);
  // Show a field's error once the user has left it (or tried to submit).
  const errorFor = (key) => serverErrors[key] || (touched[key] ? clientErrors[key] : "");

  const bind = (key) => ({
    id: `reg-${key}`,
    name: key,
    ref: (el) => (refs.current[key] = el),
    value: form[key],
    onChange: (e) => {
      setForm((f) => ({ ...f, [key]: e.target.value }));
      if (serverErrors[key]) setServerErrors((s) => ({ ...s, [key]: "" }));
    },
    onBlur: () => setTouched((t) => ({ ...t, [key]: true })),
    error: errorFor(key),
    valid: Boolean(touched[key] && !errorFor(key) && form[key]),
  });

  const submit = async (e) => {
    e.preventDefault();
    setFormError("");
    setTouched(Object.fromEntries(FIELDS.map((k) => [k, true])));

    const firstInvalid = FIELDS.find((k) => clientErrors[k]);
    if (firstInvalid) {
      refs.current[firstInvalid]?.focus();
      return;
    }

    setBusy(true);
    try {
      await authApi.register({
        full_name: form.full_name.trim(),
        email: form.email.trim(),
        phone_number: normalizePhone(form.phone_number),
        password: form.password,
      });
      // Accounts are active straight away, so sign the user in and take them to the menu.
      try {
        await login(form.email.trim(), form.password);
        navigate("/menu", { replace: true });
      } catch {
        navigate("/login", { state: { registered: true, email: form.email.trim() } });
      }
    } catch (err) {
      const fields = fieldErrorsFromApi(err);
      if (/already registered/i.test(err.message)) fields.email = "An account with this email already exists. Try logging in.";
      const firstServer = FIELDS.find((k) => fields[k]);
      if (firstServer) {
        setServerErrors(fields);
        refs.current[firstServer]?.focus();
      } else {
        setFormError(err.message);
      }
    } finally {
      setBusy(false);
    }
  };


  return (
    <AuthLayout image={HERO_IMAGES.register} title="Create your account" subtitle="Join in a minute, then order in seconds.">
      <form onSubmit={submit} noValidate>
        <Alert type="error" onClose={() => setFormError("")}>
          {formError}
        </Alert>

        <FloatField {...bind("full_name")} label="Full name" icon={User} hint="5–20 characters" type="text" autoComplete="name" maxLength={20} />
        <FloatField {...bind("email")} label="Email address" icon={Mail} type="email" autoComplete="email" inputMode="email" />
        <FloatField
          {...bind("phone_number")}
         
          label="Mobile number"
          icon={Phone}
          hint="Any country — include the country code, e.g. +44 7911 123456"
          type="tel"
          autoComplete="tel"
          inputMode="tel"
          maxLength={24}
        />
        <FloatField
          {...bind("password")}
         
          label="Password"
          icon={Lock}
          type={showPassword ? "text" : "password"}
          autoComplete="new-password"
          className="mb-2"
          trailing={<PasswordToggle shown={showPassword} onToggle={() => setShowPassword((s) => !s)} />}
        />

        <PasswordStrength value={form.password} />

        <FloatField
          {...bind("confirm")}
         
          label="Confirm password"
          icon={Lock}
          type={showPassword ? "text" : "password"}
          autoComplete="new-password"
        />

        <button className="btn btn-primary btn-block mt-2 h-12 text-base" disabled={busy}>
          {busy ? (
            <>
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" /> Creating account…
            </>
          ) : (
            <>
              Create account <ArrowRight className="h-5 w-5" aria-hidden="true" />
            </>
          )}
        </button>
      </form>

      <p className="mt-8 text-center text-sm text-muted">
        Already registered?{" "}
        <Link to="/login" className="font-semibold">
          Log in
        </Link>
      </p>
    </AuthLayout>
  );
}
