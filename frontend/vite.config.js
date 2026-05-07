import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/generate_agent': 'http://backend:8000',
      '/agents': 'http://backend:8000',
      '/config': 'http://backend:8000',
    }
  }
})
