/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {},
  },
  plugins: [],
  safelist: [
    "bg-blue-600",
    "hover:bg-blue-700",
    "cursor-pointer",
    "bg-gray-300",
    "cursor-not-allowed",
  ],
};
