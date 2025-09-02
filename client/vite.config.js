import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tsconfigPaths from 'vite-tsconfig-paths';
import { fileURLToPath, URL } from 'node:url';
import { cacheBusterPlugin } from './vite.plugins.cachebuster.js'; // 👈 Import as named export

export default defineConfig({
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
        // Use the VITE_API_URL environment variable when available. Inside the
        // frontend Docker container this should point to the backend service
        // (e.g. http://backend:8000). Fallback to http://backend:8000 for
        // containerized dev environments.
        target: process.env.VITE_API_URL || 'http://backend:8000',
        changeOrigin: true,
      },
    },
  },
});
