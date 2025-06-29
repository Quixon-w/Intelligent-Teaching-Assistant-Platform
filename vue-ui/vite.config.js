import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
    open: true,
    proxy: {
      '/api': {
        target: 'http://192.168.240.226:8080',
        changeOrigin: true,
      },
      '/ai': {
        target: 'http://192.168.240.200:9001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/ai/, ''),
      }
    },
  },
})
