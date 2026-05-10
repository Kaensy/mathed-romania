/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // MathEd brand colors — adjust as design evolves
        primary: {
          50: "#eff6ff",
          100: "#dbeafe",
          200: "#bfdbfe",
          300: "#93c5fd",
          400: "#60a5fa",
          500: "#3b82f6",
          600: "#2563eb",
          700: "#1d4ed8",
          800: "#1e40af",
          900: "#1e3a8a",
          950: "#172554",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      keyframes: {
        "badge-toast-in": {
          "0%": { opacity: "0", transform: "translate(-50%, 24px)" },
          "100%": { opacity: "1", transform: "translate(-50%, 0)" },
        },
        "xp-toast-in": {
          "0%": { opacity: "0", transform: "scale(0.85)" },
          "60%": { opacity: "1", transform: "scale(1.06)" },
          "100%": { opacity: "1", transform: "scale(1)" },
        },
        "level-up-backdrop": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        "level-up-pop": {
          "0%": { opacity: "0", transform: "scale(0.4) translateY(40px)" },
          "55%": { opacity: "1", transform: "scale(1.15) translateY(-8px)" },
          "75%": { transform: "scale(0.95) translateY(0)" },
          "100%": { opacity: "1", transform: "scale(1) translateY(0)" },
        },
      },
      animation: {
        "badge-toast-in": "badge-toast-in 280ms cubic-bezier(0.22, 1, 0.36, 1)",
        "xp-toast-in": "xp-toast-in 320ms cubic-bezier(0.34, 1.56, 0.64, 1)",
        "level-up-backdrop": "level-up-backdrop 220ms ease-out",
        "level-up-pop": "level-up-pop 700ms cubic-bezier(0.34, 1.56, 0.64, 1)",
      },
    },
  },
  plugins: [],
};
