import { Check } from "lucide-react";
import { PASSWORD_RULES } from "../../validation";

const STRENGTH = [
  { label: "Too weak", color: "bg-brand-600" },
  { label: "Weak", color: "bg-brand-500" },
  { label: "Fair", color: "bg-amber-500" },
  { label: "Good", color: "bg-amber-400" },
  { label: "Strong", color: "bg-emerald-500" },
];

/** Strength bar + live checklist of the backend's password rules. */
export default function PasswordStrength({ value }) {
  const started = value.length > 0;
  const passed = PASSWORD_RULES.filter((r) => r.test(value)).length;
  const strength = STRENGTH[Math.max(0, passed - 1)];

  return (
    <div className="mb-4">
      <div className="mb-2 flex items-center gap-2">
        <div className="flex flex-1 gap-1" aria-hidden="true">
          {PASSWORD_RULES.map((r, i) => (
            <span key={r.key} className={`h-1.5 flex-1 rounded-full transition-colors duration-300 ${started && i < passed ? strength.color : "bg-line"}`} />
          ))}
        </div>
        {started && <span className="w-16 text-right text-xs font-semibold text-muted">{strength.label}</span>}
      </div>
      <ul className="grid grid-cols-1 gap-1 text-xs sm:grid-cols-2" aria-label="Password requirements">
        {PASSWORD_RULES.map((r) => {
          const ok = r.test(value);
          return (
            <li key={r.key} className={`flex items-center gap-1.5 ${ok ? "text-emerald-600 dark:text-emerald-400" : started ? "text-brand-600" : "text-muted"}`}>
              <span className={`grid h-4 w-4 place-items-center rounded-full ${ok ? "bg-emerald-500 text-white" : "bg-surface-2"}`} aria-hidden="true">
                {ok && <Check className="h-2.5 w-2.5" strokeWidth={3.5} />}
              </span>
              {r.label}
              <span className="sr-only">{ok ? " (done)" : " (not yet)"}</span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
