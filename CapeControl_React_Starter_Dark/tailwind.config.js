
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html','./src/**/*.{ts,tsx,js,jsx}'],
  theme: {
    extend: {
      colors: {
        bg: 'var(--cc-bg)',
        surface: 'var(--cc-surface)',
        border: 'var(--cc-border)',
        text: { DEFAULT: 'var(--cc-text)', muted: 'var(--cc-text-muted)' },
        accent: {
          frontend: 'var(--cc-accent-frontend)',
          backend: 'var(--cc-accent-backend)',
          agents: 'var(--cc-accent-agents)',
          data: 'var(--cc-accent-data)',
          infra: 'var(--cc-accent-infra)',
          integrations: 'var(--cc-accent-integrations)',
          ops: 'var(--cc-accent-ops)',
        }
      }
    }
  },
  plugins: []
}
