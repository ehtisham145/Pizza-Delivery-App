import { motion } from "framer-motion";
import { Eye, EyeOff, ShieldCheck, Truck, Wallet } from "lucide-react";
import { BRAND_NAME } from "../../constants";
import Logo from "../Logo";
import Typewriter from "./Typewriter";

const PHRASES = ["Hot & fresh in 30 mins…", "Wood-fired perfection…", "Crafted with real mozzarella…", "Your favourites, one tap away…"];

const TRUST = [
  { icon: Truck, text: "Live order status updates" },
  { icon: Wallet, text: "Pay by card or cash on delivery" },
  { icon: ShieldCheck, text: "Secure, token-based sign-in" },
];

export function PasswordToggle({ shown, onToggle }) {
  return (
    <button
      type="button"
      onClick={onToggle}
      className="grid h-10 w-10 place-items-center rounded-lg text-muted transition hover:bg-surface-2 hover:text-ink"
      aria-label={shown ? "Hide password" : "Show password"}
      aria-pressed={shown}
    >
      {shown ? <EyeOff className="h-[18px] w-[18px]" /> : <Eye className="h-[18px] w-[18px]" />}
    </button>
  );
}

export default function AuthLayout({ image, title, subtitle, children }) {
  return (
    <div className="min-h-screen bg-surface lg:grid lg:grid-cols-2">
      {/* Visual side (top band on mobile) */}
      <div className="relative h-56 overflow-hidden bg-gray-900 sm:h-64 lg:sticky lg:top-0 lg:h-screen">
        <motion.img
          src={image}
          alt=""
          initial={{ scale: 1.08, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 1.2, ease: "easeOut" }}
          className="absolute inset-0 h-full w-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/45 to-black/25" aria-hidden="true" />
        <div className="relative flex h-full flex-col justify-between p-6 sm:p-8 lg:p-12">
          <Logo light />
          <div className="pb-6 lg:pb-0">
            <p className="hidden text-sm font-semibold uppercase tracking-[0.2em] text-amber-300 lg:block">{BRAND_NAME}</p>
            <h2 className="mt-2 font-display text-2xl font-extrabold leading-tight text-white sm:text-3xl lg:text-5xl">
              Pizza night,
              <br className="hidden lg:block" /> sorted.
            </h2>
            <p className="mt-2 min-h-[1.75em] font-display text-lg font-bold text-amber-300 sm:text-xl lg:mt-4 lg:text-2xl">
              <Typewriter phrases={PHRASES} />
            </p>
            <ul className="mt-8 hidden space-y-3 lg:block">
              {TRUST.map(({ icon: Icon, text }) => (
                <li key={text} className="flex items-center gap-3 text-white/85">
                  <span className="grid h-9 w-9 place-items-center rounded-full bg-white/10 backdrop-blur">
                    <Icon className="h-[18px] w-[18px] text-amber-300" aria-hidden="true" />
                  </span>
                  {text}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Form side */}
      <div className="relative -mt-6 rounded-t-3xl bg-surface lg:mt-0 lg:flex lg:items-center lg:justify-center lg:rounded-none">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: "easeOut", delay: 0.1 }}
          className="mx-auto w-full max-w-md px-6 py-10 sm:px-8 lg:py-16"
        >
          <h1 className="text-[1.9rem] font-extrabold">{title}</h1>
          {subtitle && <p className="mt-1.5 text-muted">{subtitle}</p>}
          <div className="mt-8">{children}</div>
        </motion.div>
      </div>
    </div>
  );
}
