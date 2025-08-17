import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tsconfigPaths from 'vite-tsconfig-paths';
import path from 'path';
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
      "@": path.resolve(__dirname, "./src"),
      "@components": path.resolve(__dirname, "./src/components"),
      "@pages": path.resolve(__dirname, "./src/pages"),
      "@assets": path.resolve(__dirname, "./src/assets"),
      "@ui": path.resolve(__dirname, "./src/components/ui"),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        // Remove the rewrite to preserve the /api prefix
      },
    },
  },
});
