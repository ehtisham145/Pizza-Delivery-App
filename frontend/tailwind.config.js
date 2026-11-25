/** @type {import('tailwindcss').Config} */
// Neutral colours read CSS variables (see src/index.css) so light/dark mode
// switch automatically; brand colours are fixed.
const v = (name) => `rgb(var(--${name}) / <alpha-value>)`;

export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#FEF2F2",
          100: "#FDE3E3",
          200: "#FBC9CB",
          400: "#EF5A64",
          500: "#E63946",
          600: "#D92B2B",
          700: "#B91F24",
          800: "#961C20",
        },
        amber: {
          50: "#FFF8E6",
          100: "#FFEFC2",
          300: "#FFD166",
          400: "#FFB703",
          500: "#F4A261",
          700: "#9A6400",
        },
        canvas: v("canvas"),
        surface: v("surface"),
        "surface-2": v("surface-2"),
        line: v("line"),
        ink: v("ink"),
        muted: v("muted"),
        "brand-soft": v("brand-soft"),
        "brand-ink": v("brand-ink"),
      },
      fontFamily: {
        display: ['"Plus Jakarta Sans"', "Inter", "system-ui", "sans-serif"],
        sans: ["Inter", "system-ui", "-apple-system", '"Segoe UI"', "Roboto", "sans-serif"],
      },
      boxShadow: {
        soft: "0 1px 2px rgb(16 24 40 / 0.04), 0 2px 8px rgb(16 24 40 / 0.05)",
        lift: "0 4px 12px rgb(16 24 40 / 0.08), 0 16px 32px rgb(16 24 40 / 0.08)",
        pop: "0 24px 64px rgb(16 24 40 / 0.22)",
        brand: "0 6px 20px rgb(217 43 43 / 0.32)",
      },
      borderRadius: {
        "4xl": "2rem",
      },
      keyframes: {
        shimmer: { "100%": { transform: "translateX(100%)" } },
        blink: { "50%": { opacity: "0" } },
        bump: { "0%,100%": { transform: "scale(1)" }, "40%": { transform: "scale(1.25)" } },
      },
      animation: {
        shimmer: "shimmer 1.4s infinite",
        blink: "blink 1s step-end infinite",
        bump: "bump 0.35s ease-out",
      },
    },
  },
  plugins: [],
};
