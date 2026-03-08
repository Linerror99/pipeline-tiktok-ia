import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api/v3': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
      '/ws/v3': {
        target: 'ws://localhost:8080',
        ws: true,
      },
    },
  },
})
