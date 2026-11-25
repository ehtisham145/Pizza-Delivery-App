import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

// In development, /api/* is proxied to the FastAPI backend and the /api
// prefix is stripped — the same thing nginx does in Docker.
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const target = env.VITE_DEV_API_TARGET || "http://127.0.0.1:8002";

  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: {
        "/api": {
          target,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ""),
        },
      },
    },
  };
});
