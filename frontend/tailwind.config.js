/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class", // enable class-based dark mode toggle
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx,html}"
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#e3f2fd",
          100: "#bbdefb",
          200: "#90caf9",
          300: "#64b5f6",
          400: "#42a5f5",
          500: "#2196f3",
          600: "#2563eb", // primary main
          700: "#1d4ed8",
          800: "#1e293b", // secondary base
          900: "#0d47a1"
        },
        secondary: {
          600: "#1e293b"
        }
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui"]
      },
      backdropBlur: {
        xs: "2px",
        sm: "4px",
        md: "8px"
      },
      boxShadow: {
        glass: "0 4px 30px rgba(0,0,0,0.1)"
      }
    }
  },
  plugins: [require("@tailwindcss/forms"), require("@tailwindcss/aspect-ratio")]
};

