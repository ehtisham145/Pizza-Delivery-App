import { useEffect, useRef, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, ArrowRight, Mail, MailCheck } from "lucide-react";
import { authApi } from "../api/endpoints";
import { Alert } from "../components/ui";
import { HERO_IMAGES } from "../lib/images";
import AuthLayout from "../components/auth/AuthLayout";
import FloatField from "../components/auth/FloatField";
import { validateEmail } from "../validation";

const COOLDOWN = 60; // matches the backend's resend throttle

export default function ForgotPassword() {
  const location = useLocation();
  const [email, setEmail] = useState(location.state?.email || "");
  const [touched, setTouched] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [sentTo, setSentTo] = useState("");
  const [cooldown, setCooldown] = useState(0);
  const inputRef = useRef(null);

  const emailError = validateEmail(email);

  useEffect(() => {
    if (!cooldown) return undefined;
    const t = setTimeout(() => setCooldown((c) => c - 1), 1000);
    return () => clearTimeout(t);
  }, [cooldown]);

  const send = async (e) => {
    e?.preventDefault();
    setTouched(true);
    if (emailError) {
      inputRef.current?.focus();
      return;
    }
    setBusy(true);
    setError("");
    try {
      await authApi.forgotPassword(email.trim());
      setSentTo(email.trim());
      setCooldown(COOLDOWN);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  if (sentTo) {
    return (
      <AuthLayout image={HERO_IMAGES.login} title="Check your email" subtitle="We've sent you a link to reset your password.">
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
          <div className="mb-6 flex items-start gap-4 rounded-2xl border border-line bg-surface-2 p-5">
            <span className="grid h-12 w-12 shrink-0 place-items-center rounded-full bg-emerald-500/15 text-emerald-600 dark:text-emerald-400">
              <MailCheck className="h-6 w-6" aria-hidden="true" />
            </span>
            <div className="text-sm">
              <p className="text-ink">
                If an account exists for <strong className="break-all">{sentTo}</strong>, a reset link is on its way.
              </p>
              <p className="mt-2 text-muted">The link works for 30 minutes. Don't forget to check your spam folder.</p>
            </div>
          </div>
          <Alert type="error">{error}</Alert>

          <button type="button" className="btn btn-secondary btn-block h-12" onClick={send} disabled={busy || cooldown > 0}>
            {busy ? "Sending…" : cooldown > 0 ? `Resend link in ${cooldown}s` : "Resend link"}
          </button>
          <button
            type="button"
            className="btn btn-ghost btn-block mt-2"
            onClick={() => {
              setSentTo("");
              setCooldown(0);
            }}
          >
            Use a different email
          </button>
        </motion.div>

        <p className="mt-8 text-center text-sm text-muted">
          <Link to="/login" state={{ email: sentTo }} className="inline-flex items-center gap-1.5 font-semibold">
            <ArrowLeft className="h-4 w-4" /> Back to log in
          </Link>
        </p>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout image={HERO_IMAGES.login} title="Forgot your password?" subtitle="Enter your account email and we'll send you a link to set a new one.">
      <form onSubmit={send} noValidate>
        <Alert type="error">{error}</Alert>
        <FloatField
          id="forgot-email"
          ref={inputRef}
          label="Email address"
          icon={Mail}
          type="email"
          autoComplete="email"
          inputMode="email"
          autoFocus
          value={email}
          onChange={(e) => {
            setEmail(e.target.value);
            if (error) setError("");
          }}
          onBlur={() => setTouched(true)}
          error={touched ? emailError : ""}
          valid={touched && !emailError}
        />
        <button className="btn btn-primary btn-block mt-2 h-12 text-base" disabled={busy}>
          {busy ? (
            <>
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" /> Sending link…
            </>
          ) : (
            <>
              Send reset link <ArrowRight className="h-5 w-5" aria-hidden="true" />
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
