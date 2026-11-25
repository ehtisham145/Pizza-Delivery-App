import { forwardRef } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { AlertCircle, CheckCircle2 } from "lucide-react";

/**
 * Input with a floating label and live validation states.
 * - `error`: red border, red label/icon and an animated message below.
 * - `valid`: green border/icon once the value passes validation.
 * `trailing` renders inside the input on the right (e.g. a show/hide toggle).
 * Messages use id `${id}-msg`, linked through aria-describedby.
 */
const FloatField = forwardRef(function FloatField({ id, label, icon: Icon, error, hint, valid = false, trailing, className = "", ...input }, ref) {
  const msgId = `${id}-msg`;
  const state = error ? "error" : valid ? "valid" : "idle";

  const border = {
    error: "border-brand-600 bg-brand-soft/40 focus:border-brand-600 focus:ring-brand-600/20",
    valid: "border-emerald-500/70 focus:border-emerald-500 focus:ring-emerald-500/15",
    idle: "",
  }[state];
  const iconColor = { error: "text-brand-600", valid: "text-emerald-500", idle: "text-muted" }[state];
  const labelColor = {
    error: "text-brand-600 peer-focus:text-brand-600",
    valid: "text-muted peer-focus:text-emerald-600 dark:peer-focus:text-emerald-400",
    idle: "text-muted peer-focus:text-ink",
  }[state];

  return (
    <div className={`mb-4 ${className}`}>
      <div className="relative">
        {Icon && (
          <Icon className={`pointer-events-none absolute left-4 top-1/2 z-10 h-[18px] w-[18px] -translate-y-1/2 transition-colors ${iconColor}`} aria-hidden="true" />
        )}
        <input
          id={id}
          ref={ref}
          placeholder=" "
          aria-invalid={error ? true : undefined}
          aria-describedby={error || hint ? msgId : undefined}
          {...input}
          className={`peer h-14 rounded-xl bg-surface pb-1.5 pt-5 transition-[border-color,box-shadow,background-color] ${Icon ? "pl-11" : "pl-4"} ${
            trailing || state !== "idle" ? "pr-12" : "pr-4"
          } ${border}`}
        />
        <label
          htmlFor={id}
          className={`pointer-events-none absolute top-1/2 -translate-y-1/2 text-[0.95rem] transition-all duration-150
            ${Icon ? "left-11" : "left-4"} ${labelColor}
            peer-focus:top-[0.95rem] peer-focus:text-[0.72rem] peer-focus:font-semibold
            peer-[:not(:placeholder-shown)]:top-[0.95rem] peer-[:not(:placeholder-shown)]:text-[0.72rem] peer-[:not(:placeholder-shown)]:font-semibold
            peer-autofill:top-[0.95rem] peer-autofill:text-[0.72rem] peer-autofill:font-semibold`}
        >
          {label}
        </label>
        <div className="absolute right-1.5 top-1/2 flex -translate-y-1/2 items-center">
          {trailing ||
            (state !== "idle" && (
              <span className="grid h-10 w-10 place-items-center" aria-hidden="true">
                {state === "error" ? (
                  <AlertCircle className="h-[18px] w-[18px] text-brand-600" />
                ) : (
                  <CheckCircle2 className="h-[18px] w-[18px] text-emerald-500" />
                )}
              </span>
            ))}
        </div>
      </div>

      <AnimatePresence initial={false} mode="wait">
        {error ? (
          <motion.p
            key={`e-${error}`}
            id={msgId}
            role="alert"
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.15 }}
            className="mt-1.5 flex items-start gap-1.5 text-[0.8rem] font-medium text-brand-600 dark:text-brand-400"
          >
            <AlertCircle className="mt-[1px] h-3.5 w-3.5 shrink-0" aria-hidden="true" />
            {error}
          </motion.p>
        ) : (
          hint && (
            <motion.p key="hint" id={msgId} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="mt-1.5 text-xs text-muted">
              {hint}
            </motion.p>
          )
        )}
      </AnimatePresence>
    </div>
  );
});

export default FloatField;
