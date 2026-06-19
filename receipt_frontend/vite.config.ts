import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1', // Forces the server to use IPv4
    port: 5173,
    hmr: {
      host: '127.0.0.1', // Explicitly tells the WebSocket where to bind
      protocol: 'ws',
    },
  }
})