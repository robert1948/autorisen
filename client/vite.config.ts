/// <reference types="node" />
import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import { readFileSync } from "fs";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const packageJson = JSON.parse(readFileSync(join(__dirname, 'package.json'), 'utf8'));

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const apiBase = (env.VITE_API_BASE || "").trim(); // empty => unset
  const useProxy = mode === "development" && apiBase.length === 0;
  const appVersion = (env.VITE_APP_VERSION || "").trim() || packageJson.version;

  return {
    plugins: [react()],
    define: {
      __APP_VERSION__: JSON.stringify(appVersion),
    },
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
    build: {
      // Ensure proper cache busting with content hashes
      rollupOptions: {
        output: {
          // Add timestamp to asset names for better cache busting
          assetFileNames: (assetInfo) => {
            const info = assetInfo.name?.split('.') || [];
            let extType = info[info.length - 1];
            if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(extType)) {
              extType = 'img';
            } else if (/woff2?|eot|ttf|otf/i.test(extType)) {
              extType = 'fonts';
            }
            return `assets/${extType}/[name]-[hash][extname]`;
          },
          chunkFileNames: 'assets/js/[name]-[hash].js',
          entryFileNames: 'assets/js/[name]-[hash].js',
        },
      },
      // Generate manifest for additional cache control and build fingerprinting
      manifest: true,
      // Optimize output size
      target: 'esnext',
      minify: 'esbuild',
      // Source maps for production debugging
      sourcemap: mode === 'production' ? 'hidden' : true,
    },
    // If you ever serve under a subpath in prod, set base here.
    // base: "/",
    preview: {
      port: 4173,
      strictPort: true,
    },
  };
});
