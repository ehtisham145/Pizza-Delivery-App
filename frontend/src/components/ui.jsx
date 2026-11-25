import { useCallback, useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { AlertCircle, CheckCircle2, Info, Minus, Plus, X } from "lucide-react";

// ── Formatting helpers ──────────────────────────────────────────
export const money = (v) => `Rs ${Number(v || 0).toLocaleString("en-PK", { maximumFractionDigits: 2 })}`;
export const dateTime = (v) => (v ? new Date(v).toLocaleString() : "—");
export const shortId = (id) => (id ? String(id).slice(0, 8) : "—");

// ── Data loading hook ───────────────────────────────────────────
export function useLoad(loader, deps = []) {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const reload = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setData(await loader());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, deps);

  useEffect(() => {
    reload();
  }, [reload]);

  return { data, setData, error, loading, reload };
}

// Wraps an async action with busy state + message reporting.
export function useAction() {
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState(null); // { type, text }

  const run = useCallback(async (fn, successText) => {
    setBusy(true);
    setMessage(null);
    try {
      const result = await fn();
      if (successText) setMessage({ type: "success", text: successText });
      return result;
    } catch (err) {
      setMessage({ type: "error", text: err.message });
      return undefined;
    } finally {
      setBusy(false);
    }
  }, []);

  return { busy, message, setMessage, run };
}

/** Prevents the page behind an overlay from scrolling. */
export function useLockBodyScroll(active) {
  useEffect(() => {
    if (!active) return undefined;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = prev;
    };
  }, [active]);
}

// ── Small UI pieces ─────────────────────────────────────────────
const ALERT_ICONS = { error: AlertCircle, success: CheckCircle2, info: Info };

export function Alert({ type = "info", children, onClose }) {
  if (!children) return null;
  const Icon = ALERT_ICONS[type] || Info;
  return (
    <motion.div
      initial={{ opacity: 0, y: -6 }}
      animate={{ opacity: 1, y: 0 }}
      className={`alert alert-${type}`}
      role={type === "error" ? "alert" : "status"}
    >
      <span className="flex items-start gap-2.5">
        <Icon className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
        <span>{children}</span>
      </span>
      {onClose && (
        <button type="button" className="alert-close" onClick={onClose} aria-label="Dismiss">
          <X className="h-4 w-4" />
        </button>
      )}
    </motion.div>
  );
}

export function Message({ message, onClose }) {
  if (!message) return null;
  return (
    <Alert type={message.type} onClose={onClose}>
      {message.text}
    </Alert>
  );
}

export function Spinner({ label = "Loading…", className = "" }) {
  return (
    <div className={`flex items-center gap-3 py-6 text-sm text-muted ${className}`} role="status">
      <span className="h-5 w-5 animate-spin rounded-full border-2 border-line border-t-brand-600" aria-hidden="true" />
      <span>{label}</span>
    </div>
  );
}

export function Skeleton({ className = "" }) {
  return <div className={`skeleton ${className}`} aria-hidden="true" />;
}

/** A stack of list-row skeletons for pages that load lists. */
export function ListSkeleton({ rows = 3 }) {
  return (
    <div className="flex flex-col gap-3" role="status" aria-label="Loading">
      {Array.from({ length: rows }, (_, i) => (
        <div key={i} className="card flex items-center gap-4">
          <Skeleton className="h-12 w-12 rounded-xl" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-4 w-1/3" />
            <Skeleton className="h-3 w-1/2" />
          </div>
          <Skeleton className="h-6 w-20 rounded-full" />
        </div>
      ))}
    </div>
  );
}

/** `icon` can be an emoji string or a lucide icon component. */
export function Empty({ icon = "🍕", title, children, action }) {
  const IconComp = typeof icon === "string" ? null : icon;
  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="empty">
      <div className="mb-4 grid h-20 w-20 place-items-center rounded-full bg-brand-soft text-4xl text-brand-600">
        {IconComp ? <IconComp className="h-9 w-9" aria-hidden="true" /> : <span aria-hidden="true">{icon}</span>}
      </div>
      <h3 className="text-lg">{title}</h3>
      {children && <p className="mt-1 max-w-sm text-sm">{children}</p>}
      {action && <div className="mt-5">{action}</div>}
    </motion.div>
  );
}

export function StatusBadge({ status }) {
  const key = String(status || "").toLowerCase().replace(/\s+/g, "-");
  return (
    <span className={`badge badge-${key}`}>
      <span className="h-1.5 w-1.5 rounded-full bg-current opacity-70" aria-hidden="true" />
      {status}
    </span>
  );
}

export function PageHeader({ title, subtitle, actions, eyebrow }) {
  return (
    <div className="page-header">
      <div>
        {eyebrow && <p className="mb-1 text-xs font-bold uppercase tracking-widest text-brand-ink">{eyebrow}</p>}
        <h1>{title}</h1>
        {subtitle && <p className="muted">{subtitle}</p>}
      </div>
      {actions && <div className="page-actions">{actions}</div>}
    </div>
  );
}

/** Centred dialog on desktop, bottom sheet on mobile. */
export function Modal({ title, onClose, children, size = "md", bare = false }) {
  useLockBodyScroll(true);
  useEffect(() => {
    const onKey = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const width = size === "lg" ? "sm:max-w-3xl" : "sm:max-w-lg";

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 z-50 flex items-end justify-center bg-black/50 backdrop-blur-sm sm:items-center sm:p-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onMouseDown={onClose}
      >
        <motion.div
          role="dialog"
          aria-modal="true"
          aria-label={title}
          onMouseDown={(e) => e.stopPropagation()}
          initial={{ opacity: 0, y: 40, scale: 0.98 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 40 }}
          transition={{ type: "spring", damping: 28, stiffness: 320 }}
          className={`relative max-h-[92vh] w-full overflow-y-auto rounded-t-3xl bg-surface shadow-pop sm:rounded-3xl ${width} ${bare ? "" : "p-5 pb-safe sm:p-6"}`}
        >
          {bare ? (
            <>
              <button
                type="button"
                onClick={onClose}
                aria-label="Close"
                className="absolute right-3 top-3 z-10 grid h-10 w-10 place-items-center rounded-full bg-black/40 text-white backdrop-blur transition hover:bg-black/60"
              >
                <X className="h-5 w-5" />
              </button>
              {children}
            </>
          ) : (
            <>
              <div className="mx-auto -mt-1 mb-3 h-1.5 w-10 rounded-full bg-line sm:hidden" aria-hidden="true" />
              <div className="mb-5 flex items-center justify-between gap-3">
                <h2 className="text-xl">{title}</h2>
                <button type="button" className="icon-btn h-9 w-9 border-0 bg-surface-2" onClick={onClose} aria-label="Close">
                  <X className="h-4 w-4" />
                </button>
              </div>
              {children}
            </>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}

/** Friendly text for the browser's built-in constraint checks. */
function constraintMessage(el) {
  const v = el.validity;
  if (!v || v.valid) return "";
  if (v.valueMissing) return el.tagName === "SELECT" ? "Please choose an option." : "This field is required.";
  if (v.tooShort) return `Use at least ${el.minLength} characters (you have ${el.value.length}).`;
  if (v.tooLong) return `Use at most ${el.maxLength} characters.`;
  if (v.patternMismatch) return el.title || (el.inputMode === "numeric" ? "Enter numbers only, in the format shown." : "Please match the requested format.");
  if (v.typeMismatch) return el.type === "email" ? "Enter a valid email, like name@example.com." : el.type === "url" ? "Enter a valid link starting with https://" : "Please enter a valid value.";
  if (v.rangeUnderflow) return `Must be at least ${el.min}.`;
  if (v.rangeOverflow) return `Must be at most ${el.max}.`;
  if (v.stepMismatch || v.badInput) return "Please enter a valid number.";
  return el.validationMessage;
}

// `error` shows below the input in place of the hint. Pass the same `id` you
// give the input so the message is linked via aria-describedby.
//
// Inputs that only use native rules (required, minLength, pattern, type…) get
// the same styled message: the browser's bubble is suppressed, the message
// appears when the field is left or the form is submitted, and it updates live
// on every keystroke after that. An explicit `error` prop always wins.
export function Field({ label, hint, error, id, children }) {
  const msgId = id ? `${id}-msg` : undefined;
  const [nativeError, setNativeError] = useState("");
  const [armed, setArmed] = useState(false); // show messages after first blur/submit

  const sync = (el, show) => {
    if (!el?.validity || error) return;
    const msg = show ? constraintMessage(el) : "";
    setNativeError(msg);
    if (msg) el.setAttribute("aria-invalid", "true");
    else el.removeAttribute("aria-invalid");
  };

  const onInvalidCapture = (e) => {
    e.preventDefault(); // no native bubble
    setArmed(true);
    sync(e.target, true);
    // Keep the browser's behaviour of focusing the first invalid control.
    const first = e.target.form?.querySelector(":invalid");
    if (first === e.target) e.target.focus();
  };
  const onBlurCapture = (e) => {
    if (!e.target.validity) return;
    setArmed(true);
    sync(e.target, true);
  };
  const onInputCapture = (e) => armed && sync(e.target, true);

  const shown = error || nativeError;

  return (
    <label
      className={`field${shown ? " has-error" : ""}`}
      htmlFor={id}
      onInvalidCapture={onInvalidCapture}
      onBlurCapture={onBlurCapture}
      onInputCapture={onInputCapture}
      onChangeCapture={onInputCapture}
    >
      <span className="field-label">{label}</span>
      {children}
      <AnimatePresence initial={false} mode="wait">
        {shown ? (
          <motion.span
            key={shown}
            className="field-error"
            id={msgId}
            role="alert"
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.15 }}
          >
            <AlertCircle className="mt-[1px] h-3.5 w-3.5 shrink-0" aria-hidden="true" />
            {shown}
          </motion.span>
        ) : (
          hint && (
            <span className="field-hint" id={msgId}>
              {hint}
            </span>
          )
        )}
      </AnimatePresence>
    </label>
  );
}

/** − n + control with an animated number. */
export function QtyStepper({ value, onChange, min = 1, max = 10, disabled = false, size = "md", label = "Quantity" }) {
  const btn = size === "sm" ? "h-8 w-8" : "h-10 w-10";
  return (
    <div className="inline-flex items-center rounded-full border border-line bg-surface p-0.5" role="group" aria-label={label}>
      <button
        type="button"
        className={`${btn} grid place-items-center rounded-full text-ink transition hover:bg-surface-2 active:scale-90 disabled:opacity-35`}
        onClick={() => onChange(value - 1)}
        disabled={disabled || value <= min}
        aria-label="Decrease quantity"
      >
        <Minus className="h-4 w-4" />
      </button>
      <span className="relative w-8 overflow-hidden text-center font-semibold tabular-nums" aria-live="polite">
        <AnimatePresence mode="popLayout" initial={false}>
          <motion.span
            key={value}
            className="block"
            initial={{ y: 12, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: -12, opacity: 0 }}
            transition={{ duration: 0.15 }}
          >
            {value}
          </motion.span>
        </AnimatePresence>
      </span>
      <button
        type="button"
        className={`${btn} grid place-items-center rounded-full text-ink transition hover:bg-surface-2 active:scale-90 disabled:opacity-35`}
        onClick={() => onChange(value + 1)}
        disabled={disabled || value >= max}
        aria-label="Increase quantity"
      >
        <Plus className="h-4 w-4" />
      </button>
    </div>
  );
}
