# Pizza Delivery App: UI/UX Audit and Redesign Record

Audit date: 2026-11-25 · Scope: `frontend/` (Vite + React 18, React Router 6)

This file records what was wrong with the frontend before the redesign, what changed, and what is still limited by the backend.

---

## 0. Stack facts that shaped the plan

| Assumed | Actual | Consequence |
|---|---|---|
| Next.js | **Vite + React 18 SPA** with React Router | Kept Vite. No SSR/`next/image`; images are optimised through Unsplash URL params and `srcSet`. |
| Tailwind CSS | **One hand-written `index.css` (351 lines)** with no utility framework | Added Tailwind 3. Shared class names (`.btn`, `.card`, `.table`…) are re-implemented with `@apply`, so the 6 admin screens get the new design without being rewritten. |
| Framer Motion | Not installed | Added `framer-motion` and `lucide-react` (icons). |

---

## 1. Visual and colour palette flaws

1. **Off-brand, low-energy primary colour.** `--primary: #d9480f` is burnt orange on a beige `#faf7f2` background. It reads as "rustic café", not "fast, hot delivery", and it looks too much like the warning colour (`--warn: #b35c00`). Status and brand colours compete.
2. **Muddy neutrals.** Surface, border and muted text are all warm beige-browns (`#f3eee6`, `#e7dfd3`, `#7a6f66`). Cards don't separate from the page, and the UI looks washed out.
3. **Contrast risks.** Muted text `#7a6f66` on `--surface-2` `#f3eee6` is about 4.3:1, below WCAG AA for the small 0.78–0.82rem text it is used for (hints, timestamps).
4. **No type pairing or scale.** Everything uses one font stack. `Inter` was named but **never loaded**, so most users got the system font. Headings run 1.6 → 1.15 → 1rem with almost no difference between h2 and h3, which gives page titles no weight.
5. **Inconsistent radii and spacing.** Radii of 4, 6, 8, 9, 12, 16 and 99px are mixed. Padding values such as `0.55rem 0.7rem`, `0.35rem 0.8rem` and `0.9rem 1rem 1rem` are ad hoc instead of following a scale.
6. **Emoji as iconography.** 🍕 🔔 🛒 🗑 ☰ are used as UI icons. They render differently on each OS, can't be themed, and look unprofessional at small sizes.

## 2. Layout and navigation loopholes

1. **Header overload.** The top bar holds the brand, **6 customer links, up to 6 admin/staff links**, the bell, a user chip and a logout button. That is 15+ targets in one row. On desktop it scrolls horizontally (`overflow-x: auto`). Below 1000px it collapses into an unstyled dropdown.
2. **No information hierarchy.** "Payments" (a rarely used history page) has the same weight as "Menu" (the main task). Customer and admin links sit side by side, separated only by a thin border.
3. **The cart is a separate page.** Every add-to-cart is followed by a green banner and a manual "Go to cart →". There is no persistent cart count anywhere in the app.
4. **Loading states.** Every page shows a text spinner ("Loading…"), which causes layout shift when content arrives. There are no skeletons.
5. **Clunky add-to-cart.** Each card has a native `<select>` for size and a raw `<input type="number">` for quantity. That makes 2 form controls × N cards, they are hard to tap on mobile, and you can't see the price difference between sizes before choosing.
6. **Menu search is page-local.** There is no global search, and a "No pizzas found" result gives no way to recover.
7. **Mobile.** On narrow screens the cart rows put 5 columns into 375px. Modals are centred boxes instead of bottom sheets. Some tap targets are 32px.
8. **Orders.** A flat accordion list. There is no "active order" view and no progress indicator, so the customer can't tell where the order is.
9. **Destructive confirms** use `window.confirm` (kept, because changing them would alter behaviour, but noted).

## 3. Authentication and onboarding UX

1. **Plain, centred card on a tinted background.** No brand imagery, no value proposition, nothing appetising. It looks like an admin login.
2. **No trust signals.** Nothing tells the user what they get (fast delivery, live updates, payment choice) or that the login is secure.
3. **Login has no show/hide password toggle.** Register has one, but as a text button.
4. **Account activation was a surprise.** New accounts had to be activated by an admin, and this was only stated *after* sign-up. *Update: activation was removed. New accounts can log in immediately, and admins can still deactivate users.*
5. **Register validation is good** (live rules, server-error mapping, focus on the first invalid field). It was kept as-is and restyled.

## 4. Missing essential food-delivery features

| Feature | Before | After |
|---|---|---|
| Sticky cart and slide-over drawer | ❌ | ✅ Cart button in top bar with live count, and a slide-over drawer with quantity steppers |
| Size and quantity customisation modal | ❌ (inline selects) | ✅ Visual size cards with per-size price, quantity stepper and live total |
| Dietary badges (Veg / Spicy / Top rated) | ❌ | ✅ Veg and Spicy are derived from category and name. Top rated comes from real review averages |
| Rating on cards | ❌ (reviews hidden behind a link) | ✅ Average and count from the public reviews endpoint |
| Category filter with imagery | Text chips | ✅ Thumbnail pills that scroll horizontally |
| Global search | ❌ | ✅ Top-bar search synced to the URL (`/menu?q=`) |
| Favourites | ❌ | ✅ Heart toggle saved per user in `localStorage`, plus a `/favorites` page |
| Delivery location selector | ❌ | ✅ Top-bar picker, backed by the existing addresses API (set default) |
| Order tracking UI | ❌ | ✅ Step tracker per order, plus Active / Delivered / Cancelled filters (`/orders?filter=active`) |
| Skeleton loaders | ❌ | ✅ Menu grid, cart drawer and lists |
| Empty states with a next step | Partial | ✅ Illustrated, with a CTA |
| Social login | ❌ | UI only, shown **disabled with "coming soon"**, because the backend has no OAuth |

---

## 5. Constraints from the backend (not faked)

* **Toppings and crust:** `AddToCartSchema.topping_ids` is a single int that the cart route **ignores**, and cart items don't store toppings. A toppings picker would show prices the order never charges, so the modal offers only size and quantity. Wiring toppings needs a backend change (list of IDs, `Cart_Item_Topping` rows, price included in `unit_price`).
* **Order statuses** are only `Pending`, `Delivered` and `Cancelled`. The tracker shows *Placed → Preparing & on the way → Delivered* and does not invent finer-grained states.
* **Prep/delivery time** isn't in the data model. Cards show one configurable estimate, `ESTIMATED_DELIVERY` in `src/constants.js`.
* **Offers/Promotions** have no backend, so they were left out of the sidebar rather than added as a dead link.
* **Pizza images:** seeds stored relative paths (`uploads/pizzas/*.jpg`) that nothing serves, so every card image was broken. The frontend now falls back to a curated Unsplash map (`src/lib/images.js`), and the seed file now writes those URLs for new databases.

## 6. Design system (Phase 2)

| Token | Light | Dark | Use |
|---|---|---|---|
| `brand-600` | `#D92B2B` | same | Primary CTAs (white text contrast 4.9:1, AA) |
| `brand-500` | `#E63946` | same | Accents, active indicators, badges |
| `amber` | `#FFB703` / `#F4A261` | same | Ratings, highlights |
| `canvas` | `#FAFAFA` | `#121212` | Page background |
| `surface` | `#FFFFFF` | `#1C1C1F` | Cards |
| `line` | `#E5E7EB` | `#2E2E33` | Borders |
| `ink` | `#1F2937` | `#F3F4F6` | Body text |
| `muted` | `#6B7280` | `#9CA3AF` | Secondary text (4.8:1 on white) |

* Type: **Plus Jakarta Sans** (display, 700–800) and **Inter** (UI, 400–600), loaded from Google Fonts.
* Radius: `rounded-xl` (12px) for controls, `rounded-2xl` (16px) for cards, `rounded-3xl` for hero and modals, full for pills.
* Elevation: `shadow-soft` (resting cards), `shadow-lift` (hover), `shadow-pop` (drawers and modals).
* Motion: 150–250ms ease-out. Card stagger is 40ms per item. All motion is reduced under `prefers-reduced-motion`.
