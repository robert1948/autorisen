/// <reference types="node" />
import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const apiBase = (env.VITE_API_BASE || "").trim(); // empty => unset
  const useProxy = mode === "development" && apiBase.length === 0;

  return {
    plugins: [react()],
    server: {
      host: true, // allow LAN / Codespaces access
      port: 3000,
      strictPort: true,
      proxy: useProxy
        ? {
            "/api": {
              target: "http://localhost:8000",
              changeOrigin: true,
              ws: true, // proxy websockets too
              // path is preserved; add rewrite if your backend path differs
              // rewrite: (p) => p,
            },
          }
        : undefined,
    },
    // If you ever serve under a subpath in prod, set base here.
    // base: "/",
    preview: {
      port: 4173,
      strictPort: true,
    },
  };
});
