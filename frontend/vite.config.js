import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/auth': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
      '/locations': 'http://localhost:8080',
      '/services': 'http://localhost:8080',
      '/employees': 'http://localhost:8080',
      '/business-hours': 'http://localhost:8080',
      '/location-exceptions': 'http://localhost:8080',
      '/employee-absences': 'http://localhost:8080',
      '/car-brands': 'http://localhost:8080',
      '/cars': 'http://localhost:8080',
      '/bookings': 'http://localhost:8080',
      '/reviews': 'http://localhost:8080',
    },
  },
})