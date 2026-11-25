import { useCallback, useEffect, useState } from "react";

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

// ── Small UI pieces ─────────────────────────────────────────────
export function Alert({ type = "info", children, onClose }) {
  if (!children) return null;
  return (
    <div className={`alert alert-${type}`} role={type === "error" ? "alert" : "status"}>
      <span>{children}</span>
      {onClose && (
        <button className="alert-close" onClick={onClose} aria-label="Dismiss">
          ×
        </button>
      )}
    </div>
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

export function Spinner({ label = "Loading…" }) {
  return (
    <div className="spinner-wrap">
      <span className="spinner" aria-hidden="true" />
      <span>{label}</span>
    </div>
  );
}

export function Empty({ icon = "🍕", title, children }) {
  return (
    <div className="empty">
      <div className="empty-icon">{icon}</div>
      <h3>{title}</h3>
      {children && <p>{children}</p>}
    </div>
  );
}

export function StatusBadge({ status }) {
  const key = String(status || "").toLowerCase().replace(/\s+/g, "-");
  return <span className={`badge badge-${key}`}>{status}</span>;
}

export function PageHeader({ title, subtitle, actions }) {
  return (
    <div className="page-header">
      <div>
        <h1>{title}</h1>
        {subtitle && <p className="muted">{subtitle}</p>}
      </div>
      {actions && <div className="page-actions">{actions}</div>}
    </div>
  );
}

export function Modal({ title, onClose, children }) {
  useEffect(() => {
    const onKey = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div className="modal-backdrop" onMouseDown={onClose}>
      <div className="modal" role="dialog" aria-modal="true" aria-label={title} onMouseDown={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <h2>{title}</h2>
          <button className="icon-btn" onClick={onClose} aria-label="Close">
            ×
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}

export function Field({ label, hint, children }) {
  return (
    <label className="field">
      <span className="field-label">{label}</span>
      {children}
      {hint && <span className="field-hint">{hint}</span>}
    </label>
  );
}
