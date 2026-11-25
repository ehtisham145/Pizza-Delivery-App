import { useRef, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { ArrowRight, Lock, Mail } from "lucide-react";
import { homeFor, useAuth } from "../context/AuthContext";
import { Alert } from "../components/ui";
import { HERO_IMAGES } from "../lib/images";
import AuthLayout, { PasswordToggle } from "../components/auth/AuthLayout";
import FloatField from "../components/auth/FloatField";
import { validateEmail } from "../validation";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ email: location.state?.email || "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  // Live validation: a field shows its message once it has been left (or on
  // submit), then updates on every keystroke.
  const [touched, setTouched] = useState({});
  const emailRef = useRef(null);
  const passwordRef = useRef(null);
  const errors = {
    email: validateEmail(form.email),
    password: form.password ? "" : "Enter your password.",
  };
  const show = (k) => (touched[k] ? errors[k] : "");
  const touch = (k) => () => setTouched((t) => ({ ...t, [k]: true }));

  const submit = async (e) => {
    e.preventDefault();
    setTouched({ email: true, password: true });
    if (errors.email || errors.password) {
      (errors.email ? emailRef : passwordRef).current?.focus();
      return;
    }
    setBusy(true);
    setError("");
    try {
      const user = await login(form.email.trim(), form.password);
      const home = homeFor(user?.role);
      // Only return to the requested page if it belongs to this user's side of the app.
      const from = location.state?.from;
      const sameSide = from && from.startsWith("/admin") === home.startsWith("/admin");
      navigate(sameSide ? from : home, { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <AuthLayout image={HERO_IMAGES.login} title="Welcome back" subtitle="Log in to order your favourite pizza.">
      <form onSubmit={submit} noValidate>
        <Alert type="error">{error}</Alert>
        {location.state?.passwordReset && !error && (
          <Alert type="success">Password updated! Log in with your new password.</Alert>
        )}
        {location.state?.registered && !error && (
          <Alert type="success">Account created! Log in to start ordering.</Alert>
        )}

        <FloatField
          id="login-email"
          label="Email address"
          icon={Mail}
          ref={emailRef}
          type="email"
          autoComplete="email"
          inputMode="email"
          value={form.email}
          onChange={(e) => {
            setForm({ ...form, email: e.target.value });
            if (error) setError("");
          }}
          onBlur={touch("email")}
          error={show("email")}
          valid={touched.email && !errors.email}
        />
        <FloatField
          id="login-password"
          label="Password"
          icon={Lock}
          ref={passwordRef}
          type={showPassword ? "text" : "password"}
          autoComplete="current-password"
          value={form.password}
          onChange={(e) => {
            setForm({ ...form, password: e.target.value });
            if (error) setError("");
          }}
          onBlur={touch("password")}
          error={show("password")}
          trailing={<PasswordToggle shown={showPassword} onToggle={() => setShowPassword((s) => !s)} />}
        />
        <div className="-mt-2 mb-4 flex justify-end">
          <Link to="/forgot-password" state={{ email: form.email.trim() }} className="text-sm font-semibold">
            Forgot password?
          </Link>
        </div>

        <button className="btn btn-primary btn-block mt-2 h-12 text-base" disabled={busy}>
          {busy ? (
            <>
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" /> Logging in…
            </>
          ) : (
            <>
              Log in <ArrowRight className="h-5 w-5" aria-hidden="true" />
            </>
          )}
        </button>
      </form>

      <p className="mt-8 text-center text-sm text-muted">
        New here?{" "}
        <Link to="/register" className="font-semibold">
          Create an account
        </Link>
      </p>
    </AuthLayout>
  );
}
