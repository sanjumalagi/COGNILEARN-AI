import path from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const currentDir = path.dirname(fileURLToPath(import.meta.url));

// Reference: 01_Project_Foundation/05_Technology_Stack.md (Section 3 - Frontend Technology Stack)
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(currentDir, "./src"),
    },
  },
  server: {
    port: 5173,
    proxy: {
      // Forwards frontend API calls to the FastAPI backend during local
      // development, avoiding CORS friction. Overridden in production
      // via VITE_API_BASE_URL.
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
