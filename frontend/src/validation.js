// Client-side validation that mirrors backend/app/utils/validator.py, so users
// see problems while typing instead of after a round-trip to the server.

// Backend strips spaces, dashes and brackets, then expects 03xxxxxxxxx,
// 923xxxxxxxxx or +923xxxxxxxxx.
// Any country: optional "+" (or "00") then 7–15 digits (E.164 max).
// Spaces, dashes, dots and brackets are removed first — same as the backend.
export const normalizePhone = (v) => {
  const s = String(v || "").replace(/[\s\-.()]/g, "");
  return s.startsWith("00") ? `+${s.slice(2)}` : s;
};
const PHONE_RE = /^\+?\d{7,15}$/;

// Backend only accepts these characters in a password.
const PASSWORD_ALLOWED_RE = /^[A-Za-z\d@$!%*?&]*$/;
export const PASSWORD_SPECIALS = "@$!%*?&";

export const PASSWORD_RULES = [
  { key: "length", label: "At least 8 characters", test: (v) => v.length >= 8 },
  { key: "upper", label: "One uppercase letter (A–Z)", test: (v) => /[A-Z]/.test(v) },
  { key: "lower", label: "One lowercase letter (a–z)", test: (v) => /[a-z]/.test(v) },
  { key: "digit", label: "One number (0–9)", test: (v) => /\d/.test(v) },
  { key: "special", label: `One of these symbols: ${PASSWORD_SPECIALS}`, test: (v) => /[@$!%*?&]/.test(v) },
];

export function validateFullName(v) {
  const name = String(v || "").trim();
  if (!name) return "Enter your full name.";
  if (name.length < 5) return "Name must be at least 5 characters.";
  if (name.length > 20) return "Name can be at most 20 characters.";
  return "";
}

export function validateEmail(v) {
  const email = String(v || "").trim();
  if (!email) return "Enter your email address.";
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return "Enter a valid email, like name@example.com.";
  return "";
}

export function validatePhone(v) {
  const phone = normalizePhone(v);
  if (!phone) return "Enter your mobile number.";
  if (/[^\d+]/.test(phone) || phone.lastIndexOf("+") > 0) return "Use digits only, with an optional + at the start.";
  const digits = phone.replace("+", "").length;
  if (digits < 7) return "That number looks too short. Include the full number.";
  if (digits > 15) return "That number looks too long. Phone numbers have at most 15 digits.";
  if (!PHONE_RE.test(phone)) return "Enter a valid phone number, like +14155552671.";
  return "";
}

export function validatePassword(v) {
  const pw = String(v || "");
  if (!pw) return "Enter a password.";
  if (!PASSWORD_ALLOWED_RE.test(pw)) return `Only letters, numbers and ${PASSWORD_SPECIALS} are allowed.`;
  const missing = PASSWORD_RULES.filter((r) => !r.test(pw));
  if (missing.length) return "Password doesn't meet all the requirements below.";
  return "";
}

export function validateConfirm(pw, confirm) {
  if (!confirm) return "Re-enter your password.";
  if (pw !== confirm) return "Passwords don't match.";
  return "";
}

// Turn a FastAPI 422 response into { fieldName: "friendly message" }.
export function fieldErrorsFromApi(err) {
  const detail = err?.data?.detail;
  if (!Array.isArray(detail)) return {};
  const out = {};
  for (const d of detail) {
    const field = Array.isArray(d.loc) ? d.loc[d.loc.length - 1] : null;
    if (typeof field === "string" && !out[field]) {
      out[field] = String(d.msg || "").replace(/^Value error,\s*/i, "");
    }
  }
  return out;
}
