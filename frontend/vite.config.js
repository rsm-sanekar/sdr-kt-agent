import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/tutor': 'http://localhost:8000',
      '/preboarding': 'http://localhost:8000',
      '/offboarding': 'http://localhost:8000',
      '/coaching': 'http://localhost:8000',
      '/dashboard': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
    },
  },
})
