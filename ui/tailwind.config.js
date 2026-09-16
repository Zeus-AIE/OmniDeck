/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        apple: {
          bg: "#0d0e12",
          card: "#161618",
          subcard: "#1f1f23",
          border: "#28282e",
          subtle: "#86868b",
          green: "#30D158",
          blue: "#0A84FF",
          red: "#FF453A",
          orange: "#FF9F0A",
          purple: "#BF5AF2",
          teal: "#64D2FF",
          yellow: "#FFD60A",
        }
      },
      fontFamily: {
        display: ['"Segoe UI Variable Display"', '"SF Pro Display"', '-apple-system', 'sans-serif'],
        text: ['"Segoe UI Variable Text"', '"SF Pro Text"', '-apple-system', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
