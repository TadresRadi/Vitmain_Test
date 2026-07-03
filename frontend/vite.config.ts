import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes("node_modules")) return undefined
          if (id.includes("react") || id.includes("react-dom") || id.includes("react-router-dom")) {
            return "react-vendor"
          }
          if (id.includes("@radix-ui")) {
            return "radix-ui"
          }
          if (id.includes("framer-motion")) {
            return "motion"
          }
          if (id.includes("recharts")) {
            return "charts"
          }
          if (id.includes("axios") || id.includes("@tanstack/react-query") || id.includes("zustand")) {
            return "client-state"
          }
          if (id.includes("i18next") || id.includes("react-i18next")) {
            return "i18n"
          }
          return "vendor"
        },
      },
    },
  },
})
