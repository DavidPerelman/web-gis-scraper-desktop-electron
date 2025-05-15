import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  base: "./",
  server: {
    proxy: {
      "/health": "http://127.0.0.1:8000", // או הפורט שבחרת
    },
  },
  plugins: [react()],
});
