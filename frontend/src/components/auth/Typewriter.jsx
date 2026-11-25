import { useEffect, useState } from "react";
import { useReducedMotion } from "framer-motion";

/** Types, pauses, deletes and moves to the next phrase. Static if the user prefers reduced motion. */
export default function Typewriter({ phrases, typeMs = 65, deleteMs = 32, holdMs = 1700, className = "" }) {
  const reduce = useReducedMotion();
  const [index, setIndex] = useState(0);
  const [text, setText] = useState("");
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    if (reduce) return undefined;
    const full = phrases[index % phrases.length];
    let delay = deleting ? deleteMs : typeMs;
    if (!deleting && text === full) delay = holdMs;
    if (deleting && text === "") delay = 300;

    const t = window.setTimeout(() => {
      if (!deleting && text === full) setDeleting(true);
      else if (deleting && text === "") {
        setDeleting(false);
        setIndex((i) => (i + 1) % phrases.length);
      } else setText(full.slice(0, text.length + (deleting ? -1 : 1)));
    }, delay);
    return () => window.clearTimeout(t);
  }, [text, deleting, index, phrases, typeMs, deleteMs, holdMs, reduce]);

  if (reduce) return <span className={className}>{phrases[0]}</span>;

  return (
    <span className={className}>
      <span className="sr-only">{phrases.join(" ")}</span>
      <span aria-hidden="true">
        {text}
        <span className="ml-0.5 inline-block h-[0.9em] w-[3px] translate-y-[0.1em] animate-blink rounded-full bg-current" />
      </span>
    </span>
  );
}
