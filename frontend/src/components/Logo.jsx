import { Pizza } from "lucide-react";
import { BRAND_NAME } from "../constants";

// Two-line wordmark so a long brand name fits the sidebar:
// first word large, the rest as a small caps line underneath.
const [FIRST, ...REST] = BRAND_NAME.split(" ");
const SECOND = REST.join(" ");

export default function Logo({ compact = false, light = false, className = "" }) {
  return (
    <span className={`inline-flex items-center gap-2.5 ${className}`} aria-label={BRAND_NAME}>
      <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 text-white shadow-brand">
        <Pizza className="h-5 w-5" strokeWidth={2.4} aria-hidden="true" />
      </span>
      {!compact && (
        <span className="flex flex-col leading-none" aria-hidden="true">
          <span className={`font-display text-lg font-extrabold tracking-tight ${light ? "text-white" : "text-ink"}`}>
            {FIRST}
            {!SECOND && <span className="text-brand-500">.</span>}
          </span>
          {SECOND && (
            <span className={`mt-1 text-[0.62rem] font-bold uppercase tracking-[0.18em] ${light ? "text-amber-300" : "text-brand-ink"}`}>
              {SECOND}
            </span>
          )}
        </span>
      )}
    </span>
  );
}
