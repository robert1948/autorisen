import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import tsconfigPaths from 'vite-tsconfig-paths';
import { fileURLToPath, URL } from 'node:url';
import { cacheBusterPlugin } from './vite.plugins.cachebuster.js'; // 👈 Import as named export

export default ({ mode }) => {
  // Load env variables (VITE_API_BASE from .env or shell)
  const env = loadEnv(mode, process.cwd(), '');
  // Prefer VITE_API_BASE from env files or the shell-provided VITE_API_BASE when running via CLI
  const apiBase = env.VITE_API_BASE || 'http://localhost:8000';

  return defineConfig({
    plugins: [
      react(),
      tsconfigPaths(),
      cacheBusterPlugin(), // 👈 Use the plugin as a function
    ],
    base: '/', // ✅ Required for production
    resolve: {
      extensions: ['.js', '.jsx', '.ts', '.tsx', '.json'],
      alias: {
        "@": fileURLToPath(new URL('./src', import.meta.url)),
        "@components": fileURLToPath(new URL('./src/components', import.meta.url)),
        "@pages": fileURLToPath(new URL('./src/pages', import.meta.url)),
        "@assets": fileURLToPath(new URL('./src/assets', import.meta.url)),
        "@ui": fileURLToPath(new URL('./src/components/ui', import.meta.url)),
      },
    },
    server: {
      port: 3000,
      host: '0.0.0.0', // Allow external connections
      proxy: {
        '/api': {
          target: apiBase,
          changeOrigin: true,
          // Preserve the /api prefix
        },
      },
    },
  });
};
